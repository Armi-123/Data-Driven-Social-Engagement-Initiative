"""
Main Pipeline Runner
Data-Driven Social Engagement Initiative
"""

print("Starting Data-Driven Social Engagement Pipeline...")

# Step 1: Data Extraction
from src.data_extraction.fetch_data import fetch_video_data
print("Step 1: Data collection completed.")

# Step 2: Sentiment Analysis
from src.sentiment.sentiment_model import analyze_sentiment
print("Step 2: Sentiment analysis completed.")

# Step 3: Virality Prediction
from src.virality.virality_model import predict_virality
print("Step 3: Virality prediction completed.")

# Step 4: Engagement Recommendation
from src.recommender.engagement_recommender import generate_recommendations
print("Step 4: Engagement recommendations generated.")

# Step 5: Trend Forecasting
from src.forecasting.trend_forecast import forecast_trends
print("Step 5: Trend forecasting completed.")

print("Pipeline executed successfully!")
