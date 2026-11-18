import html
from pathlib import Path

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
    "page": "#071326",
    "page_grad_1": "#08172D",
    "page_grad_2": "#050E1D",
    "sidebar": "#09182C",
    "hero": "#102442",
    "hero2": "#142E52",
    "panel": "#0B1B31",
    "panel_alt": "#102541",
    "panel_soft": "#0D2039",
    "border": "#29466B",
    "tab_bg": "#0D2038",
    "tab_active": "#12396A",
    "tab_text": "#c8d4e3",
    "tab_active_border": "#398BFF",
    "text": "#edf3fb",
    "muted": "#9db0c5",
    "blue": "#398BFF",
    "blue_light": "#75B5FF",
    "teal": "#55b8a5",
    "gold": "#e0b85c",
    "success_bg": "#0B2938",
    "success_border": "#1C7895",
    "success_text": "#d4eff0",
    "table_header": "#132B49",
}

LIGHT_THEME = {
    "name": "light",
    "page": "#eef3f8",
    "page_grad_1": "#eef3f8",
    "page_grad_2": "#e6edf5",
    "sidebar": "#e7eef6",
    "hero": "#ffffff",
    "hero2": "#f6f9fc",
    "panel": "#ffffff",
    "panel_alt": "#f7fafd",
    "panel_soft": "#f3f7fb",
    "border": "#d7e1ec",
    "tab_bg": "#ffffff",
    "tab_active": "#dfeaf7",
    "tab_text": "#42566f",
    "tab_active_border": "#6f93bb",
    "text": "#32465d",
    "muted": "#6b7e93",
    "blue": "#6f93bb",
    "blue_light": "#87a9cf",
    "teal": "#5db39f",
    "gold": "#d8aa4f",
    "success_bg": "#ecf7f4",
    "success_border": "#b7ded4",
    "success_text": "#355f59",
    "table_header": "#edf3f8",
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
tab_overview, tab_evaluation, tab_analysis, tab_downloads = st.tabs(
    [
        "Overview",
        "Model Evaluation",
        "Forecast Analysis",
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
# DOWNLOADS AND DATA
# =========================================================
with tab_downloads:
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
