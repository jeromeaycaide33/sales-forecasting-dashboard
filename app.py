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
    "page": "#101B17",
    "page_grad_1": "#172820",
    "page_grad_2": "#0B1411",
    "sidebar": "#111F19",
    "hero": "#1B342A",
    "hero2": "#294B3B",
    "panel": "#172A21",
    "panel_alt": "#20382C",
    "panel_soft": "#1A3025",
    "border": "#3B5D49",
    "tab_bg": "#172A21",
    "tab_active": "#28513E",
    "tab_text": "#D8E5D9",
    "tab_active_border": "#55C49A",
    "text": "#F1F4EA",
    "muted": "#B0C0B3",
    "blue": "#4FC49A",
    "blue_light": "#A4E2C5",
    "teal": "#D18B5D",
    "gold": "#E5BE72",
    "success_bg": "#18392D",
    "success_border": "#438D6D",
    "success_text": "#DDF4E7",
    "table_header": "#294336",
}

LIGHT_THEME = {
    "name": "light",
    "page": "#F3F0E7",
    "page_grad_1": "#F8F6EF",
    "page_grad_2": "#EAE7DC",
    "sidebar": "#E4E6D9",
    "hero": "#FFFEF8",
    "hero2": "#E8F0E7",
    "panel": "#FFFEF9",
    "panel_alt": "#F4F5EC",
    "panel_soft": "#EAF0E8",
    "border": "#D0D9CB",
    "tab_bg": "#FFFEF9",
    "tab_active": "#DCECE1",
    "tab_text": "#40564A",
    "tab_active_border": "#218A67",
    "text": "#26382E",
    "muted": "#68796D",
    "blue": "#178765",
    "blue_light": "#55A989",
    "teal": "#B96F49",
    "gold": "#C69A4B",
    "success_bg": "#E7F3E9",
    "success_border": "#B8D8C0",
    "success_text": "#315D42",
    "table_header": "#E6EDE3",
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

# =========================================================
# GLOBAL GLASSMORPHISM UI — PRESENTATION ONLY
# Applied on both landing page and dashboard.
# =========================================================
st.markdown(
    """
    <style>
    /* =====================================================
       GLASSMORPHISM REDESIGN — CSS ONLY
       No Python functions, calculations, model logic, storage,
       widget keys, navigation, or callbacks are changed.
       ===================================================== */
    :root {
        --glass-border: rgba(151, 194, 245, .24);
        --glass-shadow: 0 18px 48px rgba(0, 0, 0, .28);
        --glass-bg: rgba(13, 31, 55, .68);
    }
    .stApp {
        background:
          radial-gradient(ellipse at 12% 7%, rgba(37, 112, 220, .28), transparent 34%),
          radial-gradient(ellipse at 88% 18%, rgba(24, 170, 190, .15), transparent 30%),
          linear-gradient(135deg, #050D1B 0%, #0A1C34 52%, #071326 100%) !important;
        background-attachment: fixed !important;
    }
    [data-testid="stAppViewContainer"] {
        background: transparent !important;
    }
    [data-testid="stHeader"] {
        background: rgba(5, 15, 30, .48) !important;
        backdrop-filter: blur(18px);
    }
    [data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(180deg, rgba(10, 28, 51, .94), rgba(5, 16, 31, .88)) !important;
        border-right: 1px solid var(--glass-border) !important;
        backdrop-filter: blur(24px) saturate(150%) !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stMetric"],
    [data-testid="stExpander"],
    [data-testid="stAlert"],
    .sf-hero, .sf-landing-hero, .sf-preview-card, .sf-feature,
    .sf-metric-row {
        background: linear-gradient(145deg, rgba(27, 54, 85, .76), rgba(9, 25, 46, .70)) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 20px !important;
        box-shadow: var(--glass-shadow) !important;
        backdrop-filter: blur(20px) saturate(145%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(145%) !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        transition: border-color .18s ease, transform .18s ease, box-shadow .18s ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: rgba(99, 174, 255, .52) !important;
        box-shadow: 0 22px 54px rgba(0, 0, 0, .34) !important;
    }
    [data-testid="stMetric"] { padding: 17px !important; }
    [data-testid="stTabs"] [role="tablist"] {
        gap: 8px !important; padding: 7px !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 17px !important;
        background: rgba(7, 22, 41, .68) !important;
        backdrop-filter: blur(16px) !important;
    }
    [data-testid="stTabs"] button[role="tab"] {
        border: 1px solid transparent !important; border-radius: 12px !important;
        background: transparent !important; transition: all .18s ease;
    }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, rgba(44, 126, 230, .42), rgba(25, 76, 139, .34)) !important;
        border: 1px solid rgba(112, 183, 255, .48) !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,.10), 0 7px 22px rgba(0,0,0,.18) !important;
    }
    [data-baseweb="select"] > div, [data-baseweb="input"] > div,
    [data-baseweb="textarea"] > div, [data-testid="stFileUploader"] section {
        background: rgba(9, 27, 49, .78) !important;
        border: 1px solid rgba(143, 187, 239, .30) !important;
        border-radius: 13px !important;
        backdrop-filter: blur(12px) !important;
    }
    .stButton button, [data-testid="stDownloadButton"] button,
    [data-testid="stFormSubmitButton"] button {
        border: 1px solid rgba(117, 181, 250, .48) !important;
        border-radius: 13px !important;
        background: linear-gradient(135deg, rgba(43, 119, 213, .88), rgba(24, 73, 135, .88)) !important;
        color: #F4F8FF !important;
        box-shadow: 0 9px 24px rgba(0, 0, 0, .22), inset 0 1px 0 rgba(255,255,255,.13) !important;
        transition: transform .18s ease, filter .18s ease !important;
    }
    .stButton button:hover, [data-testid="stDownloadButton"] button:hover {
        filter: brightness(1.16) !important; transform: translateY(-2px) !important;
    }
    [data-testid="stDataFrame"], [data-testid="stTable"],
    [data-testid="stPlotlyChart"] {
        border: 1px solid rgba(143, 187, 239, .20) !important;
        border-radius: 16px !important;
        overflow: hidden !important;
        box-shadow: 0 12px 32px rgba(0,0,0,.18) !important;
    }
    hr { border-color: rgba(143, 187, 239, .20) !important; }
    h1, h2, h3 { letter-spacing: -.025em; }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after { transition-duration: .01ms !important; animation-duration: .01ms !important; }
    }


    /* Ensure the dashboard's main content surfaces read as frosted glass. */
    [data-testid="stMain"] .block-container {
        position: relative;
        z-index: 1;
    }
    [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stMetric"],
    [data-testid="stExpander"] details,
    [data-testid="stAlert"] {
        background: rgba(15, 35, 61, .66) !important;
        border: 1px solid rgba(151, 194, 245, .28) !important;
        border-radius: 18px !important;
        box-shadow: 0 14px 38px rgba(0, 0, 0, .22), inset 0 1px 0 rgba(255,255,255,.05) !important;
        backdrop-filter: blur(18px) saturate(145%) !important;
        -webkit-backdrop-filter: blur(18px) saturate(145%) !important;
    }
    [data-testid="stPlotlyChart"] > div {
        background: rgba(12, 29, 51, .52) !important;
        border: 1px solid rgba(143, 187, 239, .24) !important;
        border-radius: 17px !important;
        padding: 8px !important;
        box-shadow: 0 12px 32px rgba(0,0,0,.18) !important;
        backdrop-filter: blur(14px) !important;
    }
    [data-testid="stDataFrame"], [data-testid="stTable"] {
        background: rgba(12, 29, 51, .55) !important;
        border: 1px solid rgba(143, 187, 239, .26) !important;
        border-radius: 15px !important;
        overflow: hidden !important;
        box-shadow: 0 12px 30px rgba(0,0,0,.17) !important;
    }
    [data-testid="stTabs"] [role="tablist"] {
        background: rgba(9, 26, 47, .62) !important;
        border: 1px solid rgba(151, 194, 245, .24) !important;
        border-radius: 16px !important;
        padding: 7px !important;
        backdrop-filter: blur(16px) !important;
    }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background: rgba(47, 121, 213, .35) !important;
        border: 1px solid rgba(112, 183, 255, .52) !important;
        border-radius: 11px !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        background: linear-gradient(180deg, rgba(10, 28, 51, .92), rgba(5, 16, 31, .90)) !important;
        border-right: 1px solid rgba(151, 194, 245, .24) !important;
        backdrop-filter: blur(22px) saturate(150%) !important;
    }
    [data-baseweb="select"] > div,
    [data-baseweb="input"] > div,
    [data-baseweb="textarea"] > div {
        background: rgba(9, 27, 49, .78) !important;
        border: 1px solid rgba(143, 187, 239, .32) !important;
        border-radius: 12px !important;
    }
    .stButton button, [data-testid="stDownloadButton"] button,
    [data-testid="stFormSubmitButton"] button {
        border: 1px solid rgba(117, 181, 250, .50) !important;
        border-radius: 12px !important;
        background: linear-gradient(135deg, rgba(43, 119, 213, .90), rgba(24, 73, 135, .90)) !important;
        color: #F4F8FF !important;
        box-shadow: 0 8px 22px rgba(0,0,0,.20), inset 0 1px 0 rgba(255,255,255,.12) !important;
    }
    .stButton button:hover, [data-testid="stDownloadButton"] button:hover {
        filter: brightness(1.12) !important;
        transform: translateY(-1px) !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Landing-page-only visual styling.
if not st.session_state.show_dashboard:
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] {display: none !important;}
        .block-container {max-width: 1440px !important; padding-top: 1.65rem !important;}
        .sf-landing-wrap {max-width: 1380px; margin: 0 auto;}
        .sf-brand {color:#75B5FF; font-size:.72rem; font-weight:850;
            letter-spacing:.19em; text-transform:uppercase;}
        .sf-top-note {color:var(--muted);font-size:.72rem;letter-spacing:.08em;}
        .sf-landing-hero {
            position:relative; overflow:hidden; display:grid;
            grid-template-columns:1.08fr .92fr; gap:clamp(24px,4vw,58px);
            align-items:center; padding:clamp(28px,5vw,66px);
            border-radius:24px; border:1px solid #285080;
            background:radial-gradient(circle at 90% 8%,rgba(57,139,255,.23),transparent 32%),
                       linear-gradient(120deg,#0B1C34 0%,#10294A 58%,#102442 100%);
            box-shadow:0 22px 60px rgba(0,0,0,.28);
        }
        .sf-landing-hero:before {content:"";position:absolute;width:390px;height:390px;
            right:-185px;top:-235px;border:1px solid rgba(105,173,255,.34);
            border-radius:50%;box-shadow:0 0 0 28px rgba(57,139,255,.055),
            0 0 0 62px rgba(57,139,255,.035);pointer-events:none;}
        .sf-landing-copy-wrap {position:relative;z-index:1;}
        .sf-landing-kicker {display:inline-flex;align-items:center;gap:8px;
            color:#8CC4FF;font-size:.7rem;font-weight:850;letter-spacing:.19em;
            text-transform:uppercase;margin-bottom:1.15rem;}
        .sf-kicker-dot {width:7px;height:7px;border-radius:50%;background:#398BFF;
            box-shadow:0 0 14px #398BFF;display:inline-block;}
        .sf-landing-title {color:#F4F8FF;font-size:clamp(2.25rem,4.7vw,4.35rem);
            line-height:1.035;letter-spacing:-.052em;font-weight:880;
            margin:0;max-width:720px;}
        .sf-landing-title span {color:#69AEFF;}
        .sf-landing-copy {color:#B8CBE2;font-size:1rem;line-height:1.8;
            max-width:650px;margin:1.25rem 0 1.45rem 0;}
        .sf-landing-points {display:flex;gap:10px 18px;flex-wrap:wrap;
            color:#D0DDF0;font-size:.76rem;}
        .sf-landing-points span:before {content:"✓";color:#65CDB5;font-weight:900;margin-right:7px;}
        .sf-preview-card {position:relative;z-index:1;padding:22px;border-radius:19px;
            border:1px solid rgba(115,169,226,.32);
            background:linear-gradient(155deg,rgba(12,31,55,.96),rgba(8,22,41,.97));
            box-shadow:0 18px 44px rgba(0,0,0,.3);}
        .sf-preview-top {display:flex;justify-content:space-between;align-items:center;
            gap:10px;color:#9DB6D4;font-size:.66rem;font-weight:800;letter-spacing:.12em;}
        .sf-live-pill {padding:5px 9px;border-radius:20px;color:#9CE5D4;
            background:rgba(45,181,147,.12);border:1px solid rgba(83,204,171,.25);
            letter-spacing:.06em;font-size:.61rem;white-space:nowrap;}
        .sf-preview-heading {color:#F2F7FF;font-size:1.25rem;font-weight:800;
            margin:18px 0 3px 0;}
        .sf-preview-sub {color:#91A9C5;font-size:.72rem;}
        .sf-preview-kpis {display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin:20px 0 17px;}
        .sf-preview-kpi {padding:11px 10px;border:1px solid rgba(112,157,207,.2);
            border-radius:11px;background:rgba(31,62,98,.34);}
        .sf-preview-kpi-label {color:#9DB4D0;font-size:.61rem;line-height:1.4;}
        .sf-preview-kpi-value {color:#F3F8FF;font-size:.92rem;font-weight:850;margin-top:5px;}
        .sf-chart-shell {border:1px solid rgba(112,157,207,.18);border-radius:13px;
            background:rgba(7,19,35,.52);padding:13px 13px 10px;}
        .sf-chart-label {display:flex;justify-content:space-between;gap:8px;
            color:#A9BED8;font-size:.64rem;font-weight:750;letter-spacing:.08em;}
        .sf-chart {height:112px;display:flex;align-items:flex-end;gap:7px;
            padding:12px 2px 0;border-bottom:1px solid rgba(126,164,207,.25);
            background:repeating-linear-gradient(to bottom,transparent 0,transparent 27px,rgba(123,158,197,.09) 28px);}
        .sf-chart span {flex:1;min-width:5px;border-radius:4px 4px 0 0;
            background:linear-gradient(180deg,#75B5FF 0%,#2878E8 100%);
            box-shadow:0 0 13px rgba(57,139,255,.14);opacity:.95;}
        .sf-chart-legend {display:flex;justify-content:space-between;color:#829BB8;
            font-size:.61rem;margin-top:9px;}
        .sf-model-tags {display:flex;flex-wrap:wrap;gap:6px;margin-top:15px;}
        .sf-model-tags span {font-size:.61rem;color:#B8CBE2;padding:5px 8px;
            border:1px solid rgba(117,165,219,.22);border-radius:6px;background:rgba(36,68,105,.35);}
        .sf-section-heading {font-size:1.35rem;font-weight:850;color:var(--text);
            margin:2.25rem 0 .35rem 0;letter-spacing:-.02em;}
        .sf-section-copy {color:var(--muted);font-size:.87rem;margin-bottom:1rem;line-height:1.6;}
        .sf-feature {height:100%;min-height:165px;padding:21px;border-radius:15px;
            border:1px solid var(--border);background:linear-gradient(150deg,var(--panel),var(--panel-soft));
            box-shadow:0 7px 22px rgba(0,0,0,.09);}
        .sf-feature-icon {width:42px;height:42px;display:flex;align-items:center;justify-content:center;
            border-radius:12px;background:rgba(57,139,255,.13);border:1px solid rgba(57,139,255,.22);
            font-size:1.25rem;margin-bottom:14px;}
        .sf-feature-title {color:var(--text);font-weight:850;font-size:.98rem;margin-bottom:7px;}
        .sf-feature-copy {color:var(--muted);font-size:.79rem;line-height:1.65;}
        .sf-landing-cta-note {color:var(--muted);font-size:.76rem;line-height:1.6;padding-top:7px;}
        .sf-footer {text-align:center;color:var(--muted);font-size:.68rem;
            letter-spacing:.08em;padding:15px 0 8px;}
        div[data-testid="stButton"] button[kind="primary"] {
            background:linear-gradient(110deg,#2878E8,#398BFF) !important;
            border:1px solid #69AEFF !important;color:white !important;
            box-shadow:0 8px 24px rgba(40,120,232,.24) !important;}
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


        </style>
        """,
        unsafe_allow_html=True,
    )

# =========================================================
# FOREST + SAND GLASS UI — GLOBAL PRESENTATION OVERRIDES
# CSS-only layer: keeps all existing Python logic and widgets intact.
# =========================================================
st.markdown(
    """
    <style>
    :root {
      --forest-accent: var(--blue);
      --forest-accent-soft: var(--blue-light);
      --forest-copper: var(--teal);
      --forest-gold: var(--gold);
      --forest-glass: color-mix(in srgb, var(--panel) 78%, transparent);
      --forest-glass-strong: color-mix(in srgb, var(--panel-alt) 88%, transparent);
      --forest-line: color-mix(in srgb, var(--border) 78%, transparent);
    }
    .stApp {
      background:
        radial-gradient(ellipse at 10% 0%, color-mix(in srgb, var(--blue) 17%, transparent), transparent 34%),
        radial-gradient(ellipse at 92% 12%, color-mix(in srgb, var(--teal) 13%, transparent), transparent 30%),
        linear-gradient(135deg, var(--page-grad-1), var(--page-grad-2)) !important;
      background-attachment: fixed !important;
      color: var(--text) !important;
    }
    [data-testid="stAppViewContainer"], [data-testid="stMain"] { background: transparent !important; }
    [data-testid="stHeader"] {
      background: color-mix(in srgb, var(--page) 74%, transparent) !important;
      backdrop-filter: blur(20px) saturate(145%) !important;
    }
    [data-testid="stSidebar"] > div:first-child {
      background: linear-gradient(165deg, color-mix(in srgb, var(--sidebar) 94%, transparent), color-mix(in srgb, var(--panel) 88%, transparent)) !important;
      border-right: 1px solid var(--forest-line) !important;
      box-shadow: 12px 0 36px rgba(0,0,0,.10) !important;
      backdrop-filter: blur(26px) saturate(150%) !important;
    }
    .sf-hero, .sf-landing-hero {
      background:
        radial-gradient(circle at 92% 8%, color-mix(in srgb, var(--blue) 18%, transparent), transparent 32%),
        linear-gradient(125deg, var(--hero), var(--hero2)) !important;
      border: 1px solid var(--forest-line) !important;
      border-radius: 24px !important;
      box-shadow: 0 22px 55px rgba(0,0,0,.16), inset 0 1px 0 rgba(255,255,255,.09) !important;
      backdrop-filter: blur(22px) saturate(145%) !important;
    }
    .sf-landing-hero:before { border-color: color-mix(in srgb, var(--blue-light) 38%, transparent) !important; box-shadow: 0 0 0 28px color-mix(in srgb, var(--blue) 7%, transparent), 0 0 0 62px color-mix(in srgb, var(--blue) 5%, transparent) !important; }
    .sf-brand, .sf-landing-kicker, .sf-eyebrow { color: var(--blue-light) !important; }
    .sf-landing-title, .sf-preview-heading, .sf-title { color: var(--text) !important; }
    .sf-landing-title span, .sf-kicker-dot { color: var(--blue-light) !important; background: var(--blue) !important; }
    .sf-landing-copy, .sf-landing-points, .sf-preview-sub, .sf-preview-top { color: var(--muted) !important; }
    .sf-landing-points span:before { color: var(--blue) !important; }
    .sf-preview-card, .sf-feature, .sf-preview-kpi, .sf-chart-shell, .sf-model-tags span {
      background: var(--forest-glass) !important;
      border: 1px solid var(--forest-line) !important;
      border-radius: 18px !important;
      box-shadow: 0 14px 36px rgba(0,0,0,.12), inset 0 1px 0 rgba(255,255,255,.08) !important;
      backdrop-filter: blur(20px) saturate(145%) !important;
    }
    .sf-live-pill { color: var(--blue-light) !important; background: color-mix(in srgb, var(--blue) 13%, transparent) !important; border-color: color-mix(in srgb, var(--blue) 35%, transparent) !important; }
    .sf-chart span { background: linear-gradient(180deg, var(--blue-light), var(--blue)) !important; box-shadow: 0 0 13px color-mix(in srgb, var(--blue) 18%, transparent) !important; }
    .sf-feature-icon { background: color-mix(in srgb, var(--blue) 13%, transparent) !important; border-color: color-mix(in srgb, var(--blue) 30%, transparent) !important; }
    [data-testid="stVerticalBlockBorderWrapper"], [data-testid="stMetric"],
    [data-testid="stExpander"] details, [data-testid="stAlert"],
    [data-testid="stPlotlyChart"], [data-testid="stDataFrame"], [data-testid="stTable"] {
      background: var(--forest-glass) !important;
      border: 1px solid var(--forest-line) !important;
      border-radius: 18px !important;
      box-shadow: 0 14px 36px rgba(0,0,0,.10), inset 0 1px 0 rgba(255,255,255,.07) !important;
      backdrop-filter: blur(18px) saturate(140%) !important;
    }
    [data-testid="stMetric"] { padding: 18px !important; }
    [data-testid="stVerticalBlockBorderWrapper"]:hover, [data-testid="stMetric"]:hover {
      border-color: color-mix(in srgb, var(--blue) 55%, var(--border)) !important;
      transform: translateY(-1px);
    }
    [data-testid="stTabs"] [role="tablist"] {
      gap: 7px !important; padding: 7px !important;
      background: var(--forest-glass) !important;
      border: 1px solid var(--forest-line) !important;
      border-radius: 17px !important;
      backdrop-filter: blur(18px) !important;
    }
    [data-testid="stTabs"] button[role="tab"] { border-radius: 12px !important; color: var(--muted) !important; }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
      background: color-mix(in srgb, var(--blue) 19%, var(--panel)) !important;
      border: 1px solid color-mix(in srgb, var(--blue) 48%, var(--border)) !important;
      color: var(--text) !important;
      box-shadow: inset 0 1px 0 rgba(255,255,255,.10) !important;
    }
    [data-baseweb="select"] > div, [data-baseweb="input"] > div,
    [data-baseweb="textarea"] > div, [data-testid="stFileUploader"] section {
      background: var(--forest-glass-strong) !important;
      border: 1px solid var(--forest-line) !important;
      border-radius: 13px !important;
      color: var(--text) !important;
      backdrop-filter: blur(14px) !important;
    }
    .stButton button, [data-testid="stDownloadButton"] button,
    [data-testid="stFormSubmitButton"] button, div[data-testid="stButton"] button[kind="primary"] {
      border: 1px solid color-mix(in srgb, var(--blue) 58%, var(--border)) !important;
      border-radius: 13px !important;
      background: linear-gradient(120deg, var(--blue), color-mix(in srgb, var(--blue) 66%, var(--teal))) !important;
      color: #fff !important;
      box-shadow: 0 9px 24px color-mix(in srgb, var(--blue) 18%, transparent), inset 0 1px 0 rgba(255,255,255,.17) !important;
      transition: transform .18s ease, filter .18s ease !important;
    }
    .stButton button:hover, [data-testid="stDownloadButton"] button:hover,
    [data-testid="stFormSubmitButton"] button:hover { filter: brightness(1.08) !important; transform: translateY(-2px) !important; }
    [data-testid="stDataFrame"] *, [data-testid="stTable"] * { color: var(--text); }
    hr { border-color: var(--forest-line) !important; }
    .sf-panel-title, .sf-section-heading { color: var(--text) !important; }
    .sf-panel-subtitle, .sf-section-copy, .sf-metric-label, .sf-metric-note { color: var(--muted) !important; }
    .sf-metric-value { color: var(--text) !important; }
    @media (max-width: 850px) { .sf-landing-hero { grid-template-columns: 1fr !important; } }
    @media (prefers-reduced-motion: reduce) { *, *::before, *::after { transition-duration: .01ms !important; animation-duration: .01ms !important; } }
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
        colorway=[theme["blue"], theme["teal"], theme["gold"], theme["blue_light"], "#8D9B65", "#C47B62"],
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


# =========================================================
# LANDING PAGE — CONCEPT A: EXECUTIVE ANALYTICS
# =========================================================
if not st.session_state.show_dashboard:
    top_left, top_right = st.columns([5, 1])
    with top_left:
        st.markdown(
            '<div class="sf-brand">STA. CRUZ, LAGUNA &nbsp;·&nbsp; SALES INTELLIGENCE</div>',
            unsafe_allow_html=True,
        )
    with top_right:
        landing_theme_label = "☀️ Light Mode" if st.session_state.theme_mode == "dark" else "🌙 Dark Mode"
        st.button(
            landing_theme_label,
            key="landing_theme_toggle",
            on_click=toggle_theme,
            use_container_width=True,
        )

    st.markdown(
        """
        <div class="sf-landing-wrap">
          <section class="sf-landing-hero">
            <div class="sf-landing-copy-wrap">
              <div class="sf-landing-kicker"><span class="sf-kicker-dot"></span> BUSINESS INTELLIGENCE PLATFORM</div>
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
                <span class="sf-live-pill">● ANALYTICS PREVIEW</span>
              </div>
              <div class="sf-preview-heading">Sales Forecasting DSS</div>
              <div class="sf-preview-sub">A unified view of demand patterns and forecast performance</div>
              <div class="sf-preview-kpis">
                <div class="sf-preview-kpi"><div class="sf-preview-kpi-label">HISTORICAL DATA</div><div class="sf-preview-kpi-value">Demand trends</div></div>
                <div class="sf-preview-kpi"><div class="sf-preview-kpi-label">MODEL REVIEW</div><div class="sf-preview-kpi-value">4 approaches</div></div>
                <div class="sf-preview-kpi"><div class="sf-preview-kpi-label">FORECAST OUTPUT</div><div class="sf-preview-kpi-value">Predictions</div></div>
              </div>
              <div class="sf-chart-shell">
                <div class="sf-chart-label"><span>DEMAND TREND PREVIEW</span><span>HISTORICAL + FORECAST</span></div>
                <div class="sf-chart">
                  <span style="height:38%"></span><span style="height:51%"></span>
                  <span style="height:45%"></span><span style="height:62%"></span>
                  <span style="height:55%"></span><span style="height:72%"></span>
                  <span style="height:64%"></span><span style="height:83%"></span>
                  <span style="height:72%"></span><span style="height:91%"></span>
                  <span style="height:79%"></span><span style="height:98%"></span>
                </div>
                <div class="sf-chart-legend"><span>PAST DEMAND</span><span>FORECAST INSIGHTS</span></div>
              </div>
              <div class="sf-model-tags"><span>ARIMA</span><span>SARIMA</span><span>PROPHET</span><span>RANDOM FOREST</span></div>
            </div>
          </section>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    cta_left, cta_right = st.columns([1.15, 3.85])
    with cta_left:
        if st.button(
            "Explore Dashboard  →",
            type="primary",
            use_container_width=True,
            key="enter_dashboard",
        ):
            st.session_state.show_dashboard = True
            st.rerun()
    with cta_right:
        st.markdown(
            '<div class="sf-landing-cta-note">Enter the analytics workspace to review historical sales, model evaluation results, forecast trends, and downloadable records.</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div class="sf-section-heading">One Workspace. Four Core Capabilities.</div>'
        '<div class="sf-section-copy">Explore the key functions available in the Sales Forecasting Decision Support System.</div>',
        unsafe_allow_html=True,
    )
    feature_cols = st.columns(4, gap="medium")
    feature_data = [
        ("📊", "Sales Analytics", "Examine historical daily demand, monthly totals, and recurring demand patterns."),
        ("🧠", "Forecasting Models", "Review forecasts generated using ARIMA, SARIMA, Prophet, and Random Forest."),
        ("🎯", "Model Evaluation", "Compare model accuracy through MAE, RMSE, MAPE, and WAPE."),
        ("📁", "Data & Downloads", "Inspect saved forecast records and export standardized datasets and reports."),
    ]
    for col, (icon, title, description) in zip(feature_cols, feature_data):
        with col:
            st.markdown(
                f'<div class="sf-feature"><div class="sf-feature-icon">{icon}</div>'
                f'<div class="sf-feature-title">{html.escape(title)}</div>'
                f'<div class="sf-feature-copy">{html.escape(description)}</div></div>',
                unsafe_allow_html=True,
            )

    st.markdown(
        '<div class="sf-section-heading">How It Supports Better Planning</div>'
        '<div class="sf-section-copy">A clear path from recorded sales information to forecast-based decision support.</div>',
        unsafe_allow_html=True,
    )
    step_cols = st.columns(3, gap="medium")
    steps = [
        ("01", "Understand Demand", "Review historical sales records and identify demand patterns over time."),
        ("02", "Compare Forecasts", "Evaluate the available models and examine their error measurements."),
        ("03", "Use Forecast Insights", "Review predicted demand and export results to support planning."),
    ]
    for col, (number, title, description) in zip(step_cols, steps):
        with col:
            st.markdown(
                f'<div class="sf-feature"><div class="sf-step-no">STEP {number}</div>'
                f'<div class="sf-feature-title">{html.escape(title)}</div>'
                f'<div class="sf-feature-copy">{html.escape(description)}</div></div>',
                unsafe_allow_html=True,
            )

    st.divider()
    st.markdown(
        '<div class="sf-footer">STA. CRUZ LAGUNA SALES FORECASTING DECISION SUPPORT SYSTEM &nbsp;·&nbsp; POWERED BY PYTHON AND STREAMLIT</div>',
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

# Theme control directly below System Information.
st.sidebar.markdown('<div class="theme-label">Appearance</div>', unsafe_allow_html=True)
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
tab_overview, tab_evaluation, tab_analysis, tab_auto_forecast, tab_downloads = st.tabs(
    [
        "Overview",
        "Model Evaluation",
        "Forecast Analysis",
        "Automatic Forecasting",
        "Downloads & Data",
    ]
)


# =========================================================
# OVERVIEW
# =========================================================
with tab_overview:
    total_demand = actual_df["daily_demand"].sum()
    average_demand = actual_df["daily_demand"].mean()
    highest_demand = actual_df["daily_demand"].max()
    highest_demand_date = actual_df.loc[
        actual_df["daily_demand"].idxmax(), "date"
    ].date()

    # High-level KPIs are placed first so users can understand the dataset quickly.
    kpi_cols = st.columns(4, gap="medium")
    with kpi_cols[0]:
        st.metric("Total Historical Demand", f"{total_demand:,.0f}")
    with kpi_cols[1]:
        st.metric("Average Daily Demand", f"{average_demand:,.2f}")
    with kpi_cols[2]:
        st.metric("Peak Daily Demand", f"{highest_demand:,.0f}", help=f"Recorded on {highest_demand_date}")
    with kpi_cols[3]:
       st.metric(
    "Best Model · Validation WAPE",
    f"{lowest_wape:.2f}%",
    help=f"Selected using 2023 validation WAPE: {best_model}",
)
    st.caption(
        f"Historical coverage: {actual_df['date'].min():%b %d, %Y} – "
        f"{actual_df['date'].max():%b %d, %Y}  ·  "
        f"{len(actual_df):,} historical records  ·  {len(df):,} forecast records"
    )

    top_left, top_right = st.columns([1.15, 1], gap="medium")

    with top_left:
        with st.container(border=True):
            panel_heading(
                "Forecast Model Performance",
                "Model comparison using saved MAPE values · lower is better",
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
               labels={"wape": "WAPE (%)", "model_name": ""}
            )
            fig_overview_models.update_traces(
                texttemplate="%{text:.2f}%",
                textposition="outside",
                cliponaxis=False,
            )
            fig_overview_models.update_layout(showlegend=False, xaxis_title="Validation WAPE (%)", yaxis_title="")
            style_figure(fig_overview_models, 320)
            st.plotly_chart(
                fig_overview_models,
                use_container_width=True,
                config={"responsive": True, "displayModeBar": False},
            )

    with top_right:
        with st.container(border=True):
            panel_heading("Monthly Demand", "Total historical demand by month")
            fig_monthly_overview = px.bar(
                monthly_sales,
                x="month",
                y="daily_demand",
                color_discrete_sequence=[theme["blue"]],
                labels={"month": "", "daily_demand": "Demand"},
            )
            fig_monthly_overview.update_traces(marker_line_width=0, opacity=0.92)
            fig_monthly_overview.update_xaxes(dtick="M6", tickformat="%b<br>%Y", title_text="")
            fig_monthly_overview.update_yaxes(title_text="")
            style_figure(fig_monthly_overview, 320)
            st.plotly_chart(
                fig_monthly_overview,
                use_container_width=True,
                config={"responsive": True, "displayModeBar": False},
            )

    bottom_left, bottom_right = st.columns([1, 1.7], gap="medium")

    with bottom_left:
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
                    thickness=9,
                    len=0.78,
                    tickfont=dict(size=8, color=theme["muted"]),
                    title=dict(text="", font=dict(size=8)),
                )
            )
            fig_heatmap.update_xaxes(tickfont=dict(size=8), side="bottom")
            fig_heatmap.update_yaxes(tickfont=dict(size=9))
            style_figure(fig_heatmap, 350)
            st.plotly_chart(
                fig_heatmap,
                use_container_width=True,
                config={"responsive": True, "displayModeBar": False},
            )

    with bottom_right:
        with st.container(border=True):
            panel_heading(
                f"Demand Forecast · {selected_model}",
                "Saved predicted demand values for the selected forecasting model",
            )
            fig_forecast_overview = px.line(
                model_data,
                x="forecast_date",
                y="predicted_demand",
                color_discrete_sequence=[theme["gold"]],
                labels={"forecast_date": "", "predicted_demand": "Predicted demand"},
            )
            fig_forecast_overview.update_traces(
                line=dict(width=2.5, color=theme["gold"]),
                mode="lines",
            )
            fig_forecast_overview.update_yaxes(title_text="")
            fig_forecast_overview.update_xaxes(title_text="")
            style_figure(fig_forecast_overview, 275)
            st.plotly_chart(
                fig_forecast_overview,
                use_container_width=True,
                config={"responsive": True, "displayModeBar": False},
            )

            forecast_kpis = st.columns(3, gap="small")
            with forecast_kpis[0]:
                st.metric("Average Forecast", f"{model_data['predicted_demand'].mean():,.1f}")
            with forecast_kpis[1]:
                st.metric("Peak Forecast", f"{model_data['predicted_demand'].max():,.1f}")
            with forecast_kpis[2]:
                st.metric("Forecast Records", f"{len(model_data):,}")

    st.caption(
        "Dashboard values are calculated from the historical sales file and saved forecast results."
    )

# =========================================================
# MODEL EVALUATION
# =========================================================
with tab_evaluation:
    st.subheader("Forecast Model Evaluation")
    st.caption("Compare all available models using the MAE and MAPE values stored in the forecast results.")

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
        style_figure(fig_mape, 410)
        st.plotly_chart(fig_mape, use_container_width=True, config={"responsive": True, "displayModeBar": False})

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
        style_figure(fig_mae, 410)
        st.plotly_chart(fig_mae, use_container_width=True, config={"responsive": True, "displayModeBar": False})

    st.subheader("Model Performance Summary")
    performance_display = performance.copy()
    performance_display["mae"] = performance_display["mae"].round(2)
    performance_display["mape"] = performance_display["mape"].round(2)
    st.dataframe(performance_display, use_container_width=True, hide_index=True)

   # 2023 VALIDATION PERFORMANCE
st.subheader("Model Performance Ranking (2023 Validation)")

ranking_display = ranking.copy()

for col in ["mae", "rmse", "mape", "wape"]:
    ranking_display[col] = ranking_display[col].round(3)

st.dataframe(
    ranking_display,
    use_container_width=True,
    hide_index=True
)

# 2024 FINAL HOLDOUT PERFORMANCE
st.subheader("2024 Final Holdout Performance")

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
    "using 2024 final-test performance metrics."
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
       title="2024 Final-Test MAPE by Forecasting Approach",
        color_discrete_sequence=[theme["teal"], theme["blue"]],
)
fig_approach_mape.update_traces(texttemplate="%{text:.2f}%", textposition="outside", cliponaxis=False)
fig_approach_mape.update_layout(showlegend=False)
fig_approach_mape.update_xaxes(title_text="", tickfont=dict(size=10))
fig_approach_mape.update_yaxes(title_text="MAPE (%)")
style_figure(fig_approach_mape, 405)
st.plotly_chart(fig_approach_mape, use_container_width=True, config={"responsive": True, "displayModeBar": False})

