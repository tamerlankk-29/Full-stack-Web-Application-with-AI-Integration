"""
Sentiment analysis module for analyzing the sentiment of text content.
Uses TextBlob for sentiment analysis.
"""
from textblob import TextBlob
import re

def clean_text(text):
    """
    Clean text by removing special characters, URLs, etc.
    
    Args:
        text (str): The text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Remove special characters and numbers
    text = re.sub(r'[^\w\s]', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def analyze_sentiment(text):
    """
    Analyze the sentiment of a text using TextBlob.

    Args:
        text (str): The text to analyze

    Returns:
        dict: A dictionary containing sentiment information:
            - polarity: float between -1 (negative) and 1 (positive)
            - subjectivity: float between 0 (objective) and 1 (subjective)
            - sentiment: str, one of 'positive', 'negative', or 'neutral'
    """
    if not text:
        return {
            'polarity': 0.0,
            'subjectivity': 0.0,
            'sentiment': 'neutral'
        }
    
    # Clean the text
    cleaned_text = clean_text(text)
    
    # Create a TextBlob object
    blob = TextBlob(cleaned_text)
    
    # Get sentiment
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    
    # Determine sentiment category
    if polarity > 0.1:
        sentiment = 'positive'
    elif polarity < -0.1:
        sentiment = 'negative'
    else:
        sentiment = 'neutral'
    
    return {
        'polarity': polarity,
        'subjectivity': subjectivity,
        'sentiment': sentiment
    }

def get_sentiment_emoji(sentiment):
    """
    Get an emoji representing the sentiment.
    
    Args:
        sentiment (str): The sentiment category ('positive', 'negative', or 'neutral')
        
    Returns:
        str: An emoji representing the sentiment
    """
    emoji_map = {
        'positive': '😊',
        'negative': '😞',
        'neutral': '😐'
    }
    
    return emoji_map.get(sentiment, '😐')
