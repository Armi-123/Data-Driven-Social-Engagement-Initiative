# File: dashboard/app.py

import sys
import os

# -----------------------------
# Add project root to path
# -----------------------------
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# -----------------------------
# Imports
# -----------------------------
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from src.sentiment.sentiment_model import analyze_sentiment
from src.virality.virality_model import predict_virality
from src.recommender.engagement_recommender import generate_recommendations
from src.forecasting.trend_forecast import forecast_trends
from reports.dashboard_report import generate_dashboard_report

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="Social Engagement Dashboard",
    layout="wide"
)
# -----------------------------
# Custom CSS (KPI Styling)
# -----------------------------
st.markdown("""
<style>
[data-testid="metric-container"] {
    background-color: #0f172a;
    border-radius: 14px;
    padding: 15px;
    box-shadow: 0 0 10px rgba(0,0,0,0.35);
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR CONTROLS
# =====================================================
st.sidebar.title("⚙️ Dashboard Controls")
st.sidebar.markdown("---")

# -----------------------------
# Data Selection
# -----------------------------
st.sidebar.subheader("📂 Data Selection")
uploaded_file = st.sidebar.file_uploader("Upload CSV file", type=["csv"])
use_sample_data = st.sidebar.checkbox("Use Sample Processed Data", value=True)

if uploaded_file:
    df = pd.read_csv(uploaded_file)
elif use_sample_data:
    df = pd.read_csv(
        os.path.join(project_root, "data/processed/processed_social_data.csv")
    )
else:
    st.warning("Please upload a CSV file or select sample data.")
    st.stop()

show_preview = st.sidebar.checkbox("Preview Dataset")

# -----------------------------
# Text Column Selection (ONLY NLP text)
# -----------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("📝 Text Column Selection")

exclude_cols = [
    "video_id", "channel_id", "publish_date",
    "views", "likes", "comments", "shares",
    "sentiment_label", "virality_label",
    "virality_score", "recommendations"
]

text_columns = [
    col for col in df.columns
    if df[col].dtype == "object" and col not in exclude_cols
]

if not text_columns:
    st.error("No valid text columns found for sentiment analysis.")
    st.stop()

text_column = st.sidebar.selectbox(
    "Choose column containing post content",
    options=text_columns
)

df[text_column] = df[text_column].fillna("").astype(str)

# -----------------------------
# Sidebar Data Filters
# -----------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Data Filters")

if "views" in df.columns:
    min_v, max_v = int(df["views"].min()), int(df["views"].max())
    views_range = st.sidebar.slider(
        "Filter by Views", min_v, max_v, (min_v, max_v)
    )
    df = df[df["views"].between(*views_range)]

if "likes" in df.columns:
    min_l, max_l = int(df["likes"].min()), int(df["likes"].max())
    likes_range = st.sidebar.slider(
        "Filter by Likes", min_l, max_l, (min_l, max_l)
    )
    df = df[df["likes"].between(*likes_range)]

if "comments" in df.columns:
    min_c, max_c = int(df["comments"].min()), int(df["comments"].max())
    comments_range = st.sidebar.slider(
        "Filter by Comments", min_c, max_c, (min_c, max_c)
    )
    df = df[df["comments"].between(*comments_range)]


# Publish Date Filter (Timezone-safe)
if "publish_date" in df.columns:
    # Convert to datetime and REMOVE timezone
    df["publish_date"] = pd.to_datetime(
        df["publish_date"],
        errors="coerce"
    ).dt.tz_localize(None)

    min_date = df["publish_date"].min().date()
    max_date = df["publish_date"].max().date()

    start_date, end_date = st.sidebar.date_input(
        "Filter by Publish Date",
        [min_date, max_date]
    )

    # Convert selected dates to datetime (naive)
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)

    df = df[
        (df["publish_date"] >= start_dt) &
        (df["publish_date"] <= end_dt)
    ]



# =====================================================
# MAIN DASHBOARD
# =====================================================

# -----------------------------
# 1️⃣ Title + Description
# -----------------------------
st.title("📊 Data-Driven Social Engagement Dashboard")
st.caption(
    "Analyze sentiment, predict content virality, generate engagement recommendations, "
    "and forecast future social media trends."
)

st.markdown("---")

# -----------------------------
# Run Sentiment & Virality (once)
# -----------------------------
if "sentiment_label" not in df.columns:
    df["sentiment"] = df[text_column].apply(analyze_sentiment)
    df["sentiment_label"] = df["sentiment"].apply(lambda x: x["label"])

for col in ["likes", "comments", "shares"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    else:
        df[col] = 0

if "virality_label" not in df.columns:
    df["virality"] = df.apply(
        lambda row: predict_virality(
            post_text=str(row[text_column]),
            likes=row["likes"],
            comments=row["comments"],
            shares=row["shares"]
        ),
        axis=1
    )
    df["virality_score"] = df["virality"].apply(lambda x: x["score"])
    df["virality_label"] = df["virality"].apply(lambda x: x["label"])

# -----------------------------
# 2️⃣ 📌 Key Engagement Metrics (HERO SECTION)
# -----------------------------
st.markdown("## 📌 Key Engagement Metrics")
st.caption("High-level overview of engagement performance")

col1, col2, col3, col4 = st.columns(4)

col1.metric("📄 Total Posts", len(df))
col2.metric(
    "😊 Positive Sentiment %",
    f"{(df['sentiment_label'] == 'positive').mean() * 100:.1f}%"
)
col3.metric(
    "🔥 High Virality Posts",
    (df["virality_label"] == "High").sum()
)
col4.metric(
    "📊 Avg Virality Score",
    round(df["virality_score"].mean(), 2)
)

st.markdown("### 📺 YouTube Engagement Summary")
c1, c2, c3 = st.columns(3)
c1.metric("👀 Total Views", f"{int(df['views'].sum()):,}")
c2.metric("👍 Total Likes", f"{int(df['likes'].sum()):,}")
c3.metric("💬 Total Comments", f"{int(df['comments'].sum()):,}")

st.markdown("---")



# -----------------------------
# 3️⃣ 🔍 Sentiment Analysis
# -----------------------------
st.subheader("🔍 Sentiment Analysis")

sentiment_counts = df["sentiment_label"].value_counts().reset_index()
sentiment_counts.columns = ["Sentiment", "Count"]

sentiment_fig = px.pie(
    sentiment_counts,
    names="Sentiment",
    values="Count",
    title="Sentiment Distribution",
    color="Sentiment",
    color_discrete_map={
        "positive": "#072ac8",
        "neutral": "#1e96fc",
        "negative": "#a2d6f9"
    }
)
st.plotly_chart(sentiment_fig, use_container_width=True)

st.markdown("---")
# -----------------------------
# Sentiment Filter (SAFE DEFAULT)
# -----------------------------
if "sentiment_label" in df.columns:
    sentiment_filter = st.sidebar.multiselect(
        "Filter by Sentiment",
        options=df["sentiment_label"].unique().tolist(),
        default=df["sentiment_label"].unique().tolist()
    )
    df = df[df["sentiment_label"].isin(sentiment_filter)]
else:
    sentiment_filter = []

# -----------------------------
# 4️⃣ 🚀 Virality Prediction
# -----------------------------
st.subheader("🚀 Virality Prediction")

virality_scatter_fig = px.scatter(
    df,
    x="sentiment_label",
    y="virality_score",
    color="sentiment_label",
    size="views",
    title="Virality vs Sentiment",
    hover_data=["likes", "comments"],
    color_discrete_map={
        "positive": "#072ac8",
        "neutral": "#1e96fc",
        "negative": "#a2d6f9"
    }
)

st.plotly_chart(virality_scatter_fig, use_container_width=True)

st.markdown("---")

# -----------------------------
# 5️⃣ 💡 Engagement Recommendations
# -----------------------------
st.subheader("💡 Engagement Recommendations")

if "recommendations" not in df.columns:
    df["recommendations"] = df.apply(
        lambda row: generate_recommendations(
            post_text=str(row[text_column]),
            sentiment=row["sentiment"],
            virality=row["virality"]
        ),
        axis=1
    )

st.dataframe(df[[text_column, "recommendations"]].head(10))

st.markdown("---")

# -----------------------------
# 6️⃣ 📈 Trend Forecasting
# -----------------------------
st.subheader("📈 Engagement Trend Forecasting")

forecast_days = st.slider("Forecast duration (days)", 3, 14, 7)

forecast = forecast_trends(df.to_dict("records"), days=forecast_days)
forecast_df = pd.DataFrame(forecast)

forecast_fig = px.line(
    forecast_df,
    x="date",
    y="predicted_engagement",
    title="Engagement Forecast",
    markers=True
)

forecast_fig.update_traces(
    line=dict(color="#3b82f6", width=3),
    marker=dict(color="#3b82f6")
)


st.plotly_chart(forecast_fig, use_container_width=True)

st.markdown("---")
# -----------------------------
# 📌 Auto-Generated Insights
# -----------------------------
st.subheader("📌 Key Insights")

positive_pct = (df["sentiment_label"] == "positive").mean() * 100
neutral_pct = (df["sentiment_label"] == "neutral").mean() * 100
avg_virality = df["virality_score"].mean()

st.info(
    f"Positive sentiment posts account for {positive_pct:.1f}% of content, "
    f"while neutral posts dominate at {neutral_pct:.1f}%."
)

st.info(
    f"The average virality score across posts is {avg_virality:.2f}, "
    "indicating consistent engagement behavior across sentiments."
)

# -----------------------------
# 📌 Forecast Insight (SAFE & FINAL)
# -----------------------------
if (
    "forecast_df" in locals()
    and isinstance(forecast_df, pd.DataFrame)
    and not forecast_df.empty
    and "predicted_engagement" in forecast_df.columns
):
    idx = forecast_df["predicted_engagement"].idxmax()

    peak_day = pd.to_datetime(
        forecast_df.loc[idx, "date"]
    ).strftime("%d %b %Y")

    peak_value = int(forecast_df.loc[idx, "predicted_engagement"])

    st.success(
        f"📈 Based on historical engagement patterns, the highest expected "
        f"engagement is around **{peak_value:,} interactions** on "
        f"**{peak_day}**. Planning high-impact posts on this day may improve reach."
    )
else:
    st.info(
        "📊 Forecast insights will appear once sufficient engagement data "
        "is available."
    )



# -----------------------------
# 7️⃣ Dataset Preview / Export
# -----------------------------
if show_preview:
    st.subheader("📄 Dataset Preview")
    st.dataframe(df.head(10))

st.subheader("⬇️ Export Results")
st.download_button(
    "Download Processed Data (CSV)",
    df.to_csv(index=False).encode("utf-8"),
    "social_engagement_dashboard.csv",
    "text/csv"
)

# -----------------------------
# SAFE DEFAULTS (PREVENT NameError)
# -----------------------------
sentiment_filter = []
views_range = None
likes_range = None
comments_range = None
start_date = None
end_date = None

# -----------------------------
# Dashboard Summary Report
# -----------------------------
if st.button("📄 Generate Dashboard Report (PDF)"):

    report_path = generate_dashboard_report(
    df=df,
    filters={
        "Views Range": f"{views_range[0]} – {views_range[1]}" if views_range else "All",
        "Likes Range": f"{likes_range[0]} – {likes_range[1]}" if likes_range else "All",
        "Comments Range": f"{comments_range[0]} – {comments_range[1]}" if comments_range else "All",
        "Sentiment": ", ".join(sentiment_filter) if sentiment_filter else "All",
        "Date Range": f"{start_date} to {end_date}" if start_date and end_date else "All",
        "Records Selected": len(df)
    },
    charts={
        "sentiment": sentiment_fig,
        "virality": virality_scatter_fig,
        "forecast": forecast_fig,
        "forecast_df": forecast_df
    },
    forecast_df=forecast_df,
    prepared_by="admin"
)


    st.success("Dashboard report generated successfully!")

    with open(report_path, "rb") as f:
        st.download_button(
            label="⬇️ Download Report",
            data=f,
            file_name=os.path.basename(report_path),
            mime="application/pdf"
        )



st.success("Dashboard loaded successfully and ready for analysis ✅")
