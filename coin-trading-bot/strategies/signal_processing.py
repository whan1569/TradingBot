def generate_trading_signal(sentiment, price_trend):
    """Generates a trading signal based on sentiment and price trend."""
    if sentiment > 50 and price_trend == "up":
        return "BUY"
    elif sentiment < 50 and price_trend == "down":
        return "SELL"
    return "HOLD"

if __name__ == "__main__":
    print(generate_trading_signal(60, "up"))
