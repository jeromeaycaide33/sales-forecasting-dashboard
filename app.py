import html
import io
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pandas as pd
import plotly.express as px
import streamlit as st
import textwrap


# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Sales Forecasting Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# THEME STATE
# =========================================================
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"

# Landing page is shown first. The existing dashboard remains intact.
if "show_dashboard" not in st.session_state:
    st.session_state.show_dashboard = False


def open_dashboard():
    st.session_state.show_dashboard = True


def go_home():
    st.session_state.show_dashboard = False


def toggle_theme():
    st.session_state.theme_mode = (
        "light" if st.session_state.theme_mode == "dark" else "dark"
    )


DARK_THEME = {
    "name": "dark",
    "page": "#101820",
    "page_grad_1": "#121F29",
    "page_grad_2": "#0B1219",
    "sidebar": "#111D26",
    "hero": "#172B35",
    "hero2": "#1C3940",
    "panel": "#17242D",
    "panel_alt": "#1D3038",
    "panel_soft": "#192A32",
    "border": "#304A50",
    "tab_bg": "#17262E",
    "tab_active": "#24464A",
    "tab_text": "#C4D4D3",
    "tab_active_border": "#43C6A5",
    "text": "#F1F6F4",
    "muted": "#9EB4B1",
    "blue": "#31B89A",
    "blue_light": "#70DFC0",
    "teal": "#48C9B0",
    "gold": "#E7B967",
    "success_bg": "#173A34",
    "success_border": "#347A68",
    "success_text": "#D5F5E9",
    "table_header": "#20363C",
}

LIGHT_THEME = {
    "name": "light",
    "page": "#F2F5F2",
    "page_grad_1": "#F7F9F6",
    "page_grad_2": "#E9EFEB",
    "sidebar": "#E8EFEB",
    "hero": "#FFFFFF",
    "hero2": "#F0F7F3",
    "panel": "#FFFFFF",
    "panel_alt": "#F8FBF8",
    "panel_soft": "#EEF4F0",
    "border": "#D3E0D9",
    "tab_bg": "#FFFFFF",
    "tab_active": "#E2F2EB",
    "tab_text": "#405A50",
    "tab_active_border": "#42A98C",
    "text": "#233A32",
    "muted": "#71857C",
    "blue": "#218F75",
    "blue_light": "#43B99A",
    "teal": "#369E8A",
    "gold": "#C89A3D",
    "success_bg": "#E8F6EF",
    "success_border": "#B8DFCC",
    "success_text": "#315E4B",
    "table_header": "#EAF1EC",
}

theme = DARK_THEME if st.session_state.theme_mode == "dark" else LIGHT_THEME


# =========================================================
# CSS
# =========================================================
def build_css(t):
    return f"""
    <style>
    :root {{
        --page: {t["page"]};
        --page-grad-1: {t["page_grad_1"]};
        --page-grad-2: {t["page_grad_2"]};
        --sidebar: {t["sidebar"]};
        --hero: {t["hero"]};
        --hero2: {t["hero2"]};
        --panel: {t["panel"]};
        --panel-alt: {t["panel_alt"]};
        --panel-soft: {t["panel_soft"]};
        --border: {t["border"]};
        --tab-bg: {t["tab_bg"]};
        --tab-active: {t["tab_active"]};
        --tab-text: {t["tab_text"]};
        --tab-active-border: {t["tab_active_border"]};
        --text: {t["text"]};
        --muted: {t["muted"]};
        --blue: {t["blue"]};
        --blue-light: {t["blue_light"]};
        --teal: {t["teal"]};
        --gold: {t["gold"]};
        --success-bg: {t["success_bg"]};
        --success-border: {t["success_border"]};
        --success-text: {t["success_text"]};
        --table-header: {t["table_header"]};
    }}

    .stApp {{
        background: linear-gradient(180deg, var(--page-grad-1) 0%, var(--page-grad-2) 100%);
        color: var(--text);
    }}

    .block-container {{
        max-width: 1800px;
        padding-top: 4.1rem !important;
        padding-bottom: 2.5rem;
        padding-left: clamp(1rem, 2vw, 2rem);
        padding-right: clamp(1rem, 2vw, 2rem);
    }}

    section[data-testid="stMain"] .block-container {{
        padding-top: 4.1rem !important;
    }}

    div[data-testid="stHorizontalBlock"] {{
        gap: 0.9rem;
        align-items: stretch;
    }}

    div[data-testid="stTabs"] [data-baseweb="tab-panel"] {{
        padding-top: 1rem;
    }}

    h1, h2, h3, p, label {{
        color: var(--text);
    }}

    .stMarkdown, .stMarkdown p, .stMarkdown li {{
        color: var(--text);
    }}

    .stCaption, [data-testid="stCaptionContainer"] {{
        color: var(--muted) !important;
    }}

    h1 {{ font-size: 1.9rem !important; font-weight: 800 !important; }}
    h2 {{ font-size: 1.35rem !important; font-weight: 750 !important; }}
    h3 {{ font-size: 1.05rem !important; font-weight: 700 !important; }}

    .sf-hero {{
        background: linear-gradient(110deg, var(--hero) 0%, var(--hero2) 100%);
        border: 1px solid var(--border);
        border-radius: 13px;
        padding: 19px 24px;
        margin: 0.15rem 0 1.15rem 0;
    }}

    .sf-eyebrow {{
        color: var(--blue);
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        margin-bottom: 0.45rem;
    }}

    .sf-title {{
        color: var(--text);
        font-size: 1.85rem;
        font-weight: 800;
        line-height: 1.15;
        margin: 0;
    }}

    .sf-subtitle {{
        color: var(--muted);
        font-size: 0.84rem;
        line-height: 1.45;
        max-width: 900px;
        margin: 0.45rem 0 0 0;
    }}

    .sf-accent {{
        width: 62px;
        height: 3px;
        border-radius: 10px;
        background: var(--blue);
        margin-top: 0.8rem;
    }}

    .sf-panel-title {{
        color: var(--text);
        font-size: 0.91rem;
        font-weight: 750;
        line-height: 1.3;
        margin: 0 0 0.2rem 0;
    }}

    .sf-panel-subtitle {{
        color: var(--muted);
        font-size: 0.70rem;
        line-height: 1.4;
        margin: 0 0 0.65rem 0;
    }}

    .sf-metric-row {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 10px;
        padding: 0.68rem 0;
        border-bottom: 1px solid color-mix(in srgb, var(--border) 70%, transparent);
    }}

    .sf-metric-row:last-child {{
        border-bottom: 0;
    }}

    .sf-metric-label {{
        color: var(--muted);
        font-size: 0.76rem;
        line-height: 1.35;
    }}

    .sf-metric-value {{
        color: var(--text);
        font-size: 1.03rem;
        font-weight: 800;
        white-space: nowrap;
        text-align: right;
    }}

    .sf-metric-note {{
        color: var(--teal);
        font-size: 0.65rem;
        font-weight: 650;
        margin-top: 2px;
        text-align: right;
    }}

    .sf-recommendation {{
        background: var(--success-bg);
        border: 1px solid var(--success-border);
        border-left: 3px solid var(--blue);
        color: var(--success-text);
        border-radius: 8px;
        padding: 0.75rem 0.9rem;
        font-size: 0.78rem;
        line-height: 1.5;
        margin-top: 0.8rem;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: linear-gradient(150deg, var(--panel) 0%, var(--panel-soft) 100%);
        border: 1px solid var(--border) !important;
        border-radius: 11px !important;
        padding: 0.78rem 0.82rem 0.65rem 0.82rem;
        box-shadow: none;
    }}

    div[data-testid="stMetric"] {{
        background: var(--panel-alt);
        border: 1px solid var(--border) !important;
        border-radius: 9px !important;
        padding: 11px 13px;
        min-height: 88px;
        box-shadow: none;
    }}

    [data-testid="stMetricLabel"] {{
        color: var(--muted) !important;
        font-size: 0.75rem !important;
    }}

    [data-testid="stMetricValue"] {{
        color: var(--text) !important;
        font-weight: 800 !important;
        font-size: 1.35rem !important;
    }}

    div[data-testid="stPlotlyChart"] {{
        background: transparent !important;
        border: 0 !important;
        border-radius: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        overflow: hidden !important;
        box-shadow: none !important;
    }}

    div[data-testid="stDataFrame"],
    div[data-testid="stTable"],
    .stDataFrame {{
        border: 1px solid var(--border) !important;
        border-radius: 9px !important;
        overflow: hidden;
    }}

    div[data-testid="stDataFrame"] thead tr th {{
        background: var(--table-header) !important;
    }}

    div[data-testid="stAlert"],
    .stAlert,
    div[data-testid="stExpander"] {{
        border-radius: 9px !important;
    }}

    section[data-testid="stSidebar"] {{
        background: var(--sidebar);
        border-right: 1px solid var(--border);
        min-width: 270px;
    }}

    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {{
        color: var(--text) !important;
    }}

    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        background: var(--panel-soft) !important;
    }}

    div[data-testid="stTabs"] [role="tablist"] {{
        gap: 6px;
        border-bottom: 1px solid var(--border);
        padding-bottom: 6px;
    }}

    div[data-testid="stTabs"] button[role="tab"] {{
        background: var(--tab-bg);
        border: 1px solid var(--border);
        border-radius: 8px 8px 5px 5px;
        color: var(--tab-text);
        font-weight: 650;
        padding: 8px 12px;
        font-size: 0.82rem;
    }}

    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
        background: var(--tab-active);
        border: 1px solid var(--tab-active-border);
        color: var(--text);
        box-shadow: none;
    }}

    div[data-testid="stDownloadButton"] button,
    .stButton button,
    div[data-testid="stSidebar"] button {{
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        background: var(--panel-alt) !important;
        color: var(--text) !important;
    }}

    /* Theme control anchor under System Information */
    .theme-label {{
        color: var(--muted);
        font-size: 0.75rem;
        margin: 0.75rem 0 0.35rem 0;
    }}

    hr {{
        border-color: var(--border) !important;
    }}

    /* Motion polish: subtle entrance and hover movement, without changing widgets. */
    @keyframes sfFadeRise {{
        from {{ opacity: 0; transform: translateY(9px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}
    [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stMetric"],
    [data-testid="stPlotlyChart"] {{
        animation: sfFadeRise .55s ease both;
    }}
    [data-testid="stMetric"] {{
        transition: transform .22s ease, box-shadow .22s ease, border-color .22s ease;
    }}
    [data-testid="stMetric"]:hover {{
        transform: translateY(-4px);
        border-color: var(--blue) !important;
        box-shadow: 0 12px 28px rgba(0, 170, 190, .16) !important;
    }}
    [data-testid="stPlotlyChart"] {{
        transition: transform .22s ease, filter .22s ease;
    }}
    [data-testid="stPlotlyChart"]:hover {{
        filter: drop-shadow(0 8px 15px rgba(0, 160, 185, .10));
    }}
    @media (prefers-reduced-motion: reduce) {{
        [data-testid="stVerticalBlockBorderWrapper"],
        [data-testid="stMetric"],
        [data-testid="stPlotlyChart"] {{
            animation: none !important;
            transition: none !important;
        }}
    }}

    /* Refined dashboard styling */
    html, body, [class*="css"] {{
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}

    .stApp {{
        background-attachment: fixed;
    }}

    .block-container {{
        max-width: 1680px;
        padding-top: 2.25rem !important;
    }}

    .sf-hero {{
        border-radius: 18px;
        padding: 25px 28px;
        box-shadow: 0 12px 34px rgba(0, 0, 0, 0.10);
        position: relative;
        overflow: hidden;
    }}

    .sf-hero:after {{
        content: "";
        position: absolute;
        width: 210px;
        height: 210px;
        right: -72px;
        top: -105px;
        border-radius: 50%;
        border: 1px solid color-mix(in srgb, var(--blue) 35%, transparent);
        box-shadow: 0 0 0 22px color-mix(in srgb, var(--blue) 6%, transparent),
                    0 0 0 46px color-mix(in srgb, var(--blue) 4%, transparent);
        pointer-events: none;
    }}

    .sf-title {{
        font-size: clamp(1.65rem, 2.5vw, 2.2rem);
        letter-spacing: -0.035em;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        border-radius: 15px !important;
        padding: 1rem 1rem 0.85rem 1rem;
        box-shadow: 0 5px 18px rgba(0, 0, 0, 0.055);
        transition: border-color 160ms ease, transform 160ms ease;
    }}

    div[data-testid="stMetric"] {{
        border-radius: 14px !important;
        padding: 15px 16px;
        min-height: 108px;
        box-shadow: 0 5px 16px rgba(0, 0, 0, 0.045);
    }}

    [data-testid="stMetricLabel"] p {{
        color: var(--muted) !important;
        font-size: 0.78rem !important;
        font-weight: 650 !important;
    }}

    [data-testid="stMetricValue"] {{
        font-size: clamp(1.25rem, 2vw, 1.75rem) !important;
        letter-spacing: -0.025em;
    }}

    /* Larger, clearer text-only navigation tabs */
    div[data-testid="stTabs"] [role="tablist"] {{
        display: flex;
        align-items: stretch;
        gap: 10px;
        border-bottom: 1px solid var(--border);
        padding: 0 0 10px 0;
    }}

    div[data-testid="stTabs"] button[role="tab"] {{
        min-height: 56px !important;
        padding: 14px 23px !important;
        border: 1px solid var(--border) !important;
        border-radius: 11px 11px 8px 8px !important;
        background: var(--tab-bg) !important;
        color: var(--tab-text) !important;
        white-space: nowrap !important;
        transition: background 150ms ease, border-color 150ms ease, color 150ms ease;
    }}

    div[data-testid="stTabs"] button[role="tab"] p {{
        margin: 0 !important;
        font-size: 1rem !important;
        line-height: 1.25 !important;
        font-weight: 750 !important;
    }}

    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
        background: var(--tab-active) !important;
        color: var(--text) !important;
        border-color: var(--tab-active-border) !important;
        border-bottom: 3px solid var(--blue) !important;
    }}

    div[data-testid="stTabs"] button[role="tab"]:hover {{
        background: var(--tab-active) !important;
        border-color: var(--blue) !important;
        color: var(--text) !important;
    }}

    .stButton button, div[data-testid="stDownloadButton"] button,
    section[data-testid="stSidebar"] button {{
        min-height: 42px;
        font-weight: 650;
        transition: transform 150ms ease, border-color 150ms ease, filter 150ms ease;
    }}

    .stButton button:hover, div[data-testid="stDownloadButton"] button:hover,
    section[data-testid="stSidebar"] button:hover {{
        border-color: var(--blue) !important;
        filter: brightness(1.04);
        transform: translateY(-1px);
    }}

    section[data-testid="stSidebar"] {{
        padding-top: 0.75rem;
    }}
    section[data-testid="stSidebar"] [data-testid="stExpander"] {{
        border: 1px solid var(--border) !important;
        border-radius: 15px !important;
        background: color-mix(in srgb, var(--panel) 72%, transparent) !important;
        backdrop-filter: blur(18px) saturate(140%) !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stExpander"] summary {{
        color: var(--text) !important;
        font-weight: 750 !important;
    }}
    [data-testid="stColorPicker"] {{
        border: 1px solid color-mix(in srgb, var(--border) 65%, transparent);
        border-radius: 10px;
        padding: 5px 7px;
        background: color-mix(in srgb, var(--panel-soft) 70%, transparent);
    }}
    [data-testid="stColorPicker"] label {{
        font-size: .72rem !important;
        color: var(--muted) !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
        gap: 0.75rem;
    }}

    div[data-testid="stDataFrame"], div[data-testid="stTable"] {{
        border-radius: 12px !important;
    }}

    div[data-testid="stAlert"] {{
        border-radius: 12px !important;
    }}

    @media (max-width: 768px) {{
        .block-container {{
            padding-top: 1.25rem !important;
            padding-left: 0.85rem;
            padding-right: 0.85rem;
        }}
        .sf-hero {{
            padding: 20px 18px;
        }}
        .sf-subtitle {{
            font-size: 0.8rem;
        }}
        div[data-testid="stTabs"] [role="tablist"] {{
            overflow-x: auto;
            flex-wrap: nowrap;
        }}
        div[data-testid="stTabs"] button[role="tab"] {{
            min-height: 50px !important;
            padding: 12px 17px !important;
            white-space: nowrap !important;
        }}
        div[data-testid="stTabs"] button[role="tab"] p {{
            font-size: 0.92rem !important;
        }}
    }}

    @media (max-width: 1100px) {{
        .sf-title {{ font-size: 1.55rem; }}
        .block-container {{
            padding-left: 1rem;
            padding-right: 1rem;
        }}
    }}
    </style>
    """


