# File: src/recommender/engagement_recommender.py

def generate_recommendations(post_text, sentiment, virality):
    """
    Generate engagement recommendations based on sentiment and virality.

    Parameters:
        post_text (str): Content of the post
        sentiment (dict): Output from analyze_sentiment(), e.g., {"polarity": 0.5, "label": "positive"}
        virality (dict): Output from predict_virality(), e.g., {"score": 45, "label": "medium"}

    Returns:
        list: A list of actionable recommendations (strings)
    """
    recommendations = []

    # Recommendation based on sentiment
    if sentiment["label"] == "negative":
        recommendations.append("Consider rephrasing content to be more positive.")
    elif sentiment["label"] == "neutral":
        recommendations.append("Add engaging questions or emojis to increase interest.")
    else:
        recommendations.append("Positive sentiment detected — good job!")

    # Recommendation based on virality
    if virality["label"] == "low":
        recommendations.append("Boost post visibility with hashtags or paid promotion.")
    elif virality["label"] == "medium":
        recommendations.append("Share during peak engagement hours to maximize reach.")
    else:
        recommendations.append("High virality potential — consider cross-posting!")

    return recommendations

# Optional test
if __name__ == "__main__":
    sample_text = "Excited to launch our new product!"
    sample_sentiment = {"polarity": 0.7, "label": "positive"}
    sample_virality = {"score": 65, "label": "high"}

    print(generate_recommendations(sample_text, sample_sentiment, sample_virality))
