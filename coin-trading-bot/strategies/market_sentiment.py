import requests

def get_fear_greed_index():
    """Fetches the Fear & Greed Index from an external API."""
    url = "https://api.alternative.me/fng/"
    response = requests.get(url).json()
    return response["data"][0]["value"]

def analyze_sentiment():
    """Analyzes market sentiment based on various factors."""
    fear_greed = get_fear_greed_index()
    print(f"Fear & Greed Index: {fear_greed}")
    return fear_greed

if __name__ == "__main__":
    analyze_sentiment()
