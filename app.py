import html
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="Sales Forecasting System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# THEME AND CUSTOM CSS
# =========================================================
st.markdown(
    """
    <style>
    :root {
        --page: #0a1220;
        --panel: #111c2c;
        --panel-alt: #172438;
        --border: #29384d;
        --blue: #4b8fe8;
        --blue-light: #65b5f0;
        --teal: #42c6a5;
        --gold: #f2c35b;
        --text: #edf3fb;
        --muted: #9aaac0;
    }

    .stApp {
        background: #0a1220;
        color: var(--text);
    }

    .block-container {
        max-width: 1800px;
        /* Keep the dashboard header below Streamlit's floating top toolbar. */
        padding-top: 4.1rem !important;
        padding-bottom: 2.5rem;
        padding-left: clamp(1rem, 2vw, 2rem);
        padding-right: clamp(1rem, 2vw, 2rem);
    }

    section[data-testid="stMain"] .block-container {
        padding-top: 4.1rem !important;
    }

    div[data-testid="stHorizontalBlock"] {
        gap: 0.9rem;
        align-items: stretch;
    }

    div[data-testid="stTabs"] [data-baseweb="tab-panel"] {
        padding-top: 1rem;
    }

    h1, h2, h3, p, label {
        color: var(--text);
    }

    h1 { font-size: 1.9rem !important; font-weight: 800 !important; }
    h2 { font-size: 1.35rem !important; font-weight: 750 !important; }
    h3 { font-size: 1.05rem !important; font-weight: 700 !important; }

    /* Compact BI-style dashboard header */
    .sf-hero {
        position: relative;
        overflow: hidden;
        background: linear-gradient(110deg, #101b2c 0%, #142238 100%);
        border: 1px solid #29384d;
        border-radius: 13px;
        padding: 19px 24px;
        margin: 0.15rem 0 1.15rem 0;
        box-shadow: none;
    }

    .sf-hero:after { display: none; }

    .sf-eyebrow {
        color: #75a9e8;
        font-size: 0.68rem;
        font-weight: 800;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        margin-bottom: 0.45rem;
    }

    .sf-title {
        color: #f4f7fc;
        font-size: 1.85rem;
        font-weight: 800;
        line-height: 1.15;
        margin: 0;
    }

    .sf-subtitle {
        color: #a9b8ca;
        font-size: 0.84rem;
        line-height: 1.45;
        max-width: 900px;
        margin: 0.45rem 0 0 0;
    }

    .sf-accent {
        width: 62px;
        height: 3px;
        border-radius: 10px;
        background: #4b8fe8;
        margin-top: 0.8rem;
        box-shadow: none;
    }

    /* Dashboard panel headings */
    .sf-panel-title {
        color: #e9f0f9;
        font-size: 0.91rem;
        font-weight: 750;
        line-height: 1.3;
        margin: 0 0 0.2rem 0;
    }

    .sf-panel-subtitle {
        color: #8799b0;
        font-size: 0.70rem;
        line-height: 1.4;
        margin: 0 0 0.65rem 0;
    }

    .sf-panel-divider {
        border: 0;
        border-top: 1px solid #29384d;
        margin: 0.55rem 0;
    }

    /* Compact metric rows inspired by enterprise BI dashboards */
    .sf-metric-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 10px;
        padding: 0.68rem 0;
        border-bottom: 1px solid rgba(130, 151, 178, 0.17);
    }

    .sf-metric-row:last-child { border-bottom: 0; }

    .sf-metric-label {
        color: #b6c2d2;
        font-size: 0.76rem;
        line-height: 1.35;
    }

    .sf-metric-value {
        color: #f3f6fb;
        font-size: 1.03rem;
        font-weight: 800;
        white-space: nowrap;
        text-align: right;
    }

    .sf-metric-note {
        color: #42c6a5;
        font-size: 0.65rem;
        font-weight: 650;
        margin-top: 2px;
        text-align: right;
    }

    .sf-recommendation {
        background: #10263a;
        border: 1px solid #294d6c;
        border-left: 3px solid #4b8fe8;
        color: #c9d8e9;
        border-radius: 8px;
        padding: 0.75rem 0.9rem;
        font-size: 0.78rem;
        line-height: 1.5;
        margin-top: 0.8rem;
    }

    /* Streamlit bordered containers become dashboard panels */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: linear-gradient(150deg, #121f31 0%, #101a29 100%);
        border: 1px solid #29384d !important;
        border-radius: 11px !important;
        padding: 0.78rem 0.82rem 0.65rem 0.82rem;
        box-shadow: none;
    }

    /* Standard metrics in detail tabs */
    div[data-testid="stMetric"] {
        background: #142237;
        border: 1px solid #2b4058 !important;
        border-radius: 9px !important;
        padding: 11px 13px;
        min-height: 88px;
        box-shadow: none;
    }

    [data-testid="stMetricLabel"] {
        color: #9eafc4 !important;
        font-size: 0.75rem !important;
    }

    [data-testid="stMetricValue"] {
        color: #f4f7fc !important;
        font-weight: 800 !important;
        font-size: 1.35rem !important;
    }

    /* Plotly charts sit cleanly inside their parent panels */
    div[data-testid="stPlotlyChart"] {
        background: transparent !important;
        border: 0 !important;
        border-radius: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        overflow: hidden !important;
        box-shadow: none !important;
    }

    div[data-testid="stPlotlyChart"] > div {
        overflow: hidden !important;
    }

    div[data-testid="stDataFrame"],
    div[data-testid="stTable"],
    .stDataFrame {
        border: 1px solid #29384d !important;
        border-radius: 9px !important;
        overflow: hidden;
    }

    div[data-testid="stAlert"],
    .stAlert,
    div[data-testid="stExpander"] {
        border-radius: 9px !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #0f1a2a;
        border-right: 1px solid #29384d;
        min-width: 270px;
    }

    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #f1f5fb !important;
    }

    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        border: 1px solid #344b66 !important;
        border-radius: 8px !important;
        background: #111d2d;
    }

    /* Compact navigation tabs */
    div[data-testid="stTabs"] [role="tablist"] {
        gap: 6px;
        border-bottom: 1px solid #29384d;
        padding-bottom: 6px;
    }

    div[data-testid="stTabs"] button[role="tab"] {
        background: #121f31;
        border: 1px solid #29384d;
        border-radius: 8px 8px 5px 5px;
        color: #aebdd0;
        font-weight: 650;
        padding: 8px 12px;
        font-size: 0.82rem;
    }

    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background: #1b3554;
        border: 1px solid #4b8fe8;
        color: #ffffff;
        box-shadow: none;
    }

    div[data-testid="stDownloadButton"] button,
    .stButton button {
        border: 1px solid #385778 !important;
        border-radius: 8px !important;
    }

    hr {
        border-color: #29384d !important;
    }

    @media (max-width: 1100px) {
        .sf-title { font-size: 1.55rem; }
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================
def section_heading(title: str, caption: str | None = None) -> None:
    st.markdown(
        f'<div class="sf-section-label">{html.escape(title)}</div>',
        unsafe_allow_html=True,
    )
    if caption:
        st.markdown(
            f'<div class="sf-section-caption">{html.escape(caption)}</div>',
            unsafe_allow_html=True,
        )


def kpi_card(label: str, value: str, note: str, icon: str = "✦") -> None:
    safe_label = html.escape(str(label))
    safe_value = html.escape(str(value))
    safe_note = html.escape(str(note))
    safe_icon = html.escape(str(icon))
    st.markdown(
        f"""
        <div class="sf-kpi">
            <div class="sf-kpi-top">
                <div class="sf-kpi-label">{safe_label}</div>
                <div class="sf-kpi-icon">{safe_icon}</div>
            </div>
            <div class="sf-kpi-value">{safe_value}</div>
            <div class="sf-kpi-note">{safe_note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


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
    note_html = (
        f'<div class="sf-metric-note">{html.escape(str(note))}</div>'
        if note else ""
    )
    st.markdown(
        f"""
        <div class="sf-metric-row">
            <div class="sf-metric-label">{safe_label}</div>
            <div>
                <div class="sf-metric-value">{safe_value}</div>
                {note_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_figure(fig, height: int = 340):
    """Apply compact enterprise-dashboard styling to Plotly figures."""
    fig.update_layout(
        template="plotly_dark",
        height=height,
        autosize=True,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#dce6f2", family="Arial", size=10),
        margin=dict(l=42, r=18, t=38, b=42),
        showlegend=False,
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=9),
        ),
    )
    fig.update_xaxes(
        title_font=dict(size=10),
        tickfont=dict(size=9, color="#9eafc4"),
        automargin=True,
        gridcolor="rgba(130,151,178,0.13)",
        zerolinecolor="rgba(130,151,178,0.18)",
        showline=False,
    )
    fig.update_yaxes(
        title_font=dict(size=10),
        tickfont=dict(size=9, color="#9eafc4"),
        automargin=True,
        gridcolor="rgba(130,151,178,0.13)",
        zerolinecolor="rgba(130,151,178,0.18)",
        showline=False,
    )
    return fig


# =========================================================
# DATA LOADING AND VALIDATION
# =========================================================
@st.cache_data
def load_forecast():
    file_path = Path("forecast_results_final.csv")
    if not file_path.exists():
        raise FileNotFoundError(
            "forecast_results_final.csv was not found. "
            "Place it in the same GitHub root folder as app.py."
        )

    data = pd.read_csv(file_path)
    required = {
        "forecast_date",
        "predicted_demand",
        "model_name",
        "mae",
        "mape",
    }
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(
            "forecast_results_final.csv is missing these columns: "
            + ", ".join(sorted(missing))
        )

    data["forecast_date"] = pd.to_datetime(
        data["forecast_date"], errors="coerce"
    )
    for col in ["predicted_demand", "mae", "mape"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data["model_name"] = data["model_name"].astype(str)
    data = data.dropna(
        subset=["forecast_date", "predicted_demand", "model_name"]
    ).sort_values(["model_name", "forecast_date"])

    return data


@st.cache_data
def load_actual():
    file_path = Path("daily_sales_clean.csv")
    if not file_path.exists():
        raise FileNotFoundError(
            "daily_sales_clean.csv was not found. "
            "Place it in the same GitHub root folder as app.py."
        )

    data = pd.read_csv(file_path)
    required = {"date", "daily_demand"}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(
            "daily_sales_clean.csv is missing these columns: "
            + ", ".join(sorted(missing))
        )

    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    data["daily_demand"] = pd.to_numeric(
        data["daily_demand"], errors="coerce"
    )
    data = data.dropna(subset=["date", "daily_demand"])
    data = data.sort_values("date")

    return data


try:
    df = load_forecast()
    actual_df = load_actual()
except Exception as error:
    st.error(f"Unable to load dashboard data: {error}")
    st.stop()

if df.empty or actual_df.empty:
    st.error("The forecast file or historical sales file contains no usable records.")
    st.stop()

# Consistent model ordering while retaining any model names found in the CSV.
preferred_order = ["ARIMA", "SARIMA", "Prophet", "Random Forest"]
available_models = df["model_name"].dropna().unique().tolist()
model_options = [name for name in preferred_order if name in available_models]
model_options += [name for name in available_models if name not in model_options]

if not model_options:
    st.error("No forecasting model names were found in forecast_results_final.csv.")
    st.stop()


# =========================================================
# PREPARE SHARED DATA AND METRICS
# =========================================================
performance = (
    df.groupby("model_name", as_index=False)
    .agg(
        mae=("mae", "mean"),
        mape=("mape", "mean"),
        forecast_records=("predicted_demand", "count"),
    )
)

ranking = performance.sort_values("mape", ascending=True).reset_index(drop=True)
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
lowest_mape = float(best_row["mape"])

# Monthly historical demand for the overview trend.
historical_monthly = actual_df.copy()
historical_monthly["month"] = historical_monthly["date"].dt.to_period("M").dt.to_timestamp()
monthly_sales = (
    historical_monthly.groupby("month", as_index=False)["daily_demand"]
    .sum()
)

# Heatmap data: average daily demand by month and weekday.
heatmap_source = actual_df.copy()
heatmap_source["month_num"] = heatmap_source["date"].dt.month
heatmap_source["weekday_num"] = heatmap_source["date"].dt.dayofweek

heatmap_values = (
    heatmap_source.pivot_table(
        index="month_num",
        columns="weekday_num",
        values="daily_demand",
        aggfunc="mean",
    )
    .reindex(index=range(1, 13), columns=range(0, 7))
)

month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
weekday_labels = ["Monday", "Tuesday", "Wednesday", "Thursday",
                  "Friday", "Saturday", "Sunday"]


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
# SIDEBAR CONTROLS
# =========================================================
st.sidebar.markdown(
    """
    <div style="padding: 4px 0 8px 0;">
        <div style="font-size:1.22rem;font-weight:800;color:#f1f5fb;">
            Forecast Controls
        </div>
        <div style="font-size:0.76rem;color:#91a4bb;margin-top:5px;line-height:1.45;">
            Select a forecasting model to inspect its saved predictions.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

selected_model = st.sidebar.selectbox(
    "Forecasting Model",
    model_options,
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
        MAE · MAPE

        **Platform**  
        Python + Streamlit
        """
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
# MAIN NAVIGATION
# =========================================================
tab_overview, tab_evaluation, tab_analysis, tab_downloads = st.tabs(
    [
        "📊 Overview",
        "🏆 Model Evaluation",
        "📈 Forecast Analysis",
        "📁 Downloads & Data",
    ]
)


# =========================================================
# TAB 1 — OVERVIEW
# =========================================================
with tab_overview:
    total_demand = actual_df["daily_demand"].sum()
    average_demand = actual_df["daily_demand"].mean()
    highest_demand = actual_df["daily_demand"].max()
    highest_demand_date = actual_df.loc[
        actual_df["daily_demand"].idxmax(), "date"
    ].date()

    # Top row: summary metrics, model performance, and monthly demand.
    top_left, top_center, top_right = st.columns(
        [1.02, 1.38, 1.12],
        gap="small",
    )

    with top_left:
        with st.container(border=True):
            panel_heading("Sales Metrics", "Historical demand overview")
            dashboard_metric("Total Demand", f"{total_demand:,.0f}")
            dashboard_metric("Average Daily Demand", f"{average_demand:,.2f}")
            dashboard_metric("Highest Daily Demand", f"{highest_demand:,.0f}")
            dashboard_metric("Highest Demand Date", str(highest_demand_date))
            dashboard_metric("Historical Records", f"{len(actual_df):,}")
            dashboard_metric("Forecast Records", f"{len(df):,}")
            st.markdown(
                f"""
                <div class="sf-recommendation">
                    <b>Top-performing model</b><br>
                    {html.escape(best_model)} · MAPE {lowest_mape:.2f}%
                </div>
                """,
                unsafe_allow_html=True,
            )

    with top_center:
        with st.container(border=True):
            panel_heading(
                "Forecast Model Performance",
                "Model comparison based on saved MAPE values · lower is better",
            )
            model_chart_data = ranking.sort_values("mape", ascending=True).copy()
            fig_overview_models = px.bar(
                model_chart_data,
                x="mape",
                y="model_name",
                orientation="h",
                text="mape",
                color="model_name",
                color_discrete_map={
                    "ARIMA": "#5b8fd9",
                    "SARIMA": "#3975bd",
                    "Prophet": "#42a6c8",
                    "Random Forest": "#42b99a",
                },
                labels={"mape": "MAPE (%)", "model_name": ""},
            )
            fig_overview_models.update_traces(
                texttemplate="%{text:.2f}%",
                textposition="outside",
                cliponaxis=False,
            )
            fig_overview_models.update_layout(
                showlegend=False,
                xaxis_title="MAPE (%)",
                yaxis_title="",
            )
            style_figure(fig_overview_models, 315)
            st.plotly_chart(
                fig_overview_models,
                use_container_width=True,
                config={"responsive": True, "displayModeBar": False},
            )

    with top_right:
        with st.container(border=True):
            panel_heading(
                "Monthly Demand",
                "Total historical demand by month",
            )
            fig_monthly_overview = px.bar(
                monthly_sales,
                x="month",
                y="daily_demand",
                color_discrete_sequence=["#477fc4"],
                labels={"month": "", "daily_demand": "Demand"},
            )
            fig_monthly_overview.update_traces(
                marker_line_width=0,
                opacity=0.92,
            )
            fig_monthly_overview.update_xaxes(
                dtick="M6",
                tickformat="%b<br>%Y",
                title_text="",
            )
            fig_monthly_overview.update_yaxes(title_text="")
            style_figure(fig_monthly_overview, 315)
            st.plotly_chart(
                fig_monthly_overview,
                use_container_width=True,
                config={"responsive": True, "displayModeBar": False},
            )

    # Bottom row: demand pattern heatmap and selected-model forecast.
    bottom_left, bottom_right = st.columns(
        [1.02, 2.48],
        gap="small",
    )

    with bottom_left:
        with st.container(border=True):
            panel_heading(
                "Demand Pattern",
                "Average daily demand by month and weekday",
            )
            fig_heatmap = px.imshow(
                heatmap_values,
                x=weekday_labels,
                y=month_labels,
                aspect="auto",
                color_continuous_scale=[
                    "#17263b",
                    "#244b79",
                    "#397fc0",
                    "#75b5e7",
                ],
                labels={"x": "", "y": "", "color": "Avg. demand"},
            )
            fig_heatmap.update_layout(
                coloraxis_colorbar=dict(
                    thickness=9,
                    len=0.78,
                    tickfont=dict(size=8, color="#9eafc4"),
                    title=dict(text="", font=dict(size=8)),
                )
            )
            fig_heatmap.update_xaxes(tickfont=dict(size=8), side="bottom")
            fig_heatmap.update_yaxes(tickfont=dict(size=9))
            style_figure(fig_heatmap, 340)
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
                color_discrete_sequence=["#e8bd58"],
                labels={
                    "forecast_date": "",
                    "predicted_demand": "Predicted demand",
                },
            )
            fig_forecast_overview.update_traces(
                line=dict(width=2.2, color="#e8bd58"),
                mode="lines",
            )
            fig_forecast_overview.update_yaxes(title_text="")
            fig_forecast_overview.update_xaxes(title_text="")
            style_figure(fig_forecast_overview, 265)
            st.plotly_chart(
                fig_forecast_overview,
                use_container_width=True,
                config={"responsive": True, "displayModeBar": False},
            )

            forecast_kpis = st.columns(3, gap="small")
            with forecast_kpis[0]:
                st.metric(
                    "Average Forecast",
                    f"{model_data['predicted_demand'].mean():,.1f}",
                )
            with forecast_kpis[1]:
                st.metric(
                    "Peak Forecast",
                    f"{model_data['predicted_demand'].max():,.1f}",
                )
            with forecast_kpis[2]:
                st.metric(
                    "Forecast Records",
                    f"{len(model_data):,}",
                )

    st.caption(
        "Dashboard values are calculated from the historical sales file and saved forecast results. "
        "Regional and product panels from the visual reference were adapted to demand-pattern "
        "and model-performance panels because the current dataset does not contain region or product fields."
    )

# =========================================================
# TAB 2 — MODEL EVALUATION
# =========================================================
with tab_evaluation:
    section_heading(
        "Forecast Model Evaluation",
        "Compare all available models using the MAE and MAPE values stored in the forecast results.",
    )

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
            color_discrete_sequence=["#00aaff", "#38bdf8", "#0ea5e9", "#7dd3fc"],
        )
        fig_mape.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside",
            cliponaxis=False,
        )
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
            color_discrete_sequence=["#00aaff", "#38bdf8", "#0ea5e9", "#7dd3fc"],
        )
        fig_mae.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside",
            cliponaxis=False,
        )
        fig_mae.update_layout(showlegend=False)
        style_figure(fig_mae, 410)
        st.plotly_chart(fig_mae, use_container_width=True, config={"responsive": True, "displayModeBar": False})

    section_heading("Model Performance Summary")
    performance_display = performance.copy()
    performance_display["mae"] = performance_display["mae"].round(2)
    performance_display["mape"] = performance_display["mape"].round(2)
    st.dataframe(
        performance_display,
        use_container_width=True,
        hide_index=True,
    )

    section_heading("Model Performance Ranking")
    ranking_display = ranking.copy()
    ranking_display["mae"] = ranking_display["mae"].round(2)
    ranking_display["mape"] = ranking_display["mape"].round(2)
    st.dataframe(
        ranking_display,
        use_container_width=True,
        hide_index=True,
    )

    section_heading(
        "Forecasting Approach Comparison",
        "Machine-learning and statistical approaches are compared using the same saved metric fields.",
    )

    machine_learning_mae = df.loc[
        df["model_name"] == "Random Forest", "mae"
    ].mean()
    statistical_mae = df.loc[
        df["model_name"].isin(["ARIMA", "SARIMA"]), "mae"
    ].mean()
    machine_learning_mape = df.loc[
        df["model_name"] == "Random Forest", "mape"
    ].mean()
    statistical_mape = df.loc[
        df["model_name"].isin(["ARIMA", "SARIMA"]), "mape"
    ].mean()

    approach_df = pd.DataFrame(
        {
            "Approach": ["Machine Learning Model", "Statistical Model"],
            "mae": [machine_learning_mae, statistical_mae],
            "mape": [machine_learning_mape, statistical_mape],
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
            title="MAPE by Forecasting Approach",
            color_discrete_sequence=["#00aaff", "#38bdf8"],
        )
        fig_approach_mape.update_traces(
            texttemplate="%{text:.2f}%",
            textposition="outside",
            cliponaxis=False,
        )
        fig_approach_mape.update_layout(showlegend=False)
        fig_approach_mape.update_xaxes(title_text="", tickfont=dict(size=10))
        fig_approach_mape.update_yaxes(title_text="MAPE (%)")
        style_figure(fig_approach_mape, 405)
        st.plotly_chart(
            fig_approach_mape,
            use_container_width=True,
            config={"responsive": True, "displayModeBar": False},
        )

    with approach_col2:
        fig_approach_mae = px.bar(
            approach_df,
            x="Approach",
            y="mae",
            color="Approach",
            text="mae",
            title="MAE by Forecasting Approach",
            color_discrete_sequence=["#00aaff", "#38bdf8"],
        )
        fig_approach_mae.update_traces(
            texttemplate="%{text:.2f}",
            textposition="outside",
            cliponaxis=False,
        )
        fig_approach_mae.update_layout(showlegend=False)
        fig_approach_mae.update_xaxes(title_text="", tickfont=dict(size=10))
        fig_approach_mae.update_yaxes(title_text="MAE")
        style_figure(fig_approach_mae, 405)
        st.plotly_chart(
            fig_approach_mae,
            use_container_width=True,
            config={"responsive": True, "displayModeBar": False},
        )

    st.info(
        "Interpretation note: the ranking uses the MAE and MAPE values saved in the CSV. "
        "For a defensible thesis comparison, verify that all four models were evaluated "
        "on the same holdout dates using the same metric calculation."
    )


# =========================================================
# TAB 3 — FORECAST ANALYSIS
# =========================================================
with tab_analysis:
    section_heading(
        f"{selected_model} Forecast Analysis",
        "The selected model controls the forecast charts and forecast summary below.",
    )

    forecast_summary_cols = st.columns(3, gap="medium")
    with forecast_summary_cols[0]:
        st.metric(
            "Average Forecast",
            f"{model_data['predicted_demand'].mean():,.2f}",
        )
    with forecast_summary_cols[1]:
        st.metric(
            "Highest Forecast",
            f"{model_data['predicted_demand'].max():,.2f}",
        )
    with forecast_summary_cols[2]:
        st.metric(
            "Lowest Forecast",
            f"{model_data['predicted_demand'].min():,.2f}",
        )

    section_heading("Actual Demand vs. Forecasted Demand")
    fig_compare = px.line(
        comparison,
        x="forecast_date",
        y=["daily_demand", "predicted_demand"],
        labels={
            "forecast_date": "Date",
            "value": "Demand",
            "variable": "Series",
        },
        title=f"{selected_model}: Actual vs. Forecast",
        color_discrete_map={
            "daily_demand": "#38bdf8",
            "predicted_demand": "#00aaff",
        },
    )
    fig_compare.update_traces(line=dict(width=2))
    style_figure(fig_compare, 430)
    st.plotly_chart(fig_compare, use_container_width=True, config={"responsive": True, "displayModeBar": False})

    section_heading("Monthly Historical Sales Trend")
    fig_month_analysis = px.line(
        monthly_sales,
        x="month",
        y="daily_demand",
        markers=True,
        title="Monthly Sales Demand",
        color_discrete_sequence=["#00aaff"],
        labels={"month": "Month", "daily_demand": "Total Demand"},
    )
    style_figure(fig_month_analysis, 410)
    st.plotly_chart(fig_month_analysis, use_container_width=True, config={"responsive": True, "displayModeBar": False})

    section_heading("Forecast Error Analysis")
    error_data = comparison.dropna(subset=["error"]).copy()
    fig_error = px.line(
        error_data,
        x="forecast_date",
        y="error",
        title=f"{selected_model}: Forecast Error (Actual − Predicted)",
        color_discrete_sequence=["#38bdf8"],
        labels={"forecast_date": "Date", "error": "Forecast Error"},
    )
    fig_error.add_hline(y=0, line_dash="dash", line_color="#94a3b8")
    style_figure(fig_error, 410)
    st.plotly_chart(fig_error, use_container_width=True, config={"responsive": True, "displayModeBar": False})

    section_heading(f"{selected_model} Forecast Trend")
    fig_forecast = px.line(
        model_data,
        x="forecast_date",
        y="predicted_demand",
        title=f"{selected_model} Predicted Demand",
        color_discrete_sequence=["#00aaff"],
        labels={
            "forecast_date": "Forecast Date",
            "predicted_demand": "Predicted Demand",
        },
    )
    fig_forecast.update_traces(line=dict(width=2.5))
    style_figure(fig_forecast, 410)
    st.plotly_chart(fig_forecast, use_container_width=True, config={"responsive": True, "displayModeBar": False})

    if comparison["daily_demand"].notna().any():
        actual_available = comparison.dropna(subset=["daily_demand", "predicted_demand"])
        st.caption(
            f"Actual observations matched to forecast dates: {len(actual_available):,} "
            f"of {len(model_data):,} forecast records."
        )
    else:
        st.warning(
            "No actual demand observations matched the selected model's forecast dates. "
            "The actual-versus-forecast and error charts may therefore be empty."
        )


# =========================================================
# TAB 4 — DOWNLOADS AND DATA
# =========================================================
with tab_downloads:
    section_heading(
        "Download Forecast Results",
        "Export the selected model, all forecast records, or the model-ranking report.",
    )

    selected_csv = model_data.to_csv(index=False).encode("utf-8")
    all_csv = df.to_csv(index=False).encode("utf-8")
    ranking_csv = ranking.to_csv(index=False).encode("utf-8")
    actual_csv = actual_df.to_csv(index=False).encode("utf-8")

    download_cols = st.columns(4, gap="medium")

    with download_cols[0]:
        st.download_button(
            "Selected Forecast CSV",
            selected_csv,
            file_name=f"{selected_model.lower().replace(' ', '_')}_forecast.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with download_cols[1]:
        st.download_button(
            "All Forecast Results",
            all_csv,
            file_name="all_forecast_results.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with download_cols[2]:
        st.download_button(
            "Model Ranking Report",
            ranking_csv,
            file_name="model_ranking_report.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with download_cols[3]:
        st.download_button(
            "Historical Sales Data",
            actual_csv,
            file_name="daily_sales_clean.csv",
            mime="text/csv",
            use_container_width=True,
        )

    st.divider()
    section_heading(
        "Forecast Data",
        f"Saved forecast records for the selected model: {selected_model}.",
    )
    st.dataframe(
        model_data,
        use_container_width=True,
        hide_index=True,
    )

    with st.expander("View Historical Sales Dataset"):
        st.dataframe(
            actual_df,
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# FOOTER
# =========================================================
st.divider()
st.markdown(
    """
    <div style="text-align:center;color:#71859c;font-size:0.76rem;padding:18px 0 8px 0;">
        STA. CRUZ LAGUNA SALES FORECASTING SYSTEM · PYTHON + STREAMLIT
    </div>
    """,
    unsafe_allow_html=True,
)