with approach_col2:
    fig_approach_mae = px.bar(
        approach_df,
        x="Approach",
        y="mae",
        color="Approach",
        text="mae",
        title="2024 Final-Test MAE by Forecasting Approach",
        color_discrete_sequence=[theme["teal"], theme["blue"]],
    )
    fig_approach_mae.update_traces(texttemplate="%{text:.2f}", textposition="outside", cliponaxis=False)
    fig_approach_mae.update_layout(showlegend=False)
    fig_approach_mae.update_xaxes(title_text="", tickfont=dict(size=10))
    fig_approach_mae.update_yaxes(title_text="MAE")
    style_figure(fig_approach_mae, 405)
    st.plotly_chart(fig_approach_mae, use_container_width=True, config={"responsive": True, "displayModeBar": False})

st.info(
        "Interpretation: Models are ranked using 2023 validation WAPE. "
        "The 2024 final-test metrics are reported separately and are not used "
        "for model selection. All four models are compared using the same "
        "evaluation period and demand target."
    )

# =========================================================
# FORECAST ANALYSIS
# =========================================================
with tab_analysis:
    st.subheader(f"{selected_model} Forecast Analysis")
    st.caption("The selected model controls the forecast charts and forecast summary below.")

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
    style_figure(fig_compare, 430)
    fig_compare.update_layout(showlegend=True)
    st.plotly_chart(fig_compare, use_container_width=True, config={"responsive": True, "displayModeBar": False})

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
    style_figure(fig_month_analysis, 410)
    st.plotly_chart(fig_month_analysis, use_container_width=True, config={"responsive": True, "displayModeBar": False})

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
    style_figure(fig_error, 410)
    st.plotly_chart(fig_error, use_container_width=True, config={"responsive": True, "displayModeBar": False})

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
    style_figure(fig_forecast, 410)
    st.plotly_chart(fig_forecast, use_container_width=True, config={"responsive": True, "displayModeBar": False})


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
        st.plotly_chart(fig_test, use_container_width=True)

        st.subheader(f"Next {phase2_results['horizon']} Days · Forecast by Model")
        fig_future = px.line(
            future_view,
            x="Forecast_Date",
            y="Predicted_Value",
            color="Model",
            title=f"Future {target_choice} forecast",
            labels={"Forecast_Date": "Forecast date", "Predicted_Value": "Predicted value"},
        )
        st.plotly_chart(fig_future, use_container_width=True)
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

    st.subheader("Standardized DSS Data Exports")

    st.caption(
        "Download the standardized datasets used by the academic "
        "forecasting and decision support system."
    )

    export_files = [
        ("Daily Demand Data", "aggregated_daily_demand.csv"),
        ("2023 Validation Metrics", "validation_model_performance.csv"),
        ("2024 Test Metrics", "test_model_performance_2024.csv"),
        ("2023 Validation Forecasts", "validation_forecasts_2023.csv"),
        ("2024 Test Forecasts", "test_forecasts_2024.csv"),
        ("Future Forecasts", "future_forecasts.csv"),
        ("Model Selection Summary", "model_selection_summary.csv"),
    ]

    for start in range(0, len(export_files), 2):
        cols = st.columns(2, gap="medium")

        for col, item in zip(cols, export_files[start:start + 2]):
            label, filename = item

            with col:
                st.download_button(
                    label,
                    data=(DATA_DIR / filename).read_bytes(),
                    file_name=filename,
                    mime="text/csv",
                    use_container_width=True,
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
