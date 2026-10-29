import streamlit as st
import pandas as pd
import plotly.express as px


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="Sales Forecasting System",
    layout="wide"
)


# ==========================================
# PROFESSIONAL UI STYLE
# ==========================================

st.markdown(
"""
<style>
:root {
    --dashboard-blue: #00aaff;
    --dashboard-blue-glow: rgba(0, 170, 255, 0.16);
}

.main {
    background-color: #0e1117;
}

/* Typography */
h1 {
    font-size: 42px !important;
    font-weight: 700;
}
h2 {
    font-size: 32px !important;
    font-weight: 650;
}
h3 {
    font-size: 26px !important;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background-color: #151a24 !important;
    padding: 22px !important;
    border-radius: 14px !important;
    border: 1px solid var(--dashboard-blue) !important;
    min-height: 125px;
    box-shadow: 0 0 8px var(--dashboard-blue-glow);
}
div[data-testid="stMetric"]:focus-within {
    border: 1px solid var(--dashboard-blue) !important;
}
[data-testid="stMetricValue"] {
    font-size: 32px;
    font-weight: 700;
}
[data-testid="stMetricLabel"] {
    font-size: 15px;
}

/* Data tables */
div[data-testid="stDataFrame"],
div[data-testid="stTable"],
.stDataFrame {
    border: 1px solid var(--dashboard-blue) !important;
    border-radius: 10px !important;
    overflow: hidden;
}

/* Plotly chart panels */
div[data-testid="stPlotlyChart"] {
    border: 1px solid var(--dashboard-blue) !important;
    border-radius: 12px !important;
    padding: 8px;
    box-shadow: 0 0 8px var(--dashboard-blue-glow);
}

/* Alerts, including recommendation messages */
div[data-testid="stAlert"],
.stAlert {
    border: 1px solid var(--dashboard-blue) !important;
    border-radius: 12px !important;
}

/* Explicitly bordered Streamlit containers and expanders */
div[data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stExpander"] {
    border: 1px solid var(--dashboard-blue) !important;
    border-radius: 12px !important;
}

/* Forecast Control selectbox — blue border in normal and focused states */
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    border: 1px solid var(--dashboard-blue) !important;
    border-radius: 10px !important;
}
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus,
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within,
div[data-testid="stSelectbox"]:focus-within div[data-baseweb="select"] > div {
    border-color: var(--dashboard-blue) !important;
    box-shadow: 0 0 0 1px var(--dashboard-blue) !important;
}

/* Buttons */
div[data-testid="stDownloadButton"] button,
.stButton button,
button[kind="secondary"],
button[kind="primary"] {
    border: 1px solid var(--dashboard-blue) !important;
    border-radius: 9px !important;
}

/* Input controls, in case they are added later */
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stDateInput"] input {
    border-color: var(--dashboard-blue) !important;
    border-radius: 9px !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111827;
    width: 330px !important;
}
section[data-testid="stSidebar"] > div {
    width: 330px !important;
}
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: white;
}
</style>
""",
unsafe_allow_html=True
)





# ==========================================
# TITLE
# ==========================================


# ==========================================
# PROFESSIONAL HEADER
# ==========================================

st.markdown(
"""
<div style="
width:92%;
margin:20px auto 30px auto;
background:linear-gradient(135deg, #151a24, #1f2937);
padding:38px 42px;
border-radius:18px;
border:1px solid #00aaff;
box-shadow:0px 8px 25px rgba(0,170,255,0.15);
">


<h1 style="
font-size:46px;
font-weight:800;
margin:0;
color:white;
letter-spacing:0.5px;
">
Sales Forecasting System
</h1>



<p style="
font-size:18px;
margin-top:15px;
color:#cbd5e1;
line-height:1.6;
max-width:800px;
">
A comparative forecasting system using ARIMA, SARIMA, Prophet,
and Random Forest models for accurate sales demand prediction.
</p>



<div style="
margin-top:22px;
height:4px;
width:120px;
background:#00aaff;
border-radius:10px;
">
</div>



</div>
""",
unsafe_allow_html=True
)


