# File: src/forecasting/trend_forecast.py

import random
from datetime import datetime, timedelta

def forecast_trends(posts_data, days=7):
    """
    Forecast engagement trends for the next few days based on past posts.

    Parameters:
        posts_data (list of dict): Each dict contains post info with 'likes', 'comments', 'shares'
        days (int): Number of days to forecast

    Returns:
        list of dict: Each dict contains:
            - date (str): Date of forecast
            - predicted_engagement (float): Predicted engagement score
            - trend_label (str): "upward", "stable", "downward"
    """
    # Simple heuristic: calculate average engagement
    avg_engagement = 0
    if posts_data:
        total = sum(post.get("likes", 0) + post.get("comments", 0) + post.get("shares", 0) for post in posts_data)
        avg_engagement = total / len(posts_data)

    forecasts = []
    today = datetime.today()

    for i in range(1, days + 1):
        # predicted = avg_engagement * random.uniform(0.8, 1.2)  # add some variation
        growth_factor = 1 + (i / days) * 0.1
        predicted = avg_engagement * growth_factor

        if predicted > avg_engagement * 1.05:
            trend = "upward"
        elif predicted < avg_engagement * 0.95:
            trend = "downward"
        else:
            trend = "stable"

        forecasts.append({
            "date": today + timedelta(days=i),
            "predicted_engagement": round(predicted, 2),
            "trend_label": trend
        })

    return forecasts

# Optional test
if __name__ == "__main__":
    sample_posts = [
        {"likes": 10, "comments": 2, "shares": 1},
        {"likes": 15, "comments": 5, "shares": 2},
        {"likes": 8, "comments": 1, "shares": 0}
    ]
    print(forecast_trends(sample_posts))
