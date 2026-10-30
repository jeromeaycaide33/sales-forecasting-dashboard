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
        --blue: #00aaff;
        --blue-light: #38bdf8;
        --blue-glow: rgba(0, 170, 255, 0.16);
        --page: #0b1220;
        --panel: #121d2d;
        --panel-2: #17263a;
        --text: #f8fafc;
        --muted: #9fb0c5;
    }

    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(0,170,255,0.08), transparent 28%),
            linear-gradient(180deg, #0b1220 0%, #0e1726 100%);
        color: var(--text);
    }

    .block-container {
        max-width: 1600px;
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        padding-left: clamp(1.25rem, 3vw, 3rem);
        padding-right: clamp(1.25rem, 3vw, 3rem);
    }

    /* Consistent breathing room between Streamlit sections and columns */
    div[data-testid="stHorizontalBlock"] {
        gap: 1.5rem;
        align-items: stretch;
    }

    div[data-testid="stTabs"] [data-baseweb="tab-panel"] {
        padding-top: 1.25rem;
    }

    div[data-testid="stPlotlyChart"] {
        overflow: hidden !important;
    }

    div[data-testid="stPlotlyChart"] > div {
        overflow: hidden !important;
    }

    h1, h2, h3, p, label {
        color: var(--text);
    }

    h1 { font-size: 2.15rem !important; font-weight: 800 !important; }
    h2 { font-size: 1.55rem !important; font-weight: 750 !important; }
    h3 { font-size: 1.18rem !important; font-weight: 700 !important; }

    /* Hero header */
    .sf-hero {
        position: relative;
        overflow: hidden;
        background: linear-gradient(120deg, #14243a 0%, #172b43 52%, #102034 100%);
        border: 1px solid var(--blue);
        border-radius: 20px;
        padding: 30px 34px;
        margin: 0 0 1.15rem 0;
        box-shadow: 0 12px 32px rgba(0,170,255,0.10);
    }

    .sf-hero:after {
        content: "";
        position: absolute;
        width: 220px;
        height: 220px;
        right: -75px;
        top: -105px;
        border-radius: 50%;
        border: 1px solid rgba(56,189,248,0.25);
        box-shadow: 0 0 0 22px rgba(56,189,248,0.035),
                    0 0 0 48px rgba(56,189,248,0.025);
        pointer-events: none;
    }

    .sf-eyebrow {
        color: var(--blue-light);
        font-size: 0.76rem;
        font-weight: 800;
        letter-spacing: 0.17em;
        text-transform: uppercase;
        margin-bottom: 0.65rem;
    }

    .sf-title {
        color: #ffffff;
        font-size: 2.25rem;
        font-weight: 850;
        line-height: 1.12;
        margin: 0;
    }

    .sf-subtitle {
        color: #c4d2e2;
        font-size: 0.98rem;
        line-height: 1.6;
        max-width: 850px;
        margin: 0.8rem 0 0 0;
    }

    .sf-accent {
        width: 105px;
        height: 4px;
        border-radius: 20px;
        background: var(--blue);
        margin-top: 1.1rem;
        box-shadow: 0 0 14px rgba(0,170,255,0.45);
    }

    /* Advanced KPI cards */
    .sf-kpi {
        background: linear-gradient(145deg, #17263a 0%, #111c2b 100%);
        border: 1px solid var(--blue);
        border-radius: 15px;
        padding: 18px 19px;
        min-height: 137px;
        box-shadow: 0 0 13px rgba(0,170,255,0.075);
    }

    .sf-kpi-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 8px;
        margin-bottom: 13px;
    }

    .sf-kpi-label {
        color: #a9bad0;
        font-size: 0.79rem;
        font-weight: 650;
        line-height: 1.35;
    }

    .sf-kpi-icon {
        color: var(--blue-light);
        font-size: 1.2rem;
    }

    .sf-kpi-value {
        color: #ffffff;
        font-size: 1.72rem;
        line-height: 1.15;
        font-weight: 850;
        overflow-wrap: anywhere;
    }

    .sf-kpi-note {
        color: #7f93aa;
        font-size: 0.73rem;
        line-height: 1.4;
        margin-top: 9px;
    }

    /* Section labels */
    .sf-section-label {
        color: #eaf6ff;
        font-size: 1.12rem;
        font-weight: 750;
        margin: 1.7rem 0 0.9rem 0;
    }

    .sf-section-caption {
        color: #91a5bc;
        font-size: 0.82rem;
        margin-top: -0.35rem;
        margin-bottom: 0.8rem;
    }

    /* Streamlit metric cards */
    div[data-testid="stMetric"] {
        background: var(--panel);
        border: 1px solid var(--blue) !important;
        border-radius: 13px !important;
        padding: 15px 17px;
        min-height: 105px;
        box-shadow: 0 0 9px rgba(0,170,255,0.07);
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted) !important;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    /* Chart and table frames */
    div[data-testid="stPlotlyChart"] {
        background: #101b2a;
        border: 1px solid var(--blue) !important;
        border-radius: 13px !important;
        padding: 10px 12px 8px;
        margin: 0.35rem 0 1.25rem 0;
        overflow: hidden !important;
        box-shadow: 0 0 10px rgba(0,170,255,0.055);
    }

    div[data-testid="stDataFrame"],
    div[data-testid="stTable"],
    .stDataFrame {
        border: 1px solid var(--blue) !important;
        border-radius: 11px !important;
        overflow: hidden;
    }

    /* Alerts, containers and expanders */
    div[data-testid="stAlert"],
    .stAlert,
    div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stExpander"] {
        border: 1px solid var(--blue) !important;
        border-radius: 12px !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #101b2a;
        border-right: 1px solid rgba(0,170,255,0.42);
        min-width: 300px;
    }

    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }

    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        border: 1px solid var(--blue) !important;
        border-radius: 10px !important;
        background: #111d2c;
    }

    /* Tabs */
    div[data-testid="stTabs"] [role="tablist"] {
        gap: 7px;
        border-bottom: 1px solid rgba(0,170,255,0.28);
        padding-bottom: 7px;
    }

    div[data-testid="stTabs"] button[role="tab"] {
        background: #142237;
        border: 1px solid #2b4058;
        border-radius: 10px 10px 7px 7px;
        color: #c6d4e4;
        font-weight: 650;
        padding: 9px 14px;
    }

    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background: #12304a;
        border: 1px solid var(--blue);
        color: #ffffff;
        box-shadow: 0 0 9px rgba(0,170,255,0.12);
    }

    /* Buttons and controls */
    div[data-testid="stDownloadButton"] button,
    .stButton button {
        border: 1px solid var(--blue) !important;
        border-radius: 9px !important;
    }

    hr {
        border-color: rgba(0,170,255,0.25) !important;
    }

    @media (max-width: 900px) {
        .sf-hero { padding: 23px; }
        .sf-title { font-size: 1.75rem; }
        .sf-kpi { min-height: 120px; }
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


def style_figure(fig, height: int = 410):
    """Apply consistent chart spacing, title placement, and readable axes."""
    fig.update_layout(
        template="plotly_dark",
        height=height,
        autosize=True,
        paper_bgcolor="#101b2a",
        plot_bgcolor="#101b2a",
        font=dict(color="#e5edf7", family="Arial", size=11),
        title=dict(
            x=0.02,
            xanchor="left",
            y=0.98,
            yanchor="top",
            font=dict(size=15, color="#f8fafc"),
        ),
        # Extra top space separates chart titles from legends.
        margin=dict(l=58, r=35, t=105, b=65),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            orientation="h",
            yanchor="bottom",
            y=1.08,
            xanchor="right",
            x=0.98,
            font=dict(size=10),
            itemwidth=75,
        ),
    )
    fig.update_xaxes(
        title_font=dict(size=11),
        tickfont=dict(size=10),
        automargin=True,
        gridcolor="rgba(148,163,184,0.12)",
        zerolinecolor="rgba(148,163,184,0.18)",
    )
    fig.update_yaxes(
        title_font=dict(size=11),
        tickfont=dict(size=10),
        automargin=True,
        gridcolor="rgba(148,163,184,0.12)",
        zerolinecolor="rgba(148,163,184,0.18)",
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
        <div class="sf-eyebrow">Analytics · Forecasting · Decision Support</div>
        <div class="sf-title">Sales Forecasting System</div>
        <p class="sf-subtitle">
            A comparative forecasting system using ARIMA, SARIMA, Prophet,
            and Random Forest models for sales-demand analysis and prediction.
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
    <div style="padding: 5px 0 10px 0;">
        <div style="font-size:1.42rem;font-weight:850;color:#f8fafc;">
            Forecast Control
        </div>
        <div style="font-size:0.82rem;color:#9fb0c5;margin-top:5px;">
            Choose a model to update forecast analysis
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

selected_model = st.sidebar.selectbox(
    "Select Forecasting Model",
    model_options,
    key="forecast_model_selector",
)

st.sidebar.divider()
st.sidebar.markdown(
    """
    <h3>System Details</h3>
    <b>Dataset</b><br>
    Sta. Cruz Laguna Sales Dataset<br><br>
    <b>Forecasting Models</b><br>
    ARIMA<br>
    SARIMA<br>
    Prophet<br>
    Random Forest<br><br>
    <b>Evaluation Metrics</b><br>
    MAE<br>
    MAPE<br><br>
    <b>Platform</b><br>
    Python + Streamlit
    """,
    unsafe_allow_html=True,
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
    section_heading(
        "Dashboard Overview",
        "A quick summary of historical demand and saved forecasting results.",
    )

    total_demand = actual_df["daily_demand"].sum()
    average_demand = actual_df["daily_demand"].mean()
    highest_demand = actual_df["daily_demand"].max()
    highest_demand_date = actual_df.loc[
        actual_df["daily_demand"].idxmax(), "date"
    ].date()

    kpi_cols = st.columns(4, gap="medium")
    with kpi_cols[0]:
        kpi_card(
            "Historical Sales Records",
            f"{len(actual_df):,}",
            "Daily demand observations",
            "▦",
        )
    with kpi_cols[1]:
        kpi_card(
            "Forecast Records",
            f"{len(df):,}",
            "Saved predictions across all models",
            "⌁",
        )
    with kpi_cols[2]:
        kpi_card(
            "Models Evaluated",
            str(df["model_name"].nunique()),
            "Available forecasting algorithms",
            "◈",
        )
    with kpi_cols[3]:
        kpi_card(
            "Recommended Model",
            best_model,
            f"Lowest saved average MAPE: {lowest_mape:.2f}%",
            "★",
        )

    section_heading("Historical Demand Snapshot")
    hist_cols = st.columns(4, gap="medium")
    with hist_cols[0]:
        st.metric("Total Demand", f"{total_demand:,.0f}")
    with hist_cols[1]:
        st.metric("Average Daily Demand", f"{average_demand:,.2f}")
    with hist_cols[2]:
        st.metric("Highest Daily Demand", f"{highest_demand:,.0f}")
    with hist_cols[3]:
        st.metric("Highest Demand Date", str(highest_demand_date))

    section_heading(
        "Monthly Historical Sales Trend",
        "Total daily demand aggregated by calendar month.",
    )
    fig_monthly_overview = px.area(
        monthly_sales,
        x="month",
        y="daily_demand",
        title="Monthly Sales Demand",
        color_discrete_sequence=["#00aaff"],
    )
    fig_monthly_overview.update_traces(
        line=dict(color="#38bdf8", width=2.5),
        fillcolor="rgba(0,170,255,0.16)",
    )
    style_figure(fig_monthly_overview, 410)
    st.plotly_chart(fig_monthly_overview, use_container_width=True, config={"responsive": True, "displayModeBar": False})

    section_heading(
        "Sales Demand Heatmap",
        "Average daily demand by month and day of the week. Brighter cells indicate higher average demand.",
    )
    fig_heatmap = px.imshow(
        heatmap_values,
        x=weekday_labels,
        y=month_labels,
        aspect="auto",
        color_continuous_scale=["#102337", "#075985", "#00aaff", "#bae6fd"],
        labels={
            "x": "Day of Week",
            "y": "Month",
            "color": "Average Demand",
        },
        title="Average Demand by Month and Weekday",
    )
    style_figure(fig_heatmap, 440)
    st.plotly_chart(fig_heatmap, use_container_width=True, config={"responsive": True, "displayModeBar": False})

    section_heading(
        "Model Performance Snapshot",
        "Models ranked by their saved average MAPE values.",
    )
    fig_overview_models = px.bar(
        ranking.sort_values("mape", ascending=True),
        x="model_name",
        y="mape",
        color="model_name",
        text="mape",
        title="MAPE Comparison Across Forecasting Models",
        color_discrete_sequence=["#00aaff", "#38bdf8", "#0ea5e9", "#7dd3fc"],
    )
    fig_overview_models.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside",
        cliponaxis=False,
    )
    fig_overview_models.update_layout(showlegend=False)
    style_figure(fig_overview_models, 390)
    st.plotly_chart(fig_overview_models, use_container_width=True, config={"responsive": True, "displayModeBar": False})

    st.success(
        f"Based on the saved evaluation results, {best_model} has the lowest "
        f"average MAPE at {lowest_mape:.2f}%. This recommendation reflects the "
        "metrics currently stored in forecast_results_final.csv."
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
        Sales Forecasting System · Python & Streamlit · ARIMA · SARIMA · Prophet · Random Forest
    </div>
    """,
    unsafe_allow_html=True,
)
