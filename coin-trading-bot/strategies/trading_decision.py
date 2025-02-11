from strategies.signal_processing import generate_trading_signal

def make_trading_decision():
    """Determines whether to buy, sell, or hold."""
    signal = generate_trading_signal(60, "up")
    print(f"Trading Decision: {signal}")
    return signal

if __name__ == "__main__":
    make_trading_decision()
