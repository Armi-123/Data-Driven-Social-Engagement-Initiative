# File: src/sentiment/sentiment_model.py

# Optional: you can use libraries like TextBlob or Vader for sentiment analysis
from textblob import TextBlob

def analyze_sentiment(text):
    """
    Analyze the sentiment of a text string.
    
    Parameters:
        text (str): The input text to analyze.
    
    Returns:
        dict: A dictionary containing:
            - polarity (float): sentiment score from -1 (negative) to 1 (positive)
            - subjectivity (float): subjectivity score from 0 (objective) to 1 (subjective)
            - label (str): sentiment label ("positive", "neutral", "negative")
    """
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    
    # Simple label based on polarity
    if polarity > 0.1:
        label = "positive"
    elif polarity < -0.1:
        label = "negative"
    else:
        label = "neutral"
    
    return {
        "polarity": polarity,
        "subjectivity": subjectivity,
        "label": label
    }

# Optional: test the function when running this file directly
if __name__ == "__main__":
    sample_text = "I love using ChatGPT! It's amazing."
    print(analyze_sentiment(sample_text))