st.markdown(build_css(theme), unsafe_allow_html=True)

# Landing-page-only visual styling.
if not st.session_state.show_dashboard:
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] {display: none !important;}
        .block-container {max-width: 1440px !important; padding-top: 1.65rem !important;}
        .sf-landing-wrap {max-width: 1380px; margin: 0 auto;}
        .sf-brand {color:var(--blue-light); font-size:.72rem; font-weight:850;
            letter-spacing:.19em; text-transform:uppercase;}
        .sf-top-note {color:var(--muted);font-size:.72rem;letter-spacing:.08em;}
        .sf-landing-hero {
            position:relative; overflow:hidden; display:grid;
            grid-template-columns:1.08fr .92fr; gap:clamp(24px,4vw,58px);
            align-items:center; padding:clamp(28px,5vw,66px);
            border-radius:24px; border:1px solid var(--border);
            background:radial-gradient(circle at 90% 8%,color-mix(in srgb,var(--blue) 24%,transparent),transparent 32%),
                       linear-gradient(120deg,var(--hero) 0%,var(--hero2) 58%,var(--panel) 100%);
            box-shadow:0 22px 60px rgba(0,0,0,.28);
        }
        .sf-landing-hero:before {content:"";position:absolute;width:390px;height:390px;
            right:-185px;top:-235px;border:1px solid color-mix(in srgb,var(--blue-light) 38%,transparent);
            border-radius:50%;box-shadow:0 0 0 28px rgba(57,139,255,.055),
            0 0 0 62px rgba(57,139,255,.035);pointer-events:none;}
        .sf-landing-copy-wrap {position:relative;z-index:1;}
        .sf-landing-kicker {display:inline-flex;align-items:center;gap:8px;
            color:var(--blue-light);font-size:.7rem;font-weight:850;letter-spacing:.19em;
            text-transform:uppercase;margin-bottom:1.15rem;}
        .sf-kicker-dot {width:7px;height:7px;border-radius:50%;background:var(--blue);
            box-shadow:0 0 14px var(--blue);display:inline-block;}
        .sf-landing-title {color:var(--text);font-size:clamp(2.25rem,4.7vw,4.35rem);
            line-height:1.035;letter-spacing:-.052em;font-weight:880;
            margin:0;max-width:720px;}
        .sf-landing-title span {color:var(--blue-light);}
        .sf-landing-copy {color:var(--muted);font-size:1rem;line-height:1.8;
            max-width:650px;margin:1.25rem 0 1.45rem 0;}
        .sf-landing-points {display:flex;gap:10px 18px;flex-wrap:wrap;
            color:var(--text);font-size:.76rem;}
        .sf-landing-points span:before {content:"✓";color:var(--teal);font-weight:900;margin-right:7px;}
        .sf-preview-card {position:relative;z-index:1;padding:22px;border-radius:19px;
            border:1px solid color-mix(in srgb,var(--border) 85%,transparent);
            background:linear-gradient(155deg,color-mix(in srgb,var(--panel-alt) 94%,transparent),color-mix(in srgb,var(--panel) 96%,transparent));
            box-shadow:0 18px 44px rgba(0,0,0,.20);backdrop-filter:blur(18px) saturate(145%);}
        .sf-preview-top {display:flex;justify-content:space-between;align-items:center;
            gap:10px;color:var(--muted);font-size:.66rem;font-weight:800;letter-spacing:.12em;}
        .sf-live-pill {padding:5px 9px;border-radius:20px;color:var(--teal);
            background:color-mix(in srgb,var(--teal) 15%,transparent);border:1px solid color-mix(in srgb,var(--teal) 45%,transparent);
            letter-spacing:.06em;font-size:.61rem;white-space:nowrap;}
        .sf-preview-heading {color:var(--text);font-size:1.25rem;font-weight:800;
            margin:18px 0 3px 0;}
        .sf-preview-sub {color:var(--muted);font-size:.72rem;}
        .sf-preview-kpis {display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin:20px 0 17px;}
        .sf-preview-kpi {padding:11px 10px;border:1px solid color-mix(in srgb,var(--border) 72%,transparent);
            border-radius:11px;background:color-mix(in srgb,var(--panel-soft) 78%,transparent);}
        .sf-preview-kpi-label {color:var(--muted);font-size:.61rem;line-height:1.4;}
        .sf-preview-kpi-value {color:var(--text);font-size:.92rem;font-weight:850;margin-top:5px;}
        .sf-chart-shell {border:1px solid color-mix(in srgb,var(--border) 72%,transparent);border-radius:13px;
            background:color-mix(in srgb,var(--panel) 76%,transparent);padding:13px 13px 10px;}
        .sf-chart-label {display:flex;justify-content:space-between;gap:8px;
            color:var(--muted);font-size:.64rem;font-weight:750;letter-spacing:.08em;}
        .sf-chart {height:112px;display:flex;align-items:flex-end;gap:7px;
            padding:12px 2px 0;border-bottom:1px solid color-mix(in srgb,var(--border) 75%,transparent);
            background:repeating-linear-gradient(to bottom,transparent 0,transparent 27px,color-mix(in srgb,var(--border) 20%,transparent) 28px);}
        .sf-chart span {flex:1;min-width:5px;border-radius:4px 4px 0 0;
            background:linear-gradient(180deg,var(--blue-light) 0%,var(--blue) 100%);
            box-shadow:0 0 13px color-mix(in srgb,var(--blue) 25%,transparent);opacity:.95;}
        .sf-chart-legend {display:flex;justify-content:space-between;color:var(--muted);
            font-size:.61rem;margin-top:9px;}
        .sf-model-tags {display:flex;flex-wrap:wrap;gap:6px;margin-top:15px;}
        .sf-model-tags span {font-size:.61rem;color:var(--text);padding:5px 8px;
            border:1px solid color-mix(in srgb,var(--border) 80%,transparent);border-radius:6px;background:color-mix(in srgb,var(--panel-soft) 76%,transparent);}
        .sf-section-heading {font-size:1.35rem;font-weight:850;color:var(--text);
            margin:2.25rem 0 .35rem 0;letter-spacing:-.02em;}
        .sf-section-copy {color:var(--muted);font-size:.87rem;margin-bottom:1rem;line-height:1.6;}
        .sf-feature {height:100%;min-height:165px;padding:21px;border-radius:15px;
            border:1px solid var(--border);background:linear-gradient(150deg,var(--panel),var(--panel-soft));
            box-shadow:0 7px 22px rgba(0,0,0,.09);}
        .sf-feature-icon {width:42px;height:42px;display:flex;align-items:center;justify-content:center;
            border-radius:12px;background:color-mix(in srgb,var(--blue) 14%,transparent);border:1px solid color-mix(in srgb,var(--blue) 35%,transparent);
            font-size:1.25rem;margin-bottom:14px;}
        .sf-feature-title {color:var(--text);font-weight:850;font-size:.98rem;margin-bottom:7px;}
        .sf-feature-copy {color:var(--muted);font-size:.79rem;line-height:1.65;}
        .sf-landing-cta-note {color:var(--muted);font-size:.76rem;line-height:1.6;padding-top:7px;}
        .sf-footer {text-align:center;color:var(--muted);font-size:.68rem;
            letter-spacing:.08em;padding:15px 0 8px;}
        div[data-testid="stButton"] button[kind="primary"] {
            background:linear-gradient(110deg,var(--blue),var(--blue-light)) !important;
            border:1px solid var(--blue-light) !important;color:white !important;
            box-shadow:0 8px 24px color-mix(in srgb,var(--blue) 24%,transparent) !important;}
        @media(max-width:850px) {
            .sf-landing-hero {grid-template-columns:1fr;padding:28px 22px;}
            .sf-preview-card {max-width:100%;}
            .sf-landing-title {font-size:clamp(2.15rem,9vw,3.2rem);}
        }
        @media(max-width:560px) {
            .sf-preview-kpis {grid-template-columns:1fr;}
            .sf-preview-kpi {display:flex;justify-content:space-between;align-items:center;}
            .sf-chart {height:90px;gap:4px;}
        }


    /* =====================================================
       MODERN ANALYTICS REDESIGN — MATTE SURFACES
       Presentation-only CSS. Forecasting logic and widgets
       remain unchanged.
       ===================================================== */
    .stApp {{
        background:
          linear-gradient(135deg, var(--page) 0%, var(--page-grad-1) 58%, var(--page-grad-2) 100%) !important;
        background-attachment: fixed !important;
    }}
    [data-testid="stAppViewContainer"] {{
        background: transparent !important;
    }}
    [data-testid="stHeader"] {{
        background: var(--page) !important;
        border-bottom: 1px solid var(--border);
    }}
    [data-testid="stSidebar"] > div:first-child {{
        background: var(--sidebar) !important;
        border-right: 1px solid var(--border) !important;
    }}
    [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stMetric"],
    [data-testid="stExpander"],
    [data-testid="stAlert"],
    .sf-hero, .sf-landing-hero, .sf-preview-card, .sf-feature {{
        background: var(--panel) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        box-shadow: 0 7px 20px rgba(0, 0, 0, .08) !important;
        backdrop-filter: none !important;
        -webkit-backdrop-filter: none !important;
    }}
    [data-testid="stVerticalBlockBorderWrapper"] {{
        border-top: 3px solid var(--blue) !important;
        transition: border-color .18s ease, transform .18s ease, box-shadow .18s ease;
    }}
    [data-testid="stVerticalBlockBorderWrapper"]:hover {{
        border-color: var(--blue) !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, .12) !important;
        transform: translateY(-1px);
    }}
    [data-testid="stMetric"] {{
        padding: 16px !important;
        border-left: 4px solid var(--blue) !important;
        border-radius: 10px !important;
        background: var(--panel-alt) !important;
    }}
    [data-testid="stTabs"] [role="tablist"] {{
        gap: 5px !important;
        padding: 0 0 8px 0 !important;
        border-bottom: 2px solid var(--border) !important;
        background: transparent !important;
    }}
    [data-testid="stTabs"] button[role="tab"] {{
        border: 0 !important;
        border-radius: 7px 7px 0 0 !important;
        background: transparent !important;
        color: var(--tab-text) !important;
        padding: 11px 15px !important;
        transition: all .18s ease;
    }}
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
        color: var(--text) !important;
        background: var(--tab-active) !important;
        border-bottom: 3px solid var(--blue) !important;
        font-weight: 800 !important;
        box-shadow: none !important;
    }}
    [data-baseweb="select"] > div,
    [data-baseweb="input"] > div,
    [data-baseweb="textarea"] > div,
    [data-testid="stFileUploader"] section {{
        background: var(--panel-soft) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        backdrop-filter: none !important;
    }}
    .stButton button,
    [data-testid="stDownloadButton"] button,
    [data-testid="stFormSubmitButton"] button {{
        border: 1px solid var(--blue) !important;
        border-radius: 8px !important;
        background: var(--blue) !important;
        color: #FFFFFF !important;
        font-weight: 750 !important;
        box-shadow: none !important;
        transition: transform .16s ease, filter .16s ease !important;
    }}
    .stButton button:hover,
    [data-testid="stDownloadButton"] button:hover {{
        filter: brightness(1.08) !important;
        transform: translateY(-1px) !important;
    }}
    [data-testid="stDataFrame"],
    [data-testid="stTable"],
    [data-testid="stPlotlyChart"] {{
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
        box-shadow: none !important;
    }}
    .sf-hero {{
        border-left: 5px solid var(--blue) !important;
        border-radius: 12px !important;
    }}
    .sf-landing-hero {{
        background: linear-gradient(115deg, var(--hero), var(--hero2)) !important;
        border-radius: 16px !important;
        box-shadow: 0 15px 36px rgba(0,0,0,.12) !important;
    }}
    .sf-preview-card {{
        border-top: 4px solid var(--blue) !important;
        border-radius: 12px !important;
        box-shadow: 0 12px 28px rgba(0,0,0,.12) !important;
    }}
    .sf-feature {{
        border-radius: 10px !important;
        box-shadow: 0 5px 16px rgba(0,0,0,.06) !important;
    }}
    .sf-chart-shell {{
        background: var(--panel-soft) !important;
        border-color: var(--border) !important;
    }}
    .sf-chart span {{
        background: linear-gradient(180deg, var(--blue-light), var(--blue)) !important;
        box-shadow: none !important;
    }}
    .sf-kicker-dot {{
        background: var(--blue) !important;
        box-shadow: none !important;
    }}
    .sf-landing-title span,
    .sf-landing-kicker,
    .sf-brand {{
        color: var(--blue-light) !important;
    }}
    .sf-landing-points span:before {{
        color: var(--teal) !important;
    }}
    .sf-live-pill {{
        color: var(--teal) !important;
        background: var(--success-bg) !important;
        border-color: var(--success-border) !important;
    }}
    .theme-label {{
        color: var(--muted) !important;
        font-size: .72rem !important;
        font-weight: 800 !important;
        letter-spacing: .12em !important;
        text-transform: uppercase;
        margin: .85rem 0 .35rem 0;
    }}
    hr {{ border-color: var(--border) !important; }}
    h1, h2, h3 {{ letter-spacing: -.025em; }}
    @media (prefers-reduced-motion: reduce) {{
        *, *::before, *::after {{
            transition-duration: .01ms !important;
            animation-duration: .01ms !important;
        }}
    }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# PRESENTATION UI POLISH — CSS ONLY
# Keeps the existing theme palette and all Streamlit controls,
# callbacks, data bindings, calculations, and forecasting logic.
# =========================================================
st.markdown(
    """
    <style>

    /* Compact executive dashboard layout inspired by the supplied reference.
       Existing theme variables are reused; no palette values are changed. */
    .sf-dataset-strip {
        display: grid;
        grid-template-columns: 1.05fr 2.1fr 1.25fr .7fr .8fr;
        align-items: center;
        gap: 12px;
        margin: .15rem 0 .45rem;
        padding: 11px 14px;
        border: 1px solid var(--border);
        border-radius: 10px;
        background: var(--panel-alt);
        color: var(--text);
    }
    .sf-dataset-strip > div {
        min-width: 0;
        padding-left: 12px;
        border-left: 1px solid var(--border);
    }
    .sf-dataset-strip > div:first-child {
        padding-left: 0;
        border-left: 0;
    }
    .sf-dataset-strip span {
        display: block;
        color: var(--muted);
        font-size: .58rem;
        font-weight: 750;
        letter-spacing: .09em;
        margin-bottom: 3px;
    }
    .sf-dataset-strip strong {
        display: block;
        color: var(--text);
        font-size: .70rem;
        font-weight: 700;
        line-height: 1.35;
        overflow-wrap: anywhere;
    }
    .sf-dataset-heading {
        color: var(--text);
        font-size: .82rem;
        font-weight: 800;
        white-space: nowrap;
    }
    div[data-testid="stMetric"] {
        min-height: 78px !important;
        padding: 10px 12px !important;
        border-radius: 10px !important;
    }
    [data-testid="stMetricLabel"] p {
        font-size: .68rem !important;
    }
    [data-testid="stMetricValue"] {
        font-size: clamp(1.05rem, 1.45vw, 1.45rem) !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        padding: .72rem .78rem .58rem !important;
        border-radius: 11px !important;
    }
    .sf-panel-title {
        font-size: .86rem !important;
        margin-bottom: .15rem !important;
    }
    .sf-panel-subtitle {
        font-size: .65rem !important;
        margin-bottom: .35rem !important;
    }
    div[data-testid="stPlotlyChart"] {
        margin: 0 !important;
    }
    @media (max-width: 1100px) {
        .sf-dataset-strip {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .sf-dataset-strip > div:nth-child(odd) {
            border-left: 0;
            padding-left: 0;
        }
    }
    @media (max-width: 760px) {
        .sf-dataset-strip {
            grid-template-columns: 1fr;
        }
        .sf-dataset-strip > div {
            border-left: 0;
            border-top: 1px solid var(--border);
            padding: 8px 0 0;
        }
        .sf-dataset-strip > div:first-child {
            border-top: 0;
            padding-top: 0;
        }
    }


    .sf-hero {
        padding: 15px 20px !important;
        margin: 0 0 .7rem 0 !important;
        border-radius: 12px !important;
    }
    .sf-hero .sf-title {
        font-size: 1.45rem !important;
    }
    .sf-hero .sf-subtitle {
        font-size: .72rem !important;
        margin-top: .25rem !important;
    }
    .sf-hero .sf-accent {
        margin-top: .45rem !important;
        width: 42px !important;
    }
    div[data-testid="stTabs"] [role="tablist"] {
        margin-bottom: .65rem !important;
        padding: 4px !important;
    }
    div[data-testid="stTabs"] button[role="tab"] {
        min-height: 37px !important;
        padding: 8px 11px !important;
    }


    /* Automatic, infinite chart motion. This is presentation-only:
       it does not change any underlying sales, forecast, or metric values. */
    @keyframes sf-line-flow {
        from { stroke-dashoffset: 0; }
        to   { stroke-dashoffset: -30; }
    }
    @keyframes sf-bar-breathe {
        0%, 100% { transform: scaleY(0.985); }
        50%      { transform: scaleY(1); }
    }
    @keyframes sf-point-glow {
        0%, 100% { opacity: .82; }
        50%      { opacity: 1; }
    }
    @keyframes sf-heatmap-breathe {
        0%, 100% { opacity: .92; }
        50%      { opacity: 1; }
    }

    /* Moving line traces — retain the original trace colors. */
    .js-plotly-plot .scatterlayer .trace.scatter path.js-line,
    .js-plotly-plot .scatterlayer .trace.scattergl path.js-line {
        stroke-dasharray: 28 2 !important;
        animation: sf-line-flow 2.4s linear infinite;
    }

    /* Gentle, continuous movement for bar charts. */
    .js-plotly-plot .barlayer .trace.bars path,
    .js-plotly-plot .barlayer .trace.bars rect {
        transform-box: fill-box;
        transform-origin: center bottom;
        animation: sf-bar-breathe 2.2s ease-in-out infinite;
    }

    /* Subtle movement for points and heatmap cells. */
    .js-plotly-plot .scatterlayer .trace.scatter .points path {
        animation: sf-point-glow 2s ease-in-out infinite;
    }
    .js-plotly-plot .hm .hm-layer image,
    .js-plotly-plot .hm .hm-layer rect {
        animation: sf-heatmap-breathe 3s ease-in-out infinite;
    }

    @media (prefers-reduced-motion: reduce) {
        .js-plotly-plot .scatterlayer .trace.scatter path.js-line,
        .js-plotly-plot .scatterlayer .trace.scattergl path.js-line,
        .js-plotly-plot .barlayer .trace.bars path,
        .js-plotly-plot .barlayer .trace.bars rect,
        .js-plotly-plot .scatterlayer .trace.scatter .points path,
        .js-plotly-plot .hm .hm-layer image,
        .js-plotly-plot .hm .hm-layer rect {
            animation: none !important;
        }
    }

    /* Workspace proportions and visual rhythm */
    .block-container {
        max-width: 1720px !important;
        padding-top: 2.0rem !important;
        padding-bottom: 3rem !important;
    }
    section[data-testid="stSidebar"] {
        min-width: 285px !important;
        border-right: 1px solid var(--border) !important;
        box-shadow: 8px 0 28px rgba(0,0,0,.08);
    }
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 1.1rem;
    }
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: .9rem;
    }

    /* Executive header — same theme colors, more depth */
    .sf-hero {
        position: relative;
        overflow: hidden;
        border-radius: 18px !important;
        padding: 25px 30px !important;
        margin-bottom: 1.35rem !important;
        background:
          linear-gradient(115deg,
            color-mix(in srgb, var(--hero) 96%, transparent),
            color-mix(in srgb, var(--hero2) 92%, transparent)) !important;
        border: 1px solid var(--border) !important;
        box-shadow: 0 14px 34px rgba(0,0,0,.12) !important;
    }
    .sf-hero:after {
        content: "";
        position: absolute;
        width: 230px;
        height: 230px;
        right: -85px;
        top: -135px;
        border-radius: 50%;
        border: 1px solid color-mix(in srgb, var(--blue) 38%, transparent);
        box-shadow: 0 0 0 22px color-mix(in srgb, var(--blue) 6%, transparent),
                    0 0 0 48px color-mix(in srgb, var(--blue) 4%, transparent);
        pointer-events: none;
    }
    .sf-title {
        font-size: clamp(1.8rem, 2.8vw, 2.35rem) !important;
        letter-spacing: -.04em !important;
    }
    .sf-subtitle {
        max-width: 980px !important;
        font-size: .9rem !important;
    }

    /* Navigation: clear, compact, presentation-friendly */
    div[data-testid="stTabs"] [role="tablist"] {
        display: flex !important;
        gap: 7px !important;
        padding: 7px !important;
        margin: 0 0 1.1rem 0 !important;
        border: 1px solid var(--border) !important;
        border-radius: 14px !important;
        background: color-mix(in srgb, var(--panel) 88%, transparent) !important;
        box-shadow: 0 7px 20px rgba(0,0,0,.07) !important;
        overflow-x: auto !important;
        scrollbar-width: thin;
    }
    div[data-testid="stTabs"] button[role="tab"] {
        min-height: 43px !important;
        padding: 10px 15px !important;
        border: 1px solid transparent !important;
        border-radius: 9px !important;
        background: transparent !important;
        color: var(--tab-text) !important;
        white-space: nowrap !important;
        transition: background .18s ease, border-color .18s ease, transform .18s ease !important;
    }
    div[data-testid="stTabs"] button[role="tab"] p {
        font-size: .83rem !important;
        font-weight: 720 !important;
        margin: 0 !important;
    }
    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background: var(--tab-active) !important;
        border-color: var(--tab-active-border) !important;
        box-shadow: inset 0 -2px 0 var(--blue) !important;
        color: var(--text) !important;
    }
    div[data-testid="stTabs"] button[role="tab"]:hover {
        background: var(--tab-active) !important;
        border-color: var(--border) !important;
        transform: translateY(-1px);
    }

    /* Dashboard cards: glass-like depth without changing palette */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        position: relative;
        border: 1px solid color-mix(in srgb, var(--border) 92%, transparent) !important;
        border-radius: 15px !important;
        background: linear-gradient(145deg,
          color-mix(in srgb, var(--panel-alt) 94%, transparent),
          color-mix(in srgb, var(--panel) 96%, transparent)) !important;
        box-shadow: 0 9px 25px rgba(0,0,0,.075) !important;
        padding: 1rem 1.05rem .85rem !important;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-2px);
        border-color: color-mix(in srgb, var(--blue) 62%, var(--border)) !important;
        box-shadow: 0 14px 30px rgba(0,0,0,.11) !important;
    }

    /* KPI cards */
    div[data-testid="stMetric"] {
        min-height: 112px !important;
        padding: 15px 16px !important;
        border: 1px solid var(--border) !important;
        border-top: 3px solid var(--blue) !important;
        border-radius: 13px !important;
        background: linear-gradient(150deg, var(--panel-alt), var(--panel)) !important;
        box-shadow: 0 8px 20px rgba(0,0,0,.065) !important;
        transition: transform .18s ease, box-shadow .18s ease !important;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 13px 26px rgba(0,0,0,.11) !important;
    }
    [data-testid="stMetricLabel"] p {
        font-size: .76rem !important;
        font-weight: 650 !important;
        color: var(--muted) !important;
    }
    [data-testid="stMetricValue"] {
        font-size: clamp(1.3rem, 2vw, 1.75rem) !important;
        font-weight: 850 !important;
        letter-spacing: -.035em !important;
        color: var(--text) !important;
    }

    /* Plotly charts: consistent spacing and clean chart canvas */
    div[data-testid="stPlotlyChart"] {
        width: 100% !important;
        border-radius: 11px !important;
        overflow: hidden !important;
        margin-top: .2rem !important;
    }
    div[data-testid="stPlotlyChart"] > div {
        width: 100% !important;
    }
    .sf-panel-title {
        font-size: .98rem !important;
        font-weight: 800 !important;
        letter-spacing: -.015em;
        margin-bottom: .28rem !important;
    }
    .sf-panel-subtitle {
        font-size: .73rem !important;
        line-height: 1.5 !important;
        margin-bottom: .8rem !important;
    }

    /* Tables and expanders */
    div[data-testid="stDataFrame"],
    div[data-testid="stTable"] {
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
        box-shadow: 0 7px 18px rgba(0,0,0,.055) !important;
    }
    div[data-testid="stExpander"] {
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
        background: color-mix(in srgb, var(--panel) 92%, transparent) !important;
    }

    /* Buttons retain the existing theme-driven colors */
    .stButton button,
    div[data-testid="stDownloadButton"] button {
        min-height: 42px !important;
        border-radius: 9px !important;
        font-weight: 700 !important;
        transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease !important;
    }
    .stButton button:hover,
    div[data-testid="stDownloadButton"] button:hover {
        transform: translateY(-1px);
        border-color: var(--blue) !important;
        box-shadow: 0 7px 16px rgba(0,0,0,.09) !important;
    }

    /* Sidebar controls */
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] > label,
    section[data-testid="stSidebar"] [data-testid="stExpander"] summary {
        font-weight: 720 !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        min-height: 43px;
        border-radius: 9px !important;
        border-color: var(--border) !important;
        background: var(--panel-soft) !important;
    }

    /* Responsive layout */
    @media (max-width: 900px) {
        .block-container {
            padding-left: .9rem !important;
            padding-right: .9rem !important;
        }
        .sf-hero { padding: 21px 20px !important; }
        div[data-testid="stTabs"] [role="tablist"] { gap: 4px !important; }
        div[data-testid="stTabs"] button[role="tab"] { padding: 9px 11px !important; }
    }
    @media (prefers-reduced-motion: reduce) {
        div[data-testid="stVerticalBlockBorderWrapper"],
        div[data-testid="stMetric"],
        .stButton button,
        div[data-testid="stDownloadButton"] button {
            transition: none !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# HELPER FUNCTIONS
# =========================================================
def panel_heading(title: str, subtitle: str | None = None) -> None:
    safe_title = html.escape(str(title))
    subtitle_html = ""
    if subtitle:
        subtitle_html = (
            f'<div class="sf-panel-subtitle">{html.escape(str(subtitle))}</div>'
        )
    st.markdown(
        f'<div class="sf-panel-title">{safe_title}</div>{subtitle_html}',
        unsafe_allow_html=True,
    )


def dashboard_metric(label: str, value: str, note: str = "") -> None:
    safe_label = html.escape(str(label))
    safe_value = html.escape(str(value))
    note_html = f'<div class="sf-metric-note">{html.escape(str(note))}</div>' if note else ""
    html_block = (
        '<div class="sf-metric-row">'
        f'<div class="sf-metric-label">{safe_label}</div>'
        '<div>'
        f'<div class="sf-metric-value">{safe_value}</div>'
        f'{note_html}'
        '</div>'
        '</div>'
    )
    st.markdown(html_block, unsafe_allow_html=True)


def style_figure(fig, height: int = 340):
    fig.update_layout(
        template="plotly_dark" if theme["name"] == "dark" else "plotly_white",
        height=height,
        autosize=True,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=theme["text"], family="Arial", size=10),
        margin=dict(l=42, r=18, t=38, b=42),
        showlegend=False,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=9, color=theme["text"]),
        ),
    )
    fig.update_xaxes(
        title_font=dict(size=10, color=theme["text"]),
        tickfont=dict(size=9, color=theme["muted"]),
        automargin=True,
        gridcolor="rgba(130,151,178,0.13)",
        zerolinecolor="rgba(130,151,178,0.18)",
        showline=False,
    )
    fig.update_yaxes(
        title_font=dict(size=10, color=theme["text"]),
        tickfont=dict(size=9, color=theme["muted"]),
        automargin=True,
        gridcolor="rgba(130,151,178,0.13)",
        zerolinecolor="rgba(130,151,178,0.18)",
        showline=False,
    )
    return fig


def add_chart_motion(fig, frame_count: int = 16):
    """
    Add optional Play/Pause animation to an existing Plotly figure.
    The animation uses the figure's existing x/y/z values only; it does not
    generate, alter, or simulate sales observations.
    """
    import math
    import plotly.graph_objects as go

    if not fig.data:
        return fig

    animated_traces = []
    for trace_index, trace in enumerate(fig.data):
        trace_type = getattr(trace, "type", "")
        if trace_type == "heatmap":
            z_values = getattr(trace, "z", None)
            if z_values is not None and len(z_values):
                animated_traces.append((trace_index, "heatmap", z_values))
            continue

        x_values = getattr(trace, "x", None)
        y_values = getattr(trace, "y", None)
        if x_values is None or y_values is None:
            continue
        if len(x_values) == 0 or len(y_values) == 0:
            continue
        if trace_type not in ("scatter", "bar", "scattergl"):
            continue
        animated_traces.append((trace_index, trace_type, (x_values, y_values)))

    if not animated_traces:
        return fig

    frames = []
    for step in range(1, frame_count + 1):
        progress = step / frame_count
        frame_data = []
        trace_indices = []

        for trace_index, trace_type, values in animated_traces:
            trace = fig.data[trace_index]

            if trace_type == "heatmap":
                z_rows = [list(row) for row in values]
                visible_rows = max(1, math.ceil(len(z_rows) * progress))
                revealed_z = [
                    row if row_index < visible_rows else [None] * len(row)
                    for row_index, row in enumerate(z_rows)
                ]
                frame_data.append(go.Heatmap(z=revealed_z))
                trace_indices.append(trace_index)
                continue

            x_values, y_values = values
            point_count = min(len(x_values), len(y_values))

            if trace_type == "bar":
                # Keep all category labels visible while bars grow from zero
                # toward the exact values in the source dataset.
                orientation = getattr(trace, "orientation", "v")
                if orientation == "h":
                    animated_x = [float(value) * progress for value in x_values]
                    frame_data.append(go.Bar(x=animated_x, y=list(y_values)))
                else:
                    animated_y = [float(value) * progress for value in y_values]
                    frame_data.append(go.Bar(x=list(x_values), y=animated_y))
                trace_indices.append(trace_index)
                continue

            visible_points = max(1, math.ceil(point_count * progress))
            frame_data.append(
                go.Scatter(
                    x=list(x_values[:visible_points]),
                    y=list(y_values[:visible_points]),
                )
            )
            trace_indices.append(trace_index)

        frames.append(
            go.Frame(
                name=f"reveal-{step}",
                data=frame_data,
                traces=trace_indices,
            )
        )

    fig.frames = tuple(frames)

    existing_menus = list(fig.layout.updatemenus) if fig.layout.updatemenus else []
    existing_menus.append(
        dict(
            type="buttons",
            direction="right",
            x=1,
            xanchor="right",
            y=1.16,
            yanchor="top",
            showactive=False,
            bgcolor="rgba(35, 170, 184, 0.16)",
            bordercolor="rgba(65, 190, 200, 0.55)",
            borderwidth=1,
            font=dict(size=10, color=theme["text"]),
            buttons=[
                dict(
                    label="▶ Play",
                    method="animate",
                    args=[
                        None,
                        {
                            "frame": {"duration": 55, "redraw": True},
                            "transition": {"duration": 45, "easing": "cubic-in-out"},
                            "fromcurrent": False,
                            "mode": "immediate",
                        },
                    ],
                ),
                dict(
                    label="Ⅱ Pause",
                    method="animate",
                    args=[
                        [None],
                        {
                            "frame": {"duration": 0, "redraw": False},
                            "transition": {"duration": 0},
                            "mode": "immediate",
                        },
                    ],
                ),
            ],
        )
    )
    fig.update_layout(
        updatemenus=existing_menus,
        transition={"duration": 300, "easing": "cubic-in-out"},
        hovermode="x unified",
    )
    return fig


# =========================================================
# LANDING PAGE — SIMPLE SALES GRAPH DESIGN
# Only this landing-page section is redesigned.
# Existing data loading, forecasting, evaluation, and dashboard
# functions below remain unchanged.
# =========================================================
if not st.session_state.show_dashboard:
    top_left, top_right = st.columns([5, 1], vertical_alignment="center")

    with top_left:
        st.markdown(
            '<div class="sf-brand">STA. CRUZ, LAGUNA &nbsp;·&nbsp; SALES INTELLIGENCE</div>',
            unsafe_allow_html=True,
        )

    with top_right:
        landing_theme_label = (
            "☀️ Light Mode"
            if st.session_state.theme_mode == "dark"
            else "🌙 Dark Mode"
        )
        st.button(
            landing_theme_label,
            key="landing_theme_toggle",
            on_click=toggle_theme,
            use_container_width=True,
        )

    st.html(
        textwrap.dedent(
            """
            <style>
            .sf-landing-hero {
                display:grid; grid-template-columns:1.02fr .98fr;
                align-items:center; gap:clamp(24px,4vw,52px);
                min-height:470px; padding:clamp(28px,4.5vw,58px);
                border-radius:18px; border:1px solid var(--border);
                background:linear-gradient(115deg,var(--hero),var(--hero2));
                box-shadow:0 14px 36px rgba(0,0,0,.12);
            }
            .sf-landing-kicker {color:var(--blue-light);font-size:.70rem;
                font-weight:800;letter-spacing:.18em;margin-bottom:1.2rem;}
            .sf-landing-title {color:var(--text);font-size:clamp(2.1rem,4vw,3.65rem);
                font-weight:850;line-height:1.08;letter-spacing:-.045em;margin:0;}
            .sf-landing-title span {color:var(--blue-light);}
            .sf-landing-copy {color:var(--muted);font-size:.96rem;line-height:1.8;
                max-width:590px;margin:1.2rem 0 1.4rem;}
            .sf-landing-points {display:flex;flex-wrap:wrap;gap:10px 18px;
                color:var(--text);font-size:.76rem;}
            .sf-landing-points span:before {content:"✓";color:var(--teal);
                font-weight:900;margin-right:7px;}
            .sf-preview-card {padding:22px;border:1px solid var(--border);
                border-radius:14px;background:var(--panel);
                box-shadow:0 12px 28px rgba(0,0,0,.10);}
            .sf-preview-top {display:flex;justify-content:space-between;align-items:center;
                gap:8px;color:var(--muted);font-size:.63rem;font-weight:800;letter-spacing:.12em;}
            .sf-live-pill {color:var(--teal);background:var(--success-bg);
                border:1px solid var(--success-border);border-radius:20px;
                padding:5px 9px;font-size:.59rem;white-space:nowrap;}
            .sf-preview-heading {color:var(--text);font-size:1.22rem;
                font-weight:800;margin:17px 0 3px;}
            .sf-preview-sub {color:var(--muted);font-size:.72rem;margin-bottom:18px;}
            .sf-chart-shell {border:1px solid var(--border);border-radius:11px;
                background:var(--panel-soft);padding:14px 14px 9px;}
            .sf-chart-label {display:flex;justify-content:space-between;gap:8px;
                color:var(--muted);font-size:.62rem;font-weight:750;
                letter-spacing:.08em;margin-bottom:8px;}
            .sf-chart-svg {width:100%;height:auto;display:block;}
            .sf-chart-note {color:var(--muted);font-size:.62rem;margin-top:7px;}
            .sf-model-tags {display:flex;flex-wrap:wrap;gap:7px;margin-top:14px;}
            .sf-model-tags span {color:var(--text);font-size:.61rem;padding:5px 8px;
                border:1px solid var(--border);border-radius:6px;background:var(--panel-soft);}
            @media(max-width:850px) {
                .sf-landing-hero {grid-template-columns:1fr;min-height:0;padding:28px 22px;}
            }
            </style>

            <div class="sf-landing-wrap">
              <section class="sf-landing-hero">
                <div class="sf-landing-copy-wrap">
                  <div class="sf-landing-kicker">● BUSINESS INTELLIGENCE PLATFORM</div>
                  <h1 class="sf-landing-title">Turn Sales Data Into <span>Smarter Decisions.</span></h1>
                  <p class="sf-landing-copy">
                    Monitor historical demand, compare forecasting models, and examine
                    predicted sales through one decision support workspace. Transform
                    recorded sales data into clear, practical insights for better planning.
                  </p>
                  <div class="sf-landing-points">
                    <span>Historical Demand Analysis</span>
                    <span>Forecast Model Comparison</span>
                    <span>Demand Prediction</span>
                  </div>
                </div>

                <div class="sf-preview-card">
                  <div class="sf-preview-top">
                    <span>SALES PERFORMANCE OVERVIEW</span>
                    <span class="sf-live-pill">ANALYTICS PREVIEW</span>
                  </div>
                  <div class="sf-preview-heading">Sales Forecasting DSS</div>
                  <div class="sf-preview-sub">A clear view of sales movement and demand patterns</div>

                  <div class="sf-chart-shell">
                    <div class="sf-chart-label">
                      <span>SALES TREND PREVIEW</span><span>ILLUSTRATIVE</span>
                    </div>
                    <svg class="sf-chart-svg" viewBox="0 0 520 225" role="img"
                         aria-label="Illustrative sales trend line graph">
                      <defs>
                        <linearGradient id="sfArea" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stop-color="#43B99A" stop-opacity=".28"/>
                          <stop offset="100%" stop-color="#43B99A" stop-opacity="0"/>
                        </linearGradient>
                      </defs>
                      <g stroke="var(--border)" stroke-width="1" opacity=".75">
                        <line x1="42" y1="25" x2="500" y2="25"/>
                        <line x1="42" y1="70" x2="500" y2="70"/>
                        <line x1="42" y1="115" x2="500" y2="115"/>
                        <line x1="42" y1="160" x2="500" y2="160"/>
                        <line x1="42" y1="195" x2="500" y2="195"/>
                      </g>
                      <g fill="var(--muted)" font-size="10">
                        <text x="5" y="29">100</text><text x="11" y="74">75</text>
                        <text x="11" y="119">50</text><text x="11" y="164">25</text>
                        <text x="19" y="199">0</text><text x="42" y="215">Jan</text>
                        <text x="130" y="215">Feb</text><text x="220" y="215">Mar</text>
                        <text x="310" y="215">Apr</text><text x="400" y="215">May</text>
                        <text x="480" y="215">Jun</text>
                      </g>
                      <path d="M42 155 L125 130 L208 143 L291 88 L374 103 L457 42 L457 195 L42 195 Z"
                            fill="url(#sfArea)"/>
                      <path d="M42 155 L125 130 L208 143 L291 88 L374 103 L457 42"
                            fill="none" stroke="#43B99A" stroke-width="4"
                            stroke-linecap="round" stroke-linejoin="round"/>
                      <g fill="#43B99A" stroke="var(--panel)" stroke-width="3">
                        <circle cx="42" cy="155" r="5"/><circle cx="125" cy="130" r="5"/>
                        <circle cx="208" cy="143" r="5"/><circle cx="291" cy="88" r="5"/>
                        <circle cx="374" cy="103" r="5"/><circle cx="457" cy="42" r="5"/>
                      </g>
                    </svg>
                    <div class="sf-chart-note">
                      Illustrative graph only. Actual results appear inside the dashboard
                      after a dataset is loaded.
                    </div>
                  </div>

                  <div class="sf-model-tags">
                    <span>ARIMA</span><span>SARIMA</span>
                    <span>PROPHET</span><span>RANDOM FOREST</span>
                  </div>
                </div>
              </section>
            </div>
            """
        )
    )

    st.write("")
    cta_left, cta_right = st.columns([1.1, 4.0], vertical_alignment="center")
    with cta_left:
        if st.button(
            "Open Dashboard  →",
            type="primary",
            use_container_width=True,
            key="enter_dashboard",
        ):
            st.session_state.show_dashboard = True
            st.rerun()
    with cta_right:
        st.markdown(
            '<div class="sf-landing-cta-note">View your uploaded sales data, forecasting models, evaluation results, and reports.</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="sf-footer">STA. CRUZ LAGUNA SALES FORECASTING DECISION SUPPORT SYSTEM</div>',
        unsafe_allow_html=True,
    )
    st.stop()


# =========================================================
# DATA LOADING
# =========================================================
DATA_DIR = Path("data")


SUPABASE_BUCKET = "sales-datasets"
MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # Supabase bucket currently has a 50 MB default limit.


@st.cache_resource
def get_supabase_client():
    """Create a server-side Supabase client using Streamlit Secrets."""
    from supabase import create_client

    supabase_url = st.secrets.get("SUPABASE_URL", "")
    # Accept common secret-key names. A private bucket requires a privileged
    # server-side key or an authenticated Storage policy.
    supabase_key = (
        st.secrets.get("SUPABASE_SECRET_KEY", "")
        or st.secrets.get("SUPABASE_SERVICE_ROLE_KEY", "")
        or st.secrets.get("SUPABASE_KEY", "")
    )

    if not supabase_url or not supabase_key:
        raise RuntimeError(
            "Supabase credentials are missing. Add SUPABASE_URL and "
            "SUPABASE_SECRET_KEY (or SUPABASE_SERVICE_ROLE_KEY) in "
            "Streamlit App settings → Secrets."
        )

    return create_client(supabase_url, supabase_key)


def safe_storage_filename(filename: str) -> str:
    """Keep only a safe filename while preserving its extension."""
    cleaned = Path(filename).name.strip()
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", cleaned)
    return cleaned[:120] or "dataset"


def parse_uploaded_dataset(uploaded_file):
    """Read CSV/XLSX content for a basic preview before saving."""
    file_bytes = uploaded_file.getvalue()
    suffix = Path(uploaded_file.name).suffix.lower()

    if suffix == ".csv":
        preview_df = pd.read_csv(io.BytesIO(file_bytes), nrows=100)
    elif suffix == ".xlsx":
        preview_df = pd.read_excel(io.BytesIO(file_bytes), nrows=100)
    else:
        raise ValueError("Only CSV and XLSX files are supported.")

    if preview_df.empty or len(preview_df.columns) == 0:
        raise ValueError("The uploaded file appears to be empty or has no readable columns.")

    return file_bytes, preview_df


def upload_dataset_to_supabase(uploaded_file, file_bytes: bytes):
    """Persist the original dataset in the private Supabase Storage bucket."""
    client = get_supabase_client()
    safe_name = safe_storage_filename(uploaded_file.name)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    object_path = f"uploads/{timestamp}_{uuid4().hex[:8]}_{safe_name}"

    content_type = uploaded_file.type or "application/octet-stream"
    client.storage.from_(SUPABASE_BUCKET).upload(
        path=object_path,
        file=file_bytes,
        file_options={
            "content-type": content_type,
            "upsert": "false",
        },
    )
    return object_path


def list_supabase_datasets():
    """Return objects stored under the uploads/ folder."""
    client = get_supabase_client()
    return client.storage.from_(SUPABASE_BUCKET).list("uploads")


def download_supabase_dataset(object_name: str):
    """Download one object from the private Supabase bucket."""
    client = get_supabase_client()
    return client.storage.from_(SUPABASE_BUCKET).download(f"uploads/{object_name}")


def delete_supabase_dataset(object_name: str):
    """Permanently delete one uploaded dataset from the uploads/ folder."""
    safe_name = Path(str(object_name)).name
    if not safe_name or safe_name in {".", ".."} or safe_name != str(object_name):
        raise ValueError("Invalid dataset filename. Only files inside uploads/ can be deleted.")

    client = get_supabase_client()
    return client.storage.from_(SUPABASE_BUCKET).remove([f"uploads/{safe_name}"])


# =========================================================
# PHASE 2: AUTOMATIC DUAL-TARGET FORECASTING
# Methodology follows the project's original Colab notebook:
# daily sum aggregation; ARIMA(5,1,2); SARIMA(5,1,2)x(1,1,1,7);
# Prophet yearly + weekly seasonality; recursive Random Forest;
# previous calendar year for validation and latest calendar year for test.
# =========================================================
ARIMA_ORDER = (5, 1, 2)
SARIMA_ORDER = (5, 1, 2)
SARIMA_SEASONAL_ORDER = (1, 1, 1, 7)
RANDOM_STATE = 42
RF_FEATURES = [
    "Year", "Month", "Day", "Day_of_Week", "Is_Weekend",
    "Lag_1", "Lag_7", "Rolling_7",
]
FORECAST_MODEL_NAMES = ["ARIMA", "SARIMA", "Prophet", "Random Forest"]


def prepare_dual_target_series(raw_df: pd.DataFrame):
    """Validate transaction data and aggregate quantity and revenue by day."""
    required = {"Date", "Quantity_Sold", "Total_Sales"}
    missing = required.difference(raw_df.columns)
    if missing:
        raise ValueError(
            "The uploaded dataset is missing required columns: "
            + ", ".join(sorted(missing))
            + ". Both Quantity_Sold and Total_Sales are required for the selected Both option."
        )

    frame = raw_df.copy()
    frame["Date"] = pd.to_datetime(frame["Date"], errors="coerce").dt.normalize()
    frame["Quantity_Sold"] = pd.to_numeric(frame["Quantity_Sold"], errors="coerce")
    frame["Total_Sales"] = pd.to_numeric(frame["Total_Sales"], errors="coerce")

    if frame["Date"].isna().any():
        raise ValueError("Some Date values are missing or invalid. Correct them before forecasting.")
    for column in ["Quantity_Sold", "Total_Sales"]:
        if frame[column].isna().any():
            raise ValueError(f"{column} contains missing or non-numeric values.")
        if (frame[column] < 0).any():
            raise ValueError(f"Negative values were found in {column}. Verify returns or adjustments first.")

    duplicate_rows = int(frame.duplicated().sum())
    if duplicate_rows:
        raise ValueError(
            f"Found {duplicate_rows:,} duplicate full transaction rows. "
            "Resolve duplicates before forecasting to avoid double-counting."
        )
    if "ID" in frame.columns:
        duplicate_ids = int(frame["ID"].duplicated().sum())
        if duplicate_ids:
            raise ValueError(
                f"Found {duplicate_ids:,} duplicate transaction IDs. "
                "Resolve duplicate IDs before forecasting."
            )

    daily = (
        frame.groupby("Date", as_index=True)[["Quantity_Sold", "Total_Sales"]]
        .sum()
        .sort_index()
    )
    expected_dates = pd.date_range(daily.index.min(), daily.index.max(), freq="D")
    missing_dates = expected_dates.difference(daily.index)
    if len(missing_dates):
        examples = ", ".join(str(d.date()) for d in missing_dates[:5])
        raise ValueError(
            f"The dataset has {len(missing_dates):,} calendar dates without transactions "
            f"(examples: {examples}). The original notebook does not silently fill missing "
            "dates with zero demand. Confirm whether these are true zero-sales days or missing records."
        )

    daily = daily.asfreq("D")
    if len(daily) < 400:
        raise ValueError(
            "At least 400 consecutive daily observations are required for this four-model "
            "comparison and yearly validation approach."
        )

    latest_year = int(daily.index.max().year)
    validation_year = latest_year - 1
    test_year = latest_year
    validation_actual = daily.loc[daily.index.year == validation_year]
    test_actual = daily.loc[daily.index.year == test_year]
    train_validation = daily.loc[daily.index < pd.Timestamp(f"{validation_year}-01-01")]
    train_test = daily.loc[daily.index < pd.Timestamp(f"{test_year}-01-01")]

    if validation_actual.empty or test_actual.empty or train_validation.empty or train_test.empty:
        raise ValueError(
            "The uploaded dataset must contain at least one full training period, "
            "the previous calendar year for validation, and the latest calendar year for testing."
        )
    if validation_actual.index.min() != pd.Timestamp(f"{validation_year}-01-01"):
        raise ValueError(f"Validation year {validation_year} is incomplete at the beginning of the year.")
    if test_actual.index.min() != pd.Timestamp(f"{test_year}-01-01"):
        raise ValueError(f"Test year {test_year} is incomplete at the beginning of the year.")

    return {
        "daily": daily,
        "validation_year": validation_year,
        "test_year": test_year,
        "train_validation": train_validation,
        "validation_actual": validation_actual,
        "train_test": train_test,
        "test_actual": test_actual,
    }


def calculate_forecast_metrics(actual, predicted):
    import numpy as np
    from sklearn.metrics import mean_absolute_error, mean_squared_error

    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    errors = actual - predicted
    absolute_errors = np.abs(errors)
    nonzero = actual != 0
    mape = (
        float(np.mean(absolute_errors[nonzero] / np.abs(actual[nonzero])) * 100)
        if nonzero.any() else float("nan")
    )
    denominator = float(np.sum(np.abs(actual)))
    wape = float(np.sum(absolute_errors) / denominator * 100) if denominator else float("nan")
    return {
        "MAE": float(mean_absolute_error(actual, predicted)),
        "RMSE": float(np.sqrt(mean_squared_error(actual, predicted))),
        "MAPE (%)": mape,
        "WAPE (%)": wape,
    }


def make_rf_training_frame(train_series: pd.Series):
    import pandas as pd

    frame = pd.DataFrame({"Daily_Target": train_series.astype(float).copy()})
    dates = frame.index
    frame["Year"] = dates.year
    frame["Month"] = dates.month
    frame["Day"] = dates.day
    frame["Day_of_Week"] = dates.dayofweek
    frame["Is_Weekend"] = (dates.dayofweek >= 5).astype(int)
    frame["Lag_1"] = frame["Daily_Target"].shift(1)
    frame["Lag_7"] = frame["Daily_Target"].shift(7)
    # Shift before rolling so the current target never leaks into its features.
    frame["Rolling_7"] = frame["Daily_Target"].shift(1).rolling(window=7).mean()
    return frame.dropna()


def forecast_one_model(model_name: str, train_series: pd.Series, future_dates: pd.DatetimeIndex):
    import numpy as np

    if model_name == "ARIMA":
        from statsmodels.tsa.arima.model import ARIMA
        fitted = ARIMA(train_series.astype(float), order=ARIMA_ORDER).fit()
        values = np.asarray(fitted.forecast(steps=len(future_dates)), dtype=float)

    elif model_name == "SARIMA":
        from statsmodels.tsa.statespace.sarimax import SARIMAX
        model = SARIMAX(
            train_series.astype(float),
            order=SARIMA_ORDER,
            seasonal_order=SARIMA_SEASONAL_ORDER,
            enforce_stationarity=False,
            enforce_invertibility=False,
        )
        fitted = model.fit(disp=False, maxiter=150)
        values = np.asarray(fitted.forecast(steps=len(future_dates)), dtype=float)

    elif model_name == "Prophet":
        from prophet import Prophet
        prophet_train = pd.DataFrame({"ds": train_series.index, "y": train_series.values})
        model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False,
        )
        model.fit(prophet_train)
        future_frame = pd.DataFrame({"ds": future_dates})
        values = model.predict(future_frame)["yhat"].to_numpy(dtype=float)

    elif model_name == "Random Forest":
        from sklearn.ensemble import RandomForestRegressor
        training_frame = make_rf_training_frame(train_series)
        if training_frame.empty:
            raise ValueError("Insufficient training history for Random Forest lag features.")
        model = RandomForestRegressor(
            n_estimators=300,
            min_samples_leaf=2,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )
        model.fit(training_frame[RF_FEATURES], training_frame["Daily_Target"])
        history = list(train_series.astype(float).values)
        predictions = []
        for forecast_date in future_dates:
            row = {
                "Year": forecast_date.year,
                "Month": forecast_date.month,
                "Day": forecast_date.day,
                "Day_of_Week": forecast_date.dayofweek,
                "Is_Weekend": int(forecast_date.dayofweek >= 5),
                "Lag_1": history[-1],
                "Lag_7": history[-7],
                "Rolling_7": float(np.mean(history[-7:])),
            }
            prediction = max(float(model.predict(pd.DataFrame([row], columns=RF_FEATURES))[0]), 0.0)
            predictions.append(prediction)
            history.append(prediction)
        values = np.asarray(predictions, dtype=float)
    else:
        raise ValueError(f"Unsupported forecasting model: {model_name}")

    # Preserve the notebook's non-negative forecast constraint.
    values = np.maximum(values, 0.0)
    return pd.Series(values, index=future_dates, name=model_name)


def run_dual_target_forecasting(raw_df: pd.DataFrame, horizon: int, progress_callback=None):
    """Run the notebook's four models for quantity and revenue targets."""
    import numpy as np

    prepared = prepare_dual_target_series(raw_df)
    daily = prepared["daily"]
    validation_dates = prepared["validation_actual"].index
    test_dates = prepared["test_actual"].index
    future_dates = pd.date_range(
        start=daily.index.max() + pd.Timedelta(days=1),
        periods=int(horizon),
        freq="D",
    )

    validation_frames = []
    test_frames = []
    future_frames = []
    validation_metric_rows = []
    test_metric_rows = []
    total_runs = 2 * len(FORECAST_MODEL_NAMES) * 3
    completed = 0

    for target in ["Quantity_Sold", "Total_Sales"]:
        series = daily[target].astype(float)
        target_label = "Quantity Sold (units)" if target == "Quantity_Sold" else "Total Sales (currency units)"
        runs = [
            ("Validation", prepared["train_validation"][target].astype(float), validation_dates, prepared["validation_actual"][target]),
            ("Final Test", prepared["train_test"][target].astype(float), test_dates, prepared["test_actual"][target]),
            ("Future", series, future_dates, None),
        ]

        for period, train_series, dates, actual_series in runs:
            for model_name in FORECAST_MODEL_NAMES:
                prediction = forecast_one_model(model_name, train_series, dates)
                if period == "Validation":
                    validation_frames.append(pd.DataFrame({
                        "Date": dates, "Target": target, "Target_Label": target_label,
                        "Model": model_name, "Actual": actual_series.to_numpy(dtype=float),
                        "Predicted": prediction.to_numpy(dtype=float),
                    }))
                    metrics = calculate_forecast_metrics(actual_series, prediction)
                    validation_metric_rows.append({"Target": target, "Target_Label": target_label, "Model": model_name, **metrics})
                elif period == "Final Test":
                    test_frames.append(pd.DataFrame({
                        "Date": dates, "Target": target, "Target_Label": target_label,
                        "Model": model_name, "Actual": actual_series.to_numpy(dtype=float),
                        "Predicted": prediction.to_numpy(dtype=float),
                    }))
                    metrics = calculate_forecast_metrics(actual_series, prediction)
                    test_metric_rows.append({"Target": target, "Target_Label": target_label, "Model": model_name, **metrics})
                else:
                    future_frames.append(pd.DataFrame({
                        "Forecast_Date": dates, "Target": target, "Target_Label": target_label,
                        "Model": model_name, "Predicted_Value": prediction.to_numpy(dtype=float),
                        "Forecast_Origin": daily.index.max().date(),
                    }))

                completed += 1
                if progress_callback:
                    progress_callback(completed, total_runs, f"{target_label}: {period} · {model_name}")

    validation_metrics = pd.DataFrame(validation_metric_rows)
    test_metrics = pd.DataFrame(test_metric_rows)
    future_forecasts = pd.concat(future_frames, ignore_index=True)
    validation_predictions = pd.concat(validation_frames, ignore_index=True)
    test_predictions = pd.concat(test_frames, ignore_index=True)

    best_models = (
        validation_metrics.sort_values("WAPE (%)")
        .groupby("Target", as_index=False)
        .first()[["Target", "Model", "WAPE (%)"]]
        .rename(columns={"Model": "Selected_Model", "WAPE (%)": "Validation_WAPE_Percent"})
    )

    return {
        "daily": daily.reset_index().rename(columns={"Date": "Date"}),
        "validation_metrics": validation_metrics,
        "test_metrics": test_metrics,
        "validation_predictions": validation_predictions,
        "test_predictions": test_predictions,
        "future_forecasts": future_forecasts,
        "best_models": best_models,
        "validation_year": prepared["validation_year"],
        "test_year": prepared["test_year"],
        "forecast_origin": daily.index.max(),
        "horizon": int(horizon),
    }


def build_forecast_run_zip(results: dict) -> bytes:
    """Package all dual-target outputs for download and persistent storage."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        exports = {
            "daily_quantity_and_sales.csv": results["daily"],
            "validation_metrics.csv": results["validation_metrics"],
            "final_test_metrics.csv": results["test_metrics"],
            "validation_predictions.csv": results["validation_predictions"],
            "final_test_predictions.csv": results["test_predictions"],
            "future_forecasts.csv": results["future_forecasts"],
            "selected_models.csv": results["best_models"],
        }
        for filename, frame in exports.items():
            archive.writestr(filename, frame.to_csv(index=False).encode("utf-8"))
        metadata = {
            "validation_year": int(results["validation_year"]),
            "final_test_year": int(results["test_year"]),
            "forecast_origin": str(pd.Timestamp(results["forecast_origin"]).date()),
            "forecast_horizon_days": int(results["horizon"]),
            "targets": ["Quantity_Sold", "Total_Sales"],
            "models": FORECAST_MODEL_NAMES,
            "selection_rule": "Lowest validation WAPE per target",
        }
        archive.writestr("run_metadata.json", json.dumps(metadata, indent=2))
    return buffer.getvalue()


def save_forecast_run_to_supabase(zip_bytes: bytes, run_id: str):
    """Persist a completed forecast run under forecast_runs/ in Supabase."""
    client = get_supabase_client()
    object_path = f"forecast_runs/{run_id}/dual_target_forecast_results.zip"
    client.storage.from_(SUPABASE_BUCKET).upload(
        path=object_path,
        file=zip_bytes,
        file_options={"content-type": "application/zip", "upsert": "false"},
    )
    return object_path


def read_required_csv(filename: str) -> pd.DataFrame:
    path = DATA_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(
            f"Required file '{path.as_posix()}' was not found. "
            "Check that the standardized CSV files are in the repository's data/ folder."
        )
    return pd.read_csv(path)


@st.cache_data
def load_standardized_data():
    # 1. Historical daily demand
    actual = read_required_csv("aggregated_daily_demand.csv")
    required = {"Date", "Daily_Demand"}
    missing = required.difference(actual.columns)
    if missing:
        raise ValueError(
            "aggregated_daily_demand.csv is missing columns: "
            + ", ".join(sorted(missing))
        )

    actual = actual.rename(
        columns={"Date": "date", "Daily_Demand": "daily_demand"}
    )
    actual["date"] = pd.to_datetime(actual["date"], errors="coerce")
    actual["daily_demand"] = pd.to_numeric(
        actual["daily_demand"], errors="coerce"
    )
    actual = actual.dropna(subset=["date", "daily_demand"])
    actual = actual.sort_values("date").reset_index(drop=True)

    if actual["date"].duplicated().any():
        raise ValueError(
            "aggregated_daily_demand.csv contains duplicate dates. "
            "Resolve duplicates in the notebook before deployment."
        )

    # 2. Performance metrics
    def load_metrics(filename: str) -> pd.DataFrame:
        metrics = read_required_csv(filename)
        required_metrics = {"Model", "MAE", "RMSE", "MAPE (%)", "WAPE (%)"}
        missing_metrics = required_metrics.difference(metrics.columns)
        if missing_metrics:
            raise ValueError(
                f"{filename} is missing columns: "
                + ", ".join(sorted(missing_metrics))
            )

        metrics = metrics.rename(
            columns={
                "Model": "model_name",
                "MAE": "mae",
                "RMSE": "rmse",
                "MAPE (%)": "mape",
                "WAPE (%)": "wape",
            }
        )
        metrics["model_name"] = metrics["model_name"].astype(str).str.strip()
        for column in ["mae", "rmse", "mape", "wape"]:
            metrics[column] = pd.to_numeric(metrics[column], errors="coerce")

        metrics = metrics.dropna(
            subset=["model_name", "mae", "rmse", "mape", "wape"]
        )
        if metrics["model_name"].duplicated().any():
            raise ValueError(f"{filename} contains duplicate model rows.")
        return metrics

    validation_metrics = load_metrics("validation_model_performance.csv")
    test_metrics = load_metrics("test_model_performance_2024.csv")

    # 3. Validation and final-test predictions
    def load_forecasts(filename: str) -> pd.DataFrame:
        forecasts = read_required_csv(filename)
        required_forecasts = {
            "Forecast_Date",
            "Actual_Demand",
            "Model",
            "Predicted_Demand",
        }
        missing_forecasts = required_forecasts.difference(forecasts.columns)
        if missing_forecasts:
            raise ValueError(
                f"{filename} is missing columns: "
                + ", ".join(sorted(missing_forecasts))
            )

        forecasts = forecasts.rename(
            columns={
                "Forecast_Date": "forecast_date",
                "Actual_Demand": "actual_demand",
                "Model": "model_name",
                "Predicted_Demand": "predicted_demand",
            }
        )
        forecasts["forecast_date"] = pd.to_datetime(
            forecasts["forecast_date"], errors="coerce"
        )
        forecasts["actual_demand"] = pd.to_numeric(
            forecasts["actual_demand"], errors="coerce"
        )
        forecasts["predicted_demand"] = pd.to_numeric(
            forecasts["predicted_demand"], errors="coerce"
        )
        forecasts["model_name"] = forecasts["model_name"].astype(str).str.strip()
        forecasts = forecasts.dropna(
            subset=[
                "forecast_date",
                "actual_demand",
                "predicted_demand",
                "model_name",
            ]
        )
        return forecasts.sort_values(
            ["model_name", "forecast_date"]
        ).reset_index(drop=True)

    validation_predictions = load_forecasts("validation_forecasts_2023.csv")
    test_predictions = load_forecasts("test_forecasts_2024.csv")

    # 4. Future forecasts: historical academic simulation, not live 2026 forecasts
    future = read_required_csv("future_forecasts.csv")
    required_future = {
        "Forecast_Date",
        "Model",
        "Predicted_Demand",
        "Forecast_Origin",
        "Forecast_Type",
    }
    missing_future = required_future.difference(future.columns)
    if missing_future:
        raise ValueError(
            "future_forecasts.csv is missing columns: "
            + ", ".join(sorted(missing_future))
        )

    future = future.rename(
        columns={
            "Forecast_Date": "forecast_date",
            "Model": "model_name",
            "Predicted_Demand": "predicted_demand",
            "Forecast_Origin": "forecast_origin",
            "Forecast_Type": "forecast_type",
        }
    )
    future["forecast_date"] = pd.to_datetime(
        future["forecast_date"], errors="coerce"
    )
    future["predicted_demand"] = pd.to_numeric(
        future["predicted_demand"], errors="coerce"
    )
    future["model_name"] = future["model_name"].astype(str).str.strip()
    future = future.dropna(
        subset=["forecast_date", "predicted_demand", "model_name"]
    ).sort_values(["model_name", "forecast_date"])

    # 5. Model-selection summary
    selection = read_required_csv("model_selection_summary.csv")
    required_selection = {
        "Selected_Model",
        "Selection_Metric",
        "Selection_Period",
        "Selected_Model_Validation_WAPE_Percent",
    }
    missing_selection = required_selection.difference(selection.columns)
    if missing_selection:
        raise ValueError(
            "model_selection_summary.csv is missing columns: "
            + ", ".join(sorted(missing_selection))
        )

    return (
        actual,
        validation_metrics,
        test_metrics,
        validation_predictions,
        test_predictions,
        future,
        selection,
    )


try:
    (
        actual_df,
        validation_performance,
        test_performance,
        validation_forecasts,
        test_forecasts,
        future_df,
        model_selection_summary,
    ) = load_standardized_data()
except Exception as error:
    st.error(f"Unable to load standardized forecasting data: {error}")
    st.stop()


# =========================================================
# UNIFIED ACTIVE DATASET
# Completed Phase 2 runs become the single source of truth
# for Overview, Model Evaluation, and Forecast Analysis.
# =========================================================
phase2_active_results = st.session_state.get("phase2_results")
phase2_active_source = st.session_state.get("phase2_source_name")

if phase2_active_results:
    active_target = st.sidebar.selectbox(
        "Dashboard data target",
        options=["Quantity_Sold", "Total_Sales"],
        format_func=lambda value: (
            "Quantity Sold (units)" if value == "Quantity_Sold"
            else "Total Sales (currency units)"
        ),
        key="unified_dashboard_target",
        help="This target drives Overview, Model Evaluation, and Forecast Analysis.",
    )

    active_daily = phase2_active_results["daily"].copy()
    active_daily["Date"] = pd.to_datetime(active_daily["Date"], errors="coerce")
    active_daily[active_target] = pd.to_numeric(
        active_daily[active_target], errors="coerce"
    )
    active_daily = active_daily.dropna(
        subset=["Date", active_target]
    ).sort_values("Date")

    actual_df = active_daily[["Date", active_target]].rename(
        columns={"Date": "date", active_target: "daily_demand"}
    ).reset_index(drop=True)

    def _legacy_metrics(frame):
        result = frame.loc[frame["Target"] == active_target].copy()
        return result.rename(
            columns={
                "Model": "model_name",
                "MAE": "mae",
                "RMSE": "rmse",
                "MAPE (%)": "mape",
                "WAPE (%)": "wape",
            }
        )[["model_name", "mae", "rmse", "mape", "wape"]]

    validation_performance = _legacy_metrics(
        phase2_active_results["validation_metrics"]
    )
    test_performance = _legacy_metrics(
        phase2_active_results["test_metrics"]
    )

    def _legacy_predictions(frame):
        result = frame.loc[frame["Target"] == active_target].copy()
        return result.rename(
            columns={
                "Date": "forecast_date",
                "Actual": "actual_demand",
                "Model": "model_name",
                "Predicted": "predicted_demand",
            }
        )[["forecast_date", "actual_demand", "model_name", "predicted_demand"]]

    validation_forecasts = _legacy_predictions(
        phase2_active_results["validation_predictions"]
    )
    test_forecasts = _legacy_predictions(
        phase2_active_results["test_predictions"]
    )

    future_df = phase2_active_results["future_forecasts"].loc[
        phase2_active_results["future_forecasts"]["Target"] == active_target
    ].rename(
        columns={
            "Forecast_Date": "forecast_date",
            "Model": "model_name",
            "Predicted_Value": "predicted_demand",
            "Forecast_Origin": "forecast_origin",
        }
    ).copy()
    future_df["forecast_type"] = "Dynamic Phase 2 forecast"

    best_active = phase2_active_results["best_models"].loc[
        phase2_active_results["best_models"]["Target"] == active_target
    ]
    if not best_active.empty:
        model_selection_summary = pd.DataFrame([{
            "Selected_Model": best_active.iloc[0]["Selected_Model"],
            "Selection_Metric": "Validation WAPE",
            "Selection_Period": str(phase2_active_results["validation_year"]),
            "Selected_Model_Validation_WAPE_Percent":
                best_active.iloc[0]["Validation_WAPE_Percent"],
        }])

    st.sidebar.caption(
        f"Active dataset: {phase2_active_source or 'Completed Phase 2 run'}"
    )
    st.sidebar.caption(
        f"Dashboard source: completed Phase 2 run · {active_target}"
    )

if (
    actual_df.empty
    or validation_performance.empty
    or test_performance.empty
    or validation_forecasts.empty
    or test_forecasts.empty
):
    st.error("One or more standardized CSV files contain no usable records.")
    st.stop()

# Keep the existing website's expected variables so its charts continue to work.
# df represents 2024 final-test predictions, with 2024 test metrics attached.
df = test_forecasts.merge(
    test_performance,
    on="model_name",
    how="left",
    validate="many_to_one",
)

preferred_order = ["ARIMA", "SARIMA", "Prophet", "Random Forest"]
available_models = df["model_name"].dropna().unique().tolist()
model_options = [name for name in preferred_order if name in available_models]
model_options += [name for name in available_models if name not in model_options]

# Validation results are used for model selection and ranking.
performance = validation_performance.copy()
validation_counts = (
    validation_forecasts.groupby("model_name")
    .size()
    .rename("forecast_records")
)
performance = performance.merge(
    validation_counts,
    left_on="model_name",
    right_index=True,
    how="left",
)
performance["forecast_records"] = (
    performance["forecast_records"].fillna(0).astype(int)
)

ranking = (
    performance.sort_values("wape", ascending=True, na_position="last")
    .reset_index(drop=True)
)
if ranking["wape"].notna().sum() == 0:
    st.error("Validation WAPE is unavailable. Model selection cannot proceed.")
    st.stop()

ranking.insert(0, "Rank", range(1, len(ranking) + 1))


def performance_level(mape):
    if pd.isna(mape):
        return "Not available"
    if mape < 10:
        return "Excellent"
    if mape < 20:
        return "Good"
    if mape < 50:
        return "Acceptable"
    return "Poor"


ranking["Performance Level"] = ranking["mape"].apply(performance_level)
best_row = ranking.iloc[0]
best_model = str(best_row["model_name"])
lowest_wape = float(best_row["wape"])
lowest_mape = float(best_row["mape"])  # Retained for compatibility if referenced elsewhere.

# Historical summaries used by the existing Overview and Forecast Analysis tabs.
historical_monthly = actual_df.copy()
historical_monthly["month"] = (
    historical_monthly["date"].dt.to_period("M").dt.to_timestamp()
)
monthly_sales = (
    historical_monthly.groupby("month", as_index=False)["daily_demand"].sum()
)

heatmap_source = actual_df.copy()
heatmap_source["month_num"] = heatmap_source["date"].dt.month
heatmap_source["weekday_num"] = heatmap_source["date"].dt.dayofweek
heatmap_values = (
    heatmap_source.pivot_table(
        index="month_num",
        columns="weekday_num",
        values="daily_demand",
        aggfunc="mean",
    ).reindex(index=range(1, 13), columns=range(0, 7))
)

month_labels = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]
weekday_labels = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
]

# =========================================================
# HEADER
# =========================================================
st.markdown(
    """
    <div class="sf-hero">
        <div class="sf-eyebrow">Sta. Cruz Laguna · Business Intelligence</div>
        <div class="sf-title">Sales Forecasting Dashboard</div>
        <p class="sf-subtitle">
            Historical demand monitoring, forecasting model evaluation,
            and demand prediction in one analytics workspace.
        </p>
        <div class="sf-accent"></div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.button(
    "← Back to Home",
    on_click=go_home,
    use_container_width=True,
)

st.sidebar.markdown(
    """
    <div style="padding: 4px 0 8px 0;">
        <div style="font-size:1.22rem;font-weight:800;">
            Forecast Controls
        </div>
        <div style="font-size:0.76rem;margin-top:5px;line-height:1.45;">
            Select a forecasting model to inspect its saved predictions.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

selected_model = st.sidebar.selectbox(
    "Forecasting Model",
    model_options,
    index=model_options.index("Random Forest"),
    key="forecast_model_selector",
)

st.sidebar.divider()
with st.sidebar.expander("System Information", expanded=False):
    st.markdown(
        """
        **Dataset**  
        Sta. Cruz Laguna Sales Dataset

        **Forecasting Models**  
        ARIMA · SARIMA · Prophet · Random Forest

       **Evaluation Metrics**
MAE · RMSE · MAPE · WAPE

        **Platform**  
        Python + Streamlit
        """
    )

# Simple, functional Light/Dark mode switch.
st.sidebar.markdown('<div class="theme-label">APPEARANCE</div>', unsafe_allow_html=True)
theme_button_label = "Switch to Light Mode" if st.session_state.theme_mode == "dark" else "Switch to Dark Mode"
st.sidebar.button(
    theme_button_label,
    on_click=toggle_theme,
    use_container_width=True,
)

model_data = df[df["model_name"] == selected_model].copy()
comparison = model_data.merge(
    actual_df,
    left_on="forecast_date",
    right_on="date",
    how="left",
)
comparison["error"] = comparison["daily_demand"] - comparison["predicted_demand"]
comparison["absolute_error"] = comparison["error"].abs()


# =========================================================
# NAVIGATION TABS
# =========================================================
tab_overview, tab_evaluation, tab_analysis, tab_auto_forecast, tab_live_dataset, tab_downloads = st.tabs(
    [
        "Overview",
        "Model Evaluation",
        "Forecast Analysis",
        "Automatic Forecasting",
        "Live Dataset Studio",
        "Downloads & Data",
    ]
)


def render_no_active_dataset_state():
    """Show a consistent empty state instead of repository baseline metrics."""
    st.info(
        "No active dataset. Upload a CSV/XLSX file in **Downloads & Data**, "
        "then run **Automatic Forecasting**. KPIs, tables, and charts will "
        "appear here only after a successful forecasting run."
    )


# =========================================================
# OVERVIEW
# =========================================================

with tab_overview:
    if not phase2_active_results:
        render_no_active_dataset_state()
    else:
        total_demand = actual_df["daily_demand"].sum()
        average_demand = actual_df["daily_demand"].mean()
        highest_demand = actual_df["daily_demand"].max()
        highest_demand_date = actual_df.loc[
            actual_df["daily_demand"].idxmax(), "date"
        ].date()

        # Compact KPI strip, matching the reference dashboard proportions.
        kpi_cols = st.columns(4, gap="small")
        with kpi_cols[0]:
            st.metric("Total Historical Demand", f"{total_demand:,.0f}")
        with kpi_cols[1]:
            st.metric("Average Daily Demand", f"{average_demand:,.2f}")
        with kpi_cols[2]:
            st.metric(
                "Peak Daily Demand",
                f"{highest_demand:,.0f}",
                help=f"Recorded on {highest_demand_date}",
            )
        with kpi_cols[3]:
            st.metric(
                "Best Model · Validation WAPE",
                f"{lowest_wape:.2f}%",
                help=f"Selected using validation WAPE: {best_model}",
            )

        # Three compact analytical panels on one row, like the supplied UI reference.
        chart_left, chart_middle, chart_right = st.columns([1.55, 1.05, 1.0], gap="small")

        with chart_left:
            with st.container(border=True):
                panel_heading(
                    "Actual vs Forecast",
                    f"{selected_model} · Historical actuals and saved predictions",
                )
                fig_overview_actual_forecast = px.line(
                    comparison,
                    x="forecast_date",
                    y=["daily_demand", "predicted_demand"],
                    color_discrete_map={
                        "daily_demand": theme["blue"],
                        "predicted_demand": theme["gold"],
                    },
                    labels={
                        "forecast_date": "",
                        "value": "Demand",
                        "variable": "Series",
                    },
                )
                fig_overview_actual_forecast.update_traces(line=dict(width=2))
                fig_overview_actual_forecast.update_layout(showlegend=True)
                style_figure(fig_overview_actual_forecast, 245)
                st.plotly_chart(
                    add_chart_motion(fig_overview_actual_forecast),
                    use_container_width=True,
                    config={"responsive": True, "displayModeBar": "hover", "scrollZoom": True},
                )

        with chart_middle:
            with st.container(border=True):
                panel_heading("Monthly Demand", "Historical demand by month")
                fig_monthly_overview = px.bar(
                    monthly_sales,
                    x="month",
                    y="daily_demand",
                    color_discrete_sequence=[theme["blue"]],
                    labels={"month": "", "daily_demand": "Demand"},
                )
                fig_monthly_overview.update_traces(marker_line_width=0, opacity=0.92)
                fig_monthly_overview.update_xaxes(dtick="M3", tickformat="%b", title_text="")
                fig_monthly_overview.update_yaxes(title_text="")
                style_figure(fig_monthly_overview, 245)
                st.plotly_chart(
                    add_chart_motion(fig_monthly_overview),
                    use_container_width=True,
                    config={"responsive": True, "displayModeBar": "hover", "scrollZoom": True},
                )

        with chart_right:
            with st.container(border=True):
                panel_heading(
                    "Model Performance",
                    "Validation WAPE · lower is better",
                )
                model_chart_data = ranking.sort_values("wape", ascending=True)
                fig_overview_models = px.bar(
                    model_chart_data,
                    x="wape",
                    y="model_name",
                    orientation="h",
                    text="wape",
                    color="model_name",
                    color_discrete_map={
                        "ARIMA": theme["blue"],
                        "SARIMA": theme["blue_light"],
                        "Prophet": theme["teal"],
                        "Random Forest": theme["gold"],
                    },
                    labels={"wape": "WAPE (%)", "model_name": ""},
                )
                fig_overview_models.update_traces(
                    texttemplate="%{text:.2f}%",
                    textposition="outside",
                    cliponaxis=False,
                )
                fig_overview_models.update_layout(
                    showlegend=False,
                    xaxis_title="WAPE (%)",
                    yaxis_title="",
                )
                style_figure(fig_overview_models, 245)
                st.plotly_chart(
                    add_chart_motion(fig_overview_models),
                    use_container_width=True,
                    config={"responsive": True, "displayModeBar": "hover", "scrollZoom": True},
                )

        # Secondary row: demand pattern and the selected model's future forecast.
        secondary_left, secondary_right = st.columns([1, 1.55], gap="small")

        with secondary_left:
            with st.container(border=True):
                panel_heading("Demand Pattern", "Average demand by month and weekday")
                fig_heatmap = px.imshow(
                    heatmap_values,
                    x=weekday_labels,
                    y=month_labels,
                    aspect="auto",
                    color_continuous_scale=[
                        theme["panel_soft"],
                        theme["blue"],
                        theme["blue_light"],
                        theme["gold"],
                    ],
                    labels={"x": "", "y": "", "color": "Avg. demand"},
                )
                fig_heatmap.update_layout(
                    coloraxis_colorbar=dict(
                        thickness=8,
                        len=0.76,
                        tickfont=dict(size=8, color=theme["muted"]),
                        title=dict(text="", font=dict(size=8)),
                    )
                )
                fig_heatmap.update_xaxes(tickfont=dict(size=8), side="bottom")
                fig_heatmap.update_yaxes(tickfont=dict(size=8))
                style_figure(fig_heatmap, 255)
                st.plotly_chart(
                    add_chart_motion(fig_heatmap),
                    use_container_width=True,
                    config={"responsive": True, "displayModeBar": "hover", "scrollZoom": True},
                )

        with secondary_right:
            with st.container(border=True):
                panel_heading(
                    f"Forecast Trend · {selected_model}",
                    "Saved predicted demand values for the selected model",
                )
                fig_forecast_overview = px.line(
                    model_data,
                    x="forecast_date",
                    y="predicted_demand",
                    color_discrete_sequence=[theme["gold"]],
                    labels={"forecast_date": "", "predicted_demand": "Predicted demand"},
                )
                fig_forecast_overview.update_traces(
                    line=dict(width=2.2, color=theme["gold"]),
                    mode="lines",
                )
                fig_forecast_overview.update_yaxes(title_text="")
                fig_forecast_overview.update_xaxes(title_text="")
                style_figure(fig_forecast_overview, 205)
                st.plotly_chart(
                    add_chart_motion(fig_forecast_overview),
                    use_container_width=True,
                    config={"responsive": True, "displayModeBar": "hover", "scrollZoom": True},
                )

                forecast_kpis = st.columns(3, gap="small")
                with forecast_kpis[0]:
                    st.metric("Average Forecast", f"{model_data['predicted_demand'].mean():,.1f}")
                with forecast_kpis[1]:
                    st.metric("Peak Forecast", f"{model_data['predicted_demand'].max():,.1f}")
                with forecast_kpis[2]:
                    st.metric("Forecast Records", f"{len(model_data):,}")

        # Slim dataset-status strip, with the currently active source clearly identified.
        if phase2_active_results:
            active_dataset_label = phase2_active_source
            active_target_label = active_target
        else:
            active_dataset_label = "Standardized baseline dataset"
            active_target_label = "Daily demand"

        st.markdown(
            f"""
            <div class="sf-dataset-strip">
              <div class="sf-dataset-heading">▤ &nbsp; Active Dataset</div>
              <div><span>DATA SOURCE</span><strong>{html.escape(str(active_dataset_label))}</strong></div>
              <div><span>DATE RANGE</span><strong>{actual_df['date'].min():%b %d, %Y} – {actual_df['date'].max():%b %d, %Y}</strong></div>
              <div><span>RECORDS</span><strong>{len(actual_df):,}</strong></div>
              <div><span>TARGET</span><strong>{html.escape(str(active_target_label))}</strong></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# =========================================================
# MODEL EVALUATION
# =========================================================
with tab_evaluation:
    if not phase2_active_results:
        render_no_active_dataset_state()
    else:
        st.subheader("Forecast Model Evaluation")
        st.caption("Compare all available models using metrics calculated from the active dataset.")

        metric_col1, metric_col2 = st.columns(2, gap="medium")

        with metric_col1:
            fig_mape = px.bar(
                ranking.sort_values("mape", ascending=True),
                x="model_name",
                y="mape",
                color="model_name",
                text="mape",
                title="Mean Absolute Percentage Error (MAPE)",
                labels={"model_name": "Forecasting Model", "mape": "MAPE (%)"},
                color_discrete_map={
                    "ARIMA": theme["blue"],
                    "SARIMA": theme["blue_light"],
                    "Prophet": theme["teal"],
                    "Random Forest": theme["gold"],
                },
            )
            fig_mape.update_traces(texttemplate="%{text:.2f}%", textposition="outside", cliponaxis=False)
            fig_mape.update_layout(showlegend=False)
            style_figure(fig_mape, 270)
            st.plotly_chart(add_chart_motion(fig_mape), use_container_width=True, config={"responsive": True, "displayModeBar": "hover", "scrollZoom": True})

        with metric_col2:
            fig_mae = px.bar(
                ranking.sort_values("mae", ascending=True),
                x="model_name",
                y="mae",
                color="model_name",
                text="mae",
                title="Mean Absolute Error (MAE)",
                labels={"model_name": "Forecasting Model", "mae": "MAE"},
                color_discrete_map={
                    "ARIMA": theme["blue"],
                    "SARIMA": theme["blue_light"],
                    "Prophet": theme["teal"],
                    "Random Forest": theme["gold"],
                },
            )
            fig_mae.update_traces(texttemplate="%{text:.2f}", textposition="outside", cliponaxis=False)
            fig_mae.update_layout(showlegend=False)
            style_figure(fig_mae, 270)
            st.plotly_chart(add_chart_motion(fig_mae), use_container_width=True, config={"responsive": True, "displayModeBar": "hover", "scrollZoom": True})

        st.subheader("Model Performance Summary")
        performance_display = performance.copy()
        performance_display["mae"] = performance_display["mae"].round(2)
        performance_display["mape"] = performance_display["mape"].round(2)
        st.dataframe(performance_display, use_container_width=True, hide_index=True)

       # 2023 VALIDATION PERFORMANCE
    st.subheader(
        f"Model Performance Ranking ({phase2_active_results['validation_year']} Validation)"
        if phase2_active_results else "Model Performance Ranking (2023 Validation)"
    )

    ranking_display = ranking.copy()

    for col in ["mae", "rmse", "mape", "wape"]:
        ranking_display[col] = ranking_display[col].round(3)

    st.dataframe(
        ranking_display,
        use_container_width=True,
        hide_index=True
    )

    # 2024 FINAL HOLDOUT PERFORMANCE
    st.subheader(
        f"{phase2_active_results['test_year']} Final Holdout Performance"
        if phase2_active_results else "2024 Final Holdout Performance"
    )

    st.caption(
        "Final test results are reported separately. "
        "These results are not used for model selection."
    )

    test_display = test_performance.copy()

    for col in ["mae", "rmse", "mape", "wape"]:
        test_display[col] = test_display[col].round(3)

    st.dataframe(
        test_display,
        use_container_width=True,
        hide_index=True
    )

    # FORECASTING APPROACH COMPARISON
    st.subheader("Forecasting Approach Comparison")

    st.caption(
        "Statistical and machine-learning approaches are compared "
        "using final-test performance metrics from the active dataset."
    )

       # 2024 FINAL TEST: FORECASTING APPROACH COMPARISON

    machine_learning_models = ["Random Forest"]
    time_series_models = ["ARIMA", "SARIMA", "Prophet"]

    machine_learning_results = test_performance[
        test_performance["model_name"].isin(machine_learning_models)
    ]

    time_series_results = test_performance[
        test_performance["model_name"].isin(time_series_models)
    ]

    approach_df = pd.DataFrame(
        {
            "Approach": [
                "Machine Learning Model",
                "Time Series Models",
            ],
            "mae": [
                machine_learning_results["mae"].mean(),
                time_series_results["mae"].mean(),
            ],
            "rmse": [
                machine_learning_results["rmse"].mean(),
                time_series_results["rmse"].mean(),
            ],
            "mape": [
                machine_learning_results["mape"].mean(),
                time_series_results["mape"].mean(),
            ],
            "wape": [
                machine_learning_results["wape"].mean(),
                time_series_results["wape"].mean(),
            ],
        }
    )

    approach_col1, approach_col2 = st.columns(2, gap="medium")
    with approach_col1:
        fig_approach_mape = px.bar(
            approach_df,
            x="Approach",
            y="mape",
            color="Approach",
            text="mape",
           title="Final-Test MAPE by Forecasting Approach",
            color_discrete_sequence=[theme["teal"], theme["blue"]],
    )
    fig_approach_mape.update_traces(texttemplate="%{text:.2f}%", textposition="outside", cliponaxis=False)
    fig_approach_mape.update_layout(showlegend=False)
    fig_approach_mape.update_xaxes(title_text="", tickfont=dict(size=10))
    fig_approach_mape.update_yaxes(title_text="MAPE (%)")
    style_figure(fig_approach_mape, 270)
    st.plotly_chart(add_chart_motion(fig_approach_mape), use_container_width=True, config={"responsive": True, "displayModeBar": "hover", "scrollZoom": True})

    with approach_col2:
        fig_approach_mae = px.bar(
            approach_df,
            x="Approach",
            y="mae",
            color="Approach",
            text="mae",
            title="Final-Test MAE by Forecasting Approach",
            color_discrete_sequence=[theme["teal"], theme["blue"]],
        )
        fig_approach_mae.update_traces(texttemplate="%{text:.2f}", textposition="outside", cliponaxis=False)
        fig_approach_mae.update_layout(showlegend=False)
        fig_approach_mae.update_xaxes(title_text="", tickfont=dict(size=10))
        fig_approach_mae.update_yaxes(title_text="MAE")
        style_figure(fig_approach_mae, 270)
        st.plotly_chart(add_chart_motion(fig_approach_mae), use_container_width=True, config={"responsive": True, "displayModeBar": "hover", "scrollZoom": True})

    st.info(
            "Interpretation: Models are ranked using validation WAPE. "
            "The final-test metrics are reported separately and are not used "
            "for model selection. All four models are compared using the same "
            "evaluation period and demand target."
        )

# =========================================================
# FORECAST ANALYSIS
# =========================================================
with tab_analysis:
    if not phase2_active_results:
        render_no_active_dataset_state()
    else:
        st.subheader(f"{selected_model} Forecast Analysis")
        st.caption("The selected model controls the forecast charts and forecast summary below." + (f" Active dataset: {phase2_active_source} · {active_target}." if phase2_active_results else " Showing standardized baseline results."))

        forecast_summary_cols = st.columns(3, gap="medium")
        with forecast_summary_cols[0]:
            st.metric("Average Forecast", f"{model_data['predicted_demand'].mean():,.2f}")
        with forecast_summary_cols[1]:
            st.metric("Highest Forecast", f"{model_data['predicted_demand'].max():,.2f}")
        with forecast_summary_cols[2]:
            st.metric("Lowest Forecast", f"{model_data['predicted_demand'].min():,.2f}")

        st.subheader("Actual Demand vs. Forecasted Demand")
        fig_compare = px.line(
            comparison,
            x="forecast_date",
            y=["daily_demand", "predicted_demand"],
            labels={"forecast_date": "Date", "value": "Demand", "variable": "Series"},
            title=f"{selected_model}: Actual vs. Forecast",
            color_discrete_map={
                "daily_demand": theme["blue"],
                "predicted_demand": theme["gold"],
            },
        )
        fig_compare.update_traces(line=dict(width=2))
        style_figure(fig_compare, 285)
        fig_compare.update_layout(showlegend=True)
        st.plotly_chart(add_chart_motion(fig_compare), use_container_width=True, config={"responsive": True, "displayModeBar": "hover", "scrollZoom": True})

        st.subheader("Monthly Historical Sales Trend")
        fig_month_analysis = px.line(
            monthly_sales,
            x="month",
            y="daily_demand",
            markers=True,
            title="Monthly Sales Demand",
            color_discrete_sequence=[theme["blue"]],
            labels={"month": "Month", "daily_demand": "Total Demand"},
        )
        style_figure(fig_month_analysis, 265)
        st.plotly_chart(add_chart_motion(fig_month_analysis), use_container_width=True, config={"responsive": True, "displayModeBar": "hover", "scrollZoom": True})

        st.subheader("Forecast Error Analysis")
        error_data = comparison.dropna(subset=["error"]).copy()
        fig_error = px.line(
            error_data,
            x="forecast_date",
            y="error",
            title=f"{selected_model}: Forecast Error (Actual − Predicted)",
            color_discrete_sequence=[theme["teal"]],
            labels={"forecast_date": "Date", "error": "Forecast Error"},
        )
        fig_error.add_hline(y=0, line_dash="dash", line_color=theme["muted"])
        style_figure(fig_error, 265)
        st.plotly_chart(add_chart_motion(fig_error), use_container_width=True, config={"responsive": True, "displayModeBar": "hover", "scrollZoom": True})

        st.subheader(f"{selected_model} Forecast Trend")
        fig_forecast = px.line(
            model_data,
            x="forecast_date",
            y="predicted_demand",
            title=f"{selected_model} Predicted Demand",
            color_discrete_sequence=[theme["gold"]],
            labels={"forecast_date": "Forecast Date", "predicted_demand": "Predicted Demand"},
        )
        fig_forecast.update_traces(line=dict(width=2.5))
        style_figure(fig_forecast, 265)
        st.plotly_chart(add_chart_motion(fig_forecast), use_container_width=True, config={"responsive": True, "displayModeBar": "hover", "scrollZoom": True})


    # =========================================================
# PHASE 2: AUTOMATIC FORECASTING WORKSPACE
# =========================================================
with tab_auto_forecast:
    st.subheader("Automatic Forecasting · Quantity and Revenue")
    st.caption(
        "Select a dataset already saved in Supabase, then run all four forecasting models "
        "for both daily Quantity_Sold and daily Total_Sales."
    )
    st.info(
        "The workflow follows the original forecasting notebook: transaction-level values "
        "are summed by date; the previous calendar year is used for validation; the latest "
        "calendar year is held out for final testing; and the best model for each target is "
        "selected using validation WAPE. Future forecasts are refitted using all available history."
    )

    try:
        available_uploads = list_supabase_datasets()
        upload_names = [
            item.get("name") for item in available_uploads
            if item.get("name") and not item.get("name", "").startswith(".")
        ]
    except Exception as list_error:
        upload_names = []
        st.error(f"Unable to retrieve saved datasets from Supabase: {list_error}")

    if not upload_names:
        st.warning("No saved upload was found. Save a CSV or XLSX file first in Downloads & Data.")
    else:
        selected_upload = st.selectbox(
            "Select saved dataset",
            options=sorted(upload_names, reverse=True),
            key="phase2_selected_dataset",
        )
        horizon = st.selectbox(
            "Future forecast horizon",
            options=[30, 60, 90],
            index=2,
            format_func=lambda days: f"{days} days",
            key="phase2_forecast_horizon",
        )
        st.caption(
            "Targets: Quantity Sold (units) and Total Sales (currency units) · "
            "Models: ARIMA, SARIMA, Prophet, and Random Forest."
        )

        if st.button(
            "Run Automatic Forecasting",
            type="primary",
            use_container_width=True,
            key="run_dual_target_forecasting",
        ):
            try:
                with st.status("Preparing dataset and training forecasting models...", expanded=True) as run_status:
                    file_bytes = download_supabase_dataset(selected_upload)
                    file_stream = io.BytesIO(file_bytes)
                    if selected_upload.lower().endswith(".csv"):
                        source_df = pd.read_csv(file_stream)
                    elif selected_upload.lower().endswith(".xlsx"):
                        source_df = pd.read_excel(file_stream)
                    else:
                        raise ValueError("Only saved CSV and XLSX datasets can be forecast.")

                    run_status.write(f"Loaded {len(source_df):,} transaction rows from {selected_upload}.")
                    progress_bar = st.progress(0, text="Starting 24 model runs...")

                    def update_forecast_progress(done, total, label):
                        progress_bar.progress(done / total, text=f"{done}/{total} model runs · {label}")
                        run_status.write(f"Completed {done}/{total}: {label}")

                    phase2_results = run_dual_target_forecasting(
                        source_df,
                        horizon,
                        progress_callback=update_forecast_progress,
                    )
                    run_zip = build_forecast_run_zip(phase2_results)
                    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid4().hex[:8]
                    stored_run_path = save_forecast_run_to_supabase(run_zip, run_id)
                    run_status.update(
                        label="Forecasting completed and results saved to Supabase.",
                        state="complete",
                        expanded=False,
                    )

                st.session_state["phase2_results"] = phase2_results
                st.session_state["phase2_archive"] = run_zip
                st.session_state["phase2_archive_name"] = f"dual_target_forecast_{run_id}.zip"
                st.session_state["phase2_storage_path"] = stored_run_path
                st.session_state["phase2_source_name"] = selected_upload
                st.session_state["phase2_run_id"] = run_id

                # Re-execute the app so every dashboard tab is rebuilt from this
                # newly completed run, rather than showing one stale render.
                st.rerun()
            except Exception as forecast_error:
                st.error(f"Automatic forecasting could not be completed: {forecast_error}")
                st.warning(
                    "No results were marked as complete. Review the dataset requirements and "
                    "the model error before rerunning. The original saved dataset is unchanged."
                )

    phase2_results = st.session_state.get("phase2_results")
    if phase2_results:
        st.divider()
        st.subheader("Forecasting Results")
        st.success(
            f"Completed for {st.session_state.get('phase2_source_name', 'selected dataset')}. "
            f"Validation: {phase2_results['validation_year']} · "
            f"Final holdout: {phase2_results['test_year']} · "
            f"Forecast origin: {pd.Timestamp(phase2_results['forecast_origin']).date()}"
        )
        st.caption(
            "Model selection is performed separately for each target using the lowest validation WAPE. "
            "Final-test metrics are reported independently and do not determine model selection."
        )

        best_display = phase2_results["best_models"].copy()
        best_cols = st.columns(2, gap="medium")
        for col, target in zip(best_cols, ["Quantity_Sold", "Total_Sales"]):
            row = best_display[best_display["Target"] == target]
            if not row.empty:
                with col:
                    label = "Best Quantity Model" if target == "Quantity_Sold" else "Best Revenue Model"
                    st.metric(label, row.iloc[0]["Selected_Model"], f"Validation WAPE: {row.iloc[0]['Validation_WAPE_Percent']:.2f}%")

        target_choice = st.radio(
            "View target",
            options=["Quantity_Sold", "Total_Sales"],
            format_func=lambda value: "Quantity Sold (units)" if value == "Quantity_Sold" else "Total Sales (currency units)",
            horizontal=True,
            key="phase2_result_target",
        )
        validation_view = phase2_results["validation_metrics"].query("Target == @target_choice").copy()
        test_view = phase2_results["test_metrics"].query("Target == @target_choice").copy()
        future_view = phase2_results["future_forecasts"].query("Target == @target_choice").copy()
        test_predictions_view = phase2_results["test_predictions"].query("Target == @target_choice").copy()

        metric_cols = st.columns(2, gap="medium")
        with metric_cols[0]:
            st.markdown(f"**{phase2_results['validation_year']} Validation Performance**")
            st.dataframe(
                validation_view[["Model", "MAE", "RMSE", "MAPE (%)", "WAPE (%)"]].round(3),
                use_container_width=True,
                hide_index=True,
            )
        with metric_cols[1]:
            st.markdown(f"**{phase2_results['test_year']} Final Holdout Performance**")
            st.dataframe(
                test_view[["Model", "MAE", "RMSE", "MAPE (%)", "WAPE (%)"]].round(3),
                use_container_width=True,
                hide_index=True,
            )

        st.subheader("Final Holdout · Actual vs Predicted")
        test_chart_data = test_predictions_view.melt(
            id_vars=["Date", "Model"],
            value_vars=["Actual", "Predicted"],
            var_name="Series",
            value_name="Value",
        )
        fig_test = px.line(
            test_chart_data,
            x="Date",
            y="Value",
            color="Series",
            line_dash="Model",
            title=f"{target_choice} · {phase2_results['test_year']} holdout",
            labels={"Value": "Daily value", "Date": "Date"},
        )
        fig_test.update_layout(legend_title_text="Series / Model")
        st.plotly_chart(add_chart_motion(fig_test), use_container_width=True)

        st.subheader(f"Next {phase2_results['horizon']} Days · Forecast by Model")
        fig_future = px.line(
            future_view,
            x="Forecast_Date",
            y="Predicted_Value",
            color="Model",
            title=f"Future {target_choice} forecast",
            labels={"Forecast_Date": "Forecast date", "Predicted_Value": "Predicted value"},
        )
        st.plotly_chart(add_chart_motion(fig_future), use_container_width=True)
        st.dataframe(
            future_view[["Forecast_Date", "Model", "Predicted_Value"]].round(2),
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Download complete forecasting results (ZIP)",
            data=st.session_state["phase2_archive"],
            file_name=st.session_state["phase2_archive_name"],
            mime="application/zip",
            type="primary",
            key="download_phase2_results_zip",
        )
        st.caption(f"Persistent results location: {st.session_state['phase2_storage_path']}")


# =========================================================
# LIVE DATASET STUDIO — charts are driven by the latest completed upload run
# =========================================================
with tab_live_dataset:
    st.markdown(
        """
        <div style="padding:26px 28px;border-radius:18px;background:linear-gradient(120deg,#102A43,#145B68);color:#F4FAFC;margin-bottom:18px;">
          <div style="font-size:11px;letter-spacing:2.2px;font-weight:700;color:#8CE0D0;">DATASET-DRIVEN WORKSPACE</div>
          <div style="font-size:28px;font-weight:800;line-height:1.2;margin-top:8px;">Live Dataset Studio</div>
          <div style="font-size:13px;color:#D5E8ED;margin-top:7px;">A separate view built from the dataset used in your latest completed forecasting run.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    live_results = st.session_state.get("phase2_results")
    live_source_name = st.session_state.get("phase2_source_name")

    if not live_results:
        st.info(
            "Wala pang completed upload run. Pumunta sa Downloads & Data para mag-upload, "
            "pagkatapos ay buksan ang Automatic Forecasting at patakbuhin ang forecast. "
            "Dito lalabas ang charts mula mismo sa napiling dataset."
        )
    else:
        live_daily = live_results["daily"].copy()
        live_daily["Date"] = pd.to_datetime(live_daily["Date"], errors="coerce")
        live_daily["Quantity_Sold"] = pd.to_numeric(live_daily["Quantity_Sold"], errors="coerce")
        live_daily["Total_Sales"] = pd.to_numeric(live_daily["Total_Sales"], errors="coerce")
        live_daily = live_daily.dropna(subset=["Date"]).sort_values("Date")

        st.markdown(
            f"""
            <div style="padding:12px 16px;border-left:4px solid #19A7A1;background:rgba(25,167,161,.10);border-radius:8px;margin-bottom:16px;">
              <div style="font-size:10px;letter-spacing:1.4px;font-weight:700;opacity:.75;">ACTIVE DATASET</div>
              <div style="font-size:16px;font-weight:750;margin-top:3px;">{html.escape(str(live_source_name or "Uploaded dataset"))}</div>
              <div style="font-size:11px;opacity:.75;margin-top:4px;">{len(live_daily):,} daily records · {live_daily['Date'].min():%b %d, %Y} – {live_daily['Date'].max():%b %d, %Y}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        live_total_qty = live_daily["Quantity_Sold"].sum()
        live_total_sales = live_daily["Total_Sales"].sum()
        live_avg_sales = live_daily["Total_Sales"].mean()
        live_peak_day = live_daily.loc[live_daily["Total_Sales"].idxmax()]

        live_kpis = st.columns(4, gap="medium")
        live_kpis[0].metric("Total Units Sold", f"{live_total_qty:,.0f}")
        live_kpis[1].metric("Total Revenue", f"{live_total_sales:,.2f}")
        live_kpis[2].metric("Average Daily Revenue", f"{live_avg_sales:,.2f}")
        live_kpis[3].metric("Highest Revenue Day", f"{live_peak_day['Total_Sales']:,.2f}", help=str(live_peak_day["Date"].date()))

        live_left, live_right = st.columns([1.35, 1], gap="large")
        with live_left:
            st.markdown("#### Revenue movement")
            live_revenue_fig = px.area(
                live_daily,
                x="Date",
                y="Total_Sales",
                title="Daily revenue from uploaded dataset",
                color_discrete_sequence=["#13A89E"],
            )
            live_revenue_fig.update_traces(
                line=dict(width=2.5, color="#087F8C"),
                fillcolor="rgba(19,168,158,.18)",
                mode="lines",
            )
            live_revenue_fig.update_layout(
                template="plotly_white",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(247,250,252,1)",
                margin=dict(l=12, r=12, t=55, b=12),
                height=370,
                hovermode="x unified",
            )
            st.plotly_chart(add_chart_motion(live_revenue_fig), use_container_width=True, key="live_dataset_revenue_chart")

        with live_right:
            st.markdown("#### Units sold")
            live_qty_fig = px.bar(
                live_daily,
                x="Date",
                y="Quantity_Sold",
                title="Daily quantity sold",
                color_discrete_sequence=["#3157A4"],
            )
            live_qty_fig.update_traces(marker_line_width=0, opacity=.88)
            live_qty_fig.update_layout(
                template="plotly_white",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(247,250,252,1)",
                margin=dict(l=12, r=12, t=55, b=12),
                height=370,
                hovermode="x unified",
            )
            st.plotly_chart(add_chart_motion(live_qty_fig), use_container_width=True, key="live_dataset_quantity_chart")

        st.markdown("#### Revenue and quantity by month")
        live_monthly = (
            live_daily.set_index("Date")[["Quantity_Sold", "Total_Sales"]]
            .resample("MS").sum().reset_index()
        )
        monthly_qty_col, monthly_revenue_col = st.columns(2, gap="large")
        with monthly_qty_col:
            live_month_qty_fig = px.bar(
                live_monthly,
                x="Date",
                y="Quantity_Sold",
                title="Monthly quantity sold",
                color_discrete_sequence=["#3157A4"],
            )
            live_month_qty_fig.update_layout(
                template="plotly_white",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(247,250,252,1)",
                margin=dict(l=12, r=12, t=55, b=12),
                height=340,
            )
            st.plotly_chart(add_chart_motion(live_month_qty_fig), use_container_width=True, key="live_dataset_monthly_qty_chart")
        with monthly_revenue_col:
            live_month_revenue_fig = px.bar(
                live_monthly,
                x="Date",
                y="Total_Sales",
                title="Monthly revenue",
                color_discrete_sequence=["#13A89E"],
            )
            live_month_revenue_fig.update_layout(
                template="plotly_white",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(247,250,252,1)",
                margin=dict(l=12, r=12, t=55, b=12),
                height=340,
            )
            st.plotly_chart(add_chart_motion(live_month_revenue_fig), use_container_width=True, key="live_dataset_monthly_revenue_chart")

        with st.expander("Inspect the exact daily data used by these graphs"):
            st.dataframe(live_daily, use_container_width=True, hide_index=True)

        st.caption(
            "All figures above are calculated from the latest completed uploaded dataset run. "
            "Upload another dataset and run forecasting again to replace this view with its values."
        )


# =========================================================
# DOWNLOADS AND DATA
# =========================================================
with tab_downloads:
    st.subheader("Upload Dataset to Cloud Storage")
    st.caption(
        "Upload a CSV or Excel dataset directly from this page. "
        "The original file is saved in your private Supabase Storage bucket "
        "so it remains available after the Streamlit app restarts."
    )

    uploaded_dataset = st.file_uploader(
        "Choose a sales dataset",
        type=["csv", "xlsx"],
        help="Maximum file size: 50 MB. The original file is stored without changing it.",
        key="supabase_dataset_uploader",
    )

    if uploaded_dataset is not None:
        try:
            uploaded_bytes, uploaded_preview = parse_uploaded_dataset(uploaded_dataset)
            upload_info_cols = st.columns(3)
            upload_info_cols[0].metric("File size", f"{len(uploaded_bytes) / 1024:.1f} KB")
            upload_info_cols[1].metric("Preview rows", f"{len(uploaded_preview):,}")
            upload_info_cols[2].metric("Columns", f"{len(uploaded_preview.columns):,}")

            with st.expander("Preview uploaded dataset", expanded=True):
                st.dataframe(uploaded_preview, use_container_width=True, hide_index=True)

            if len(uploaded_bytes) > MAX_UPLOAD_BYTES:
                st.error("This file exceeds the current 50 MB upload limit. Reduce the file size and try again.")
            elif st.button(
                "Save dataset to Supabase",
                type="primary",
                use_container_width=False,
                key="save_dataset_to_supabase",
            ):
                try:
                    with st.spinner("Saving dataset to Supabase Storage..."):
                        saved_object_path = upload_dataset_to_supabase(
                            uploaded_dataset, uploaded_bytes
                        )
                    st.success("Dataset saved successfully to Supabase Storage.")
                    st.code(saved_object_path, language="text")
                    st.caption(
                        "Your original file is now stored persistently. "
                        "To generate forecasts from this uploaded dataset, open the "
                        "Automatic Forecasting tab and run the dual-target workflow."
                    )
                except Exception as upload_error:
                    st.error(f"Upload failed: {upload_error}")
                    st.info(
                        "Check that the bucket name is exactly 'sales-datasets', "
                        "the bucket is private, and Streamlit Secrets contains a valid "
                        "server-side Supabase secret key."
                    )
        except Exception as preview_error:
            st.error(f"Unable to read this dataset: {preview_error}")

    st.divider()
    st.subheader("Saved Datasets")
    st.caption("Files saved in the private Supabase bucket are listed here.")

    if st.button("Refresh saved datasets", key="refresh_supabase_datasets"):
        st.cache_resource.clear()
        st.rerun()

    try:
        stored_objects = list_supabase_datasets()
        stored_objects = [
            item for item in stored_objects
            if item.get("name") and item.get("name") not in {".", ".."}
        ]

        if not stored_objects:
            st.info("No uploaded datasets found yet. Upload a CSV or Excel file above.")
        else:
            for stored_item in sorted(
                stored_objects,
                key=lambda item: item.get("created_at") or item.get("updated_at") or "",
                reverse=True,
            ):
                object_name = stored_item["name"]
                object_path = f"uploads/{object_name}"
                file_col, action_col = st.columns([4, 1])
                with file_col:
                    st.markdown(f"**{html.escape(object_name)}**")
                    metadata = stored_item.get("metadata") or {}
                    size_bytes = metadata.get("size")
                    if size_bytes is not None:
                        st.caption(f"{int(size_bytes) / 1024:.1f} KB · {object_path}")
                    else:
                        st.caption(object_path)
                with action_col:
                    try:
                        file_content = download_supabase_dataset(object_name)
                        st.download_button(
                            "Download",
                            data=file_content,
                            file_name=object_name,
                            mime="application/octet-stream",
                            key=f"download_supabase_{object_name}",
                            use_container_width=True,
                        )
                    except Exception as download_error:
                        st.warning(f"Download unavailable: {download_error}")

                    if st.button(
                        "Delete",
                        key=f"request_delete_supabase_{object_name}",
                        use_container_width=True,
                        type="secondary",
                    ):
                        st.session_state["pending_dataset_delete"] = object_name
                        st.rerun()

                if st.session_state.get("pending_dataset_delete") == object_name:
                    st.warning(
                        f"Are you sure you want to permanently delete **{object_name}** "
                        "from Supabase Storage? This cannot be undone."
                    )
                    confirm_col, cancel_col = st.columns(2, gap="small")
                    with confirm_col:
                        if st.button(
                            "Yes, delete permanently",
                            key=f"confirm_delete_supabase_{object_name}",
                            type="primary",
                            use_container_width=True,
                        ):
                            try:
                                delete_supabase_dataset(object_name)

                                # If this file powers the active dashboard, clear its
                                # in-memory results so charts disappear immediately.
                                if st.session_state.get("phase2_source_name") == object_name:
                                    for state_key in (
                                        "phase2_results",
                                        "phase2_archive",
                                        "phase2_archive_name",
                                        "phase2_storage_path",
                                        "phase2_source_name",
                                        "phase2_run_id",
                                    ):
                                        st.session_state.pop(state_key, None)
                                    st.session_state.pop("unified_dashboard_target", None)
                                    st.session_state.pop("phase2_result_target", None)

                                st.session_state.pop("pending_dataset_delete", None)
                                st.success(f"Deleted {object_name} from Supabase Storage.")
                                st.rerun()
                            except Exception as delete_error:
                                st.error(f"Could not delete dataset: {delete_error}")
                    with cancel_col:
                        if st.button(
                            "Cancel",
                            key=f"cancel_delete_supabase_{object_name}",
                            use_container_width=True,
                        ):
                            st.session_state.pop("pending_dataset_delete", None)
                            st.rerun()
    except Exception as storage_error:
        st.warning(f"Could not retrieve saved datasets: {storage_error}")
        st.caption(
            "Verify the Supabase URL, server-side secret key, bucket name, "
            "and Storage permissions."
        )

    st.divider()
    st.subheader("Download Forecast Results")
    st.caption("Export the selected model, all forecast records, or the model-ranking report.")

    selected_csv = model_data.to_csv(index=False).encode("utf-8")
    all_csv = df.to_csv(index=False).encode("utf-8")
    ranking_csv = ranking.to_csv(index=False).encode("utf-8")
    actual_csv = actual_df.to_csv(index=False).encode("utf-8")

    download_cols = st.columns(4, gap="medium")

    with download_cols[0]:
        st.download_button("Selected Forecast CSV", selected_csv, file_name=f"{selected_model.lower().replace(' ', '_')}_forecast.csv", mime="text/csv", use_container_width=True)
    with download_cols[1]:
        st.download_button("All Forecast Results", all_csv, file_name="all_forecast_results.csv", mime="text/csv", use_container_width=True)
    with download_cols[2]:
        st.download_button("Model Ranking Report", ranking_csv, file_name="model_ranking_report.csv", mime="text/csv", use_container_width=True)
    with download_cols[3]:
        st.download_button("Historical Sales Data", actual_csv, file_name="daily_sales_clean.csv", mime="text/csv", use_container_width=True)
    st.divider()

    st.subheader("Dataset-Driven DSS Exports")

    if phase2_active_results:
        st.caption(
            f"These exports are generated from the latest completed upload: "
            f"{phase2_active_source}. Daily data, validation, holdout, and future "
            "forecast files include both Quantity_Sold and Total_Sales targets."
        )
        active_export_files = {
            "Daily Quantity & Sales Data": (
                "daily_quantity_and_sales.csv",
                phase2_active_results["daily"],
            ),
            "Validation Metrics (Both Targets)": (
                "validation_metrics.csv",
                phase2_active_results["validation_metrics"],
            ),
            "Final Holdout Metrics (Both Targets)": (
                "final_test_metrics.csv",
                phase2_active_results["test_metrics"],
            ),
            "Validation Predictions (Both Targets)": (
                "validation_predictions.csv",
                phase2_active_results["validation_predictions"],
            ),
            "Final Holdout Predictions (Both Targets)": (
                "final_test_predictions.csv",
                phase2_active_results["test_predictions"],
            ),
            "Future Forecasts (Both Targets)": (
                "future_forecasts.csv",
                phase2_active_results["future_forecasts"],
            ),
            "Selected Models (Both Targets)": (
                "selected_models.csv",
                phase2_active_results["best_models"],
            ),
        }
        export_files = [
            (label, filename, frame.to_csv(index=False).encode("utf-8"))
            for label, (filename, frame) in active_export_files.items()
        ]
    else:
        st.caption(
            "No completed upload run is active yet. These downloads show the "
            "repository's standardized baseline data. Run Automatic Forecasting "
            "to switch these exports to the latest uploaded dataset."
        )
        baseline_exports = [
            ("Daily Demand Data", "aggregated_daily_demand.csv"),
            ("2023 Validation Metrics", "validation_model_performance.csv"),
            ("2024 Test Metrics", "test_model_performance_2024.csv"),
            ("2023 Validation Forecasts", "validation_forecasts_2023.csv"),
            ("2024 Test Forecasts", "test_forecasts_2024.csv"),
            ("Future Forecasts", "future_forecasts.csv"),
            ("Model Selection Summary", "model_selection_summary.csv"),
        ]
        export_files = [
            (label, filename, (DATA_DIR / filename).read_bytes())
            for label, filename in baseline_exports
        ]

    for start in range(0, len(export_files), 2):
        cols = st.columns(2, gap="medium")
        for col, (label, filename, file_data) in zip(cols, export_files[start:start + 2]):
            with col:
                st.download_button(
                    label,
                    data=file_data,
                    file_name=filename,
                    mime="text/csv",
                    use_container_width=True,
                    key=f"dss_export_{filename}",
                )
    st.divider()
    st.subheader("Forecast Data")
    st.caption(f"Saved forecast records for the selected model: {selected_model}.")
    st.dataframe(model_data, use_container_width=True, hide_index=True)

    with st.expander("View Historical Sales Dataset"):
        st.dataframe(actual_df, use_container_width=True, hide_index=True)


# =========================================================
# FOOTER
# =========================================================
st.divider()
st.markdown(
    """
    <div style="text-align:center;font-size:0.76rem;padding:18px 0 8px 0;">
        STA. CRUZ LAGUNA SALES FORECASTING SYSTEM · PYTHON + STREAMLIT
    </div>
    """,
    unsafe_allow_html=True,
)
