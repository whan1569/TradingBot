def analyze_news_sentiment(news_text):
    """Analyzes sentiment of news articles."""
    return "Positive" if "bullish" in news_text else "Negative"

if __name__ == "__main__":
    print(analyze_news_sentiment("The market looks bullish today!"))
