"""Glassmorphism styling layer for the Sales Forecasting DSS.

Upload this file beside app.py. Then, immediately after st.set_page_config(...)
in app.py, add:
    from glass_ui import apply_glass_ui
    apply_glass_ui()

This module only injects CSS. It does not alter forecasting logic or data operations.
"""
import streamlit as st


def apply_glass_ui():
    st.markdown(r"""
    <style>
    :root {
      --fi-border: rgba(139,190,255,.23);
      --fi-muted: #a9bdd4;
      --fi-text: #edf5ff;
      --fi-glass: rgba(17,39,67,.66);
    }
    html, body, [data-testid="stAppViewContainer"] {
      background:
        radial-gradient(circle at 12% 8%,rgba(35,119,210,.20),transparent 32%),
        radial-gradient(circle at 88% 18%,rgba(27,190,213,.12),transparent 28%),
        linear-gradient(135deg,#061225 0%,#0a1b31 48%,#071426 100%) !important;
      color:var(--fi-text) !important;
    }
    [data-testid="stHeader"] {
      background:rgba(5,16,31,.58) !important;
      backdrop-filter:blur(18px);
    }
    [data-testid="stAppViewContainer"] .main .block-container {
      padding-top:1.7rem; padding-bottom:3rem; max-width:1500px;
    }
    h1,h2,h3,h4,h5,h6,p,label,li,
    [data-testid="stMarkdownContainer"] { color:var(--fi-text); }
    [data-testid="stCaptionContainer"],.stCaption,small {
      color:var(--fi-muted) !important;
    }
    [data-testid="stSidebar"] {
      background:linear-gradient(180deg,rgba(8,27,49,.94),rgba(6,19,36,.91)) !important;
      border-right:1px solid var(--fi-border);
    }
    [data-testid="stSidebar"] > div:first-child { background:transparent !important; }
    [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stExpander"],[data-testid="stMetric"],
    [data-testid="stDataFrame"],[data-testid="stTable"],
    [data-testid="stFileUploader"],[data-testid="stAlert"],
    [data-testid="stForm"] {
      background:var(--fi-glass) !important;
      border:1px solid var(--fi-border) !important;
      border-radius:16px !important;
      box-shadow:0 14px 38px rgba(0,0,0,.24);
      backdrop-filter:blur(16px);
      -webkit-backdrop-filter:blur(16px);
    }
    [data-testid="stMetric"] { padding:16px 18px; }
    [data-testid="stMetricLabel"] { color:var(--fi-muted) !important; }
    [data-testid="stMetricValue"] { color:#f4f8ff !important; font-weight:750; }
    [data-baseweb="select"] > div,[data-baseweb="input"] > div,
    [data-baseweb="textarea"] > div,[data-testid="stDateInput"] > div,
    [data-testid="stNumberInput"] > div {
      background:rgba(9,27,48,.78) !important;
      border:1px solid var(--fi-border) !important;
      border-radius:11px !important; color:var(--fi-text) !important;
    }
    input,textarea { color:var(--fi-text) !important; }
    .stButton > button,.stDownloadButton > button,
    [data-testid="stFormSubmitButton"] > button {
      color:#f7fbff !important;
      background:linear-gradient(110deg,#1769c2,#168eb7) !important;
      border:1px solid rgba(125,195,255,.48) !important;
      border-radius:11px !important; font-weight:650 !important;
      min-height:2.55rem;
      box-shadow:0 7px 22px rgba(20,112,205,.20);
      transition:transform .18s ease,box-shadow .18s ease,filter .18s ease;
    }
    .stButton > button:hover,.stDownloadButton > button:hover,
    [data-testid="stFormSubmitButton"] > button:hover {
      transform:translateY(-2px); filter:brightness(1.10);
      box-shadow:0 11px 28px rgba(30,145,235,.30);
      border-color:#61d7ed !important;
    }
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
      gap:8px; background:rgba(10,29,51,.55);
      border:1px solid var(--fi-border); border-radius:13px; padding:6px;
    }
    [data-testid="stTabs"] button[role="tab"] {
      color:var(--fi-muted) !important; border-radius:9px; padding:9px 15px;
    }
    [data-testid="stTabs"] button[aria-selected="true"] {
      color:#fff !important;
      background:linear-gradient(110deg,rgba(30,112,204,.55),rgba(28,159,184,.32)) !important;
    }
    [data-testid="stPlotlyChart"],[data-testid="stVegaLiteChart"],
    [data-testid="stAltairChart"],[data-testid="stPyplot"] {
      background:rgba(8,24,43,.48) !important;
      border:1px solid var(--fi-border) !important;
      border-radius:16px !important; padding:8px;
      box-shadow:0 14px 38px rgba(0,0,0,.24);
    }
    [data-testid="stFileUploader"] section {
      background:rgba(12,33,57,.55) !important;
      border:1px dashed rgba(104,183,255,.42) !important;
      border-radius:13px !important;
    }
    hr { border-color:rgba(130,180,230,.20) !important; }
    ::-webkit-scrollbar { width:9px; height:9px; }
    ::-webkit-scrollbar-track { background:rgba(4,15,28,.65); }
    ::-webkit-scrollbar-thumb { background:rgba(87,151,207,.48); border-radius:20px; }
    @media(max-width:768px) {
      [data-testid="stAppViewContainer"] .main .block-container {
        padding-left:1rem; padding-right:1rem;
      }
      [data-testid="stTabs"] [data-baseweb="tab-list"] { overflow-x:auto; }
    }
    </style>
    """, unsafe_allow_html=True)