st.divider()

# ==========================================
# LOAD DATA
# ==========================================


@st.cache_data
def load_forecast():

    df = pd.read_csv(
        "forecast_results_final.csv"
    )

    df["forecast_date"] = pd.to_datetime(
        df["forecast_date"]
    )

    return df



@st.cache_data
def load_actual():

    actual = pd.read_csv(
        "daily_sales_clean.csv"
    )

    actual["date"] = pd.to_datetime(
        actual["date"]
    )

    return actual



df = load_forecast()

actual_df = load_actual()


# ==========================================
# SIDEBAR
# ==========================================


st.sidebar.markdown(
"""
<h2 style='color:white;'>Forecast Control</h2>
""",
unsafe_allow_html=True
)



selected_model = st.sidebar.selectbox(
    "Select Forecasting Model",
    df["model_name"].unique()
)



st.sidebar.divider()



st.sidebar.markdown(
"""
<h3 style='color:white;'>System Details</h3>

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
unsafe_allow_html=True
)



# ==========================================
# SELECTED MODEL DATA
# ==========================================

model_data = df[
    df["model_name"] == selected_model
]

# ==========================================
# DATASET OVERVIEW
# ==========================================

st.markdown(
"""
<h2 style="
margin-top:20px;
margin-bottom:20px;
">
Dataset Overview
</h2>
""",
unsafe_allow_html=True
)


dataset_col1, dataset_col2, dataset_col3 = st.columns(3)


def dashboard_card(title, value, description):

    st.markdown(
    f"""
    <div style="
    background:#151a24;
    padding:22px;
    border-radius:15px;
    border:1px solid #00aaff;
    height:130px;
    box-shadow:0 0 8px rgba(0,170,255,0.15);
    ">

    <p style="
    color:#94a3b8;
    font-size:15px;
    margin-bottom:8px;
    ">
    {title}
    </p>

    <h2 style="
    color:white;
    margin:0;
    ">
    {value}
    </h2>

    <p style="
    color:#64748b;
    font-size:13px;
    margin-top:8px;
    ">
    {description}
    </p>

    </div>
    """,
    unsafe_allow_html=True
    )



with dataset_col1:

    dashboard_card(
        "Historical Sales Records",
        f"{len(actual_df):,}",
        "Available sales transaction records"
    )



with dataset_col2:

    dashboard_card(
        "Forecast Records",
        f"{len(df):,}",
        "Generated prediction records"
    )



with dataset_col3:

    dashboard_card(
        "Models Evaluated",
        df["model_name"].nunique(),
        "Forecasting algorithms tested"
    )


# ==========================================
# SUMMARY CARDS
# ==========================================

st.markdown(
"""
<h2 style="
margin-top:35px;
margin-bottom:20px;
">
Forecast Summary
</h2>
""",
unsafe_allow_html=True
)


col1, col2, col3, col4 = st.columns(4)



def summary_card(title, value, description):

    st.markdown(
    f"""
    <div style="
    background-color:#151a24;
    padding:18px;
    border-radius:15px;
    border:1px solid #00aaff;
    height:120px;
    overflow:hidden;
    ">

    <div style="
    color:#94a3b8;
    font-size:13px;
    margin-bottom:8px;
    ">
    {title}
    </div>


    <div style="
    color:white;
    font-size:26px;
    font-weight:700;
    line-height:1.1;
    ">
    {value}
    </div>


    <div style="
    color:#64748b;
    font-size:11px;
    margin-top:8px;
    ">
    {description}
    </div>


    </div>
    """,
    unsafe_allow_html=True
    )



best_model = (
    df.groupby("model_name")["mape"]
    .mean()
    .idxmin()
)



lowest_mape = (
    df.groupby("model_name")["mape"]
    .mean()
    .min()
)



with col1:

    summary_card(
        "Forecast Records",
        f"{len(df):,}",
        "Generated prediction data"
    )



with col2:

    summary_card(
        "Models Tested",
        df["model_name"].nunique(),
        "Forecasting models evaluated"
    )



with col3:

    summary_card(
        "Recommended Model",
        best_model,
        "Best performing forecasting model"
    )



with col4:

    summary_card(
        "Lowest MAPE",
        f"{lowest_mape:.2f}%",
        "Lowest forecasting error achieved"
    )

# ==========================================
# MODEL PERFORMANCE
# ==========================================


st.subheader(
    "Forecast Model Evaluation"
)



performance = (
    df.groupby("model_name")
    [["mae","mape"]]
    .mean()
    .reset_index()
)



st.dataframe(
    performance,
    use_container_width=True
)



# ==========================================
# MODEL RANKING
# ==========================================


st.subheader(
    "Model Performance Ranking"
)



ranking = performance.sort_values(
    by="mape"
).reset_index(drop=True)



ranking.insert(
    0,
    "Rank",
    range(1,len(ranking)+1)
)



def performance_level(mape):

    if mape < 10:

        return "Excellent"

    elif mape < 20:

        return "Good"

    elif mape < 50:

        return "Acceptable"

    else:

        return "Poor"



ranking["Performance Level"] = (
    ranking["mape"]
    .apply(performance_level)
)



st.dataframe(
    ranking,
    use_container_width=True
)

# ==========================================
# FORECAST RECOMMENDATION
# ==========================================


st.divider()


st.subheader(
    "Forecast Recommendation"
)



best_row = ranking.iloc[0]



rec_col1, rec_col2 = st.columns(2)



with rec_col1:

    st.metric(
        "Recommended Forecast Model",
        best_row["model_name"]
    )



with rec_col2:

    st.metric(
        "Lowest MAPE",
        f"{best_row['mape']:.2f}%"
    )



st.success(
f"""
The recommended forecasting model is {best_row['model_name']}.

It achieved the lowest forecasting error among the evaluated models,
with a Mean Absolute Percentage Error (MAPE) of {best_row['mape']:.2f}%.
"""
)



# ==========================================
# FORECASTING APPROACH COMPARISON
# ==========================================


st.subheader(
    "Forecasting Approach Comparison"
)



approach_df = pd.DataFrame({

    "Approach":[
        "Machine Learning Model",
        "Statistical Model"
    ],

    "mae":[

        df[
            df["model_name"]=="Random Forest"
        ]["mae"].mean(),

        df[
            df["model_name"].isin(
                ["ARIMA","SARIMA"]
            )
        ]["mae"].mean()

    ],

    "mape":[

        df[
            df["model_name"]=="Random Forest"
        ]["mape"].mean(),

        df[
            df["model_name"].isin(
                ["ARIMA","SARIMA"]
            )
        ]["mape"].mean()

    ]

})



st.dataframe(
    approach_df,
    use_container_width=True
)



fig_approach = px.bar(

    approach_df,

    x="Approach",

    y="mape",

    title="Average MAPE Comparison by Forecasting Approach"

)



st.plotly_chart(
    fig_approach,
    use_container_width=True
)




fig_approach_mae = px.bar(

    approach_df,

    x="Approach",

    y="mae",

    title="Average MAE Comparison by Forecasting Approach"

)



st.plotly_chart(
    fig_approach_mae,
    use_container_width=True
)




# ==========================================
# HISTORICAL SALES SUMMARY
# ==========================================


st.divider()


st.subheader(
    "Historical Sales Summary"
)



hist_col1, hist_col2, hist_col3, hist_col4 = st.columns(4)



with hist_col1:

    st.metric(
        "Total Demand",
        f"{actual_df['daily_demand'].sum():,.0f}"
    )



with hist_col2:

    st.metric(
        "Average Daily Demand",
        f"{actual_df['daily_demand'].mean():,.2f}"
    )



with hist_col3:

    st.metric(
        "Highest Demand",
        f"{actual_df['daily_demand'].max():,.0f}"
    )



with hist_col4:

    highest_date = actual_df.loc[
        actual_df["daily_demand"].idxmax()
    ]["date"]


    st.metric(
        "Highest Demand Date",
        str(highest_date.date())
    )





# ==========================================
# ACTUAL VS FORECAST
# ==========================================


st.divider()


st.subheader(
    f"{selected_model}: Actual vs Forecast"
)



comparison = model_data.merge(

    actual_df,

    left_on="forecast_date",

    right_on="date",

    how="left"

)



fig_compare = px.line(

    comparison,

    x="forecast_date",

    y=[
        "daily_demand",
        "predicted_demand"
    ],

    title="Actual Demand Compared with Forecasted Demand"

)



st.plotly_chart(

    fig_compare,

    use_container_width=True

)




# ==========================================
# MONTHLY SALES TREND
# ==========================================


st.subheader(
    "Monthly Historical Sales Trend"
)



monthly_sales = actual_df.copy()



monthly_sales["month"] = (

    monthly_sales["date"]

    .dt.to_period("M")

    .astype(str)

)



monthly_sales = (

    monthly_sales

    .groupby("month")

    ["daily_demand"]

    .sum()

    .reset_index()

)



fig_month = px.line(

    monthly_sales,

    x="month",

    y="daily_demand",

    title="Monthly Sales Demand"

)



st.plotly_chart(

    fig_month,

    use_container_width=True

)




# ==========================================
# ERROR ANALYSIS
# ==========================================


st.subheader(
    "Forecast Error Analysis"
)



comparison["error"] = (

    comparison["daily_demand"]

    -

    comparison["predicted_demand"]

)



fig_error = px.line(

    comparison,

    x="forecast_date",

    y="error",

    title="Forecast Error"

)



st.plotly_chart(

    fig_error,

    use_container_width=True

)




# ==========================================
# FORECAST TREND
# ==========================================


st.subheader(

    f"{selected_model} Forecast Trend"

)



fig_forecast = px.line(

    model_data,

    x="forecast_date",

    y="predicted_demand",

    title=f"{selected_model} Predicted Demand"

)



st.plotly_chart(

    fig_forecast,

    use_container_width=True

)





# ==========================================
# FORECAST SUMMARY
# ==========================================


st.subheader(
    "Forecast Summary"
)



sum1,sum2,sum3 = st.columns(3)



with sum1:

    st.metric(

        "Average Forecast",

        f"{model_data['predicted_demand'].mean():,.2f}"

    )


with sum2:

    st.metric(

        "Highest Forecast",

        f"{model_data['predicted_demand'].max():,.2f}"

    )


with sum3:

    st.metric(

        "Lowest Forecast",

        f"{model_data['predicted_demand'].min():,.2f}"

    )




# ==========================================
# DOWNLOAD SECTION
# ==========================================


st.divider()


st.subheader(
    "Download Forecast Results"
)



selected_csv = model_data.to_csv(

    index=False

).encode("utf-8")



st.download_button(

    "Download Selected Forecast CSV",

    selected_csv,

    file_name=f"{selected_model}_forecast.csv",

    mime="text/csv"

)




all_csv = df.to_csv(

    index=False

).encode("utf-8")



st.download_button(

    "Download All Forecast Results",

    all_csv,

    file_name="all_forecast_results.csv",

    mime="text/csv"

)




ranking_csv = ranking.to_csv(

    index=False

).encode("utf-8")



st.download_button(

    "Download Model Ranking Report",

    ranking_csv,

    file_name="model_ranking_report.csv",

    mime="text/csv"

)



# ==========================================
# FINAL DATA TABLE
# ==========================================


st.subheader(
    "Forecast Data"
)



st.dataframe(

    model_data,

    use_container_width=True

)
