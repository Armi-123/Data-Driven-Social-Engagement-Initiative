# File: src/virality/virality_model.py

# Optional: you can use libraries like numpy or sklearn for future ML models
import random

def predict_virality(post_text, likes=0, comments=0, shares=0):
    """
    Predict the virality score of a post based on text and engagement metrics.

    Parameters:
        post_text (str): The content of the post
        likes (int): Number of likes
        comments (int): Number of comments
        shares (int): Number of shares

    Returns:
        dict: A dictionary containing:
            - score (float): Virality score (0 to 100)
            - label (str): Virality label ("low", "medium", "high")
    """
    # Simple heuristic for demo purposes
    # base_score = len(post_text) * 0.1
    # engagement_score = likes * 0.2 + comments * 0.3 + shares * 0.5

    base_score = min(len(post_text) * 0.05, 10)

    engagement_score = (
        likes * 0.15 +
        comments * 0.35 +
        shares * 0.5
    )

    total_score = base_score + engagement_score

    # Normalize to 0-100
    total_score = min(max(total_score, 0), 100)

    # Assign label
    if total_score > 60:
        label = "high"
    elif total_score > 30:
        label = "medium"
    else:
        label = "low"

    return {
        "score": total_score,
        "label": label
    }

# Optional test
if __name__ == "__main__":
    sample_post = "Check out this amazing video!"
    print(predict_virality(sample_post, likes=10, comments=5, shares=2))
