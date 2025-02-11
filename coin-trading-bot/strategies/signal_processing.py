import json
import pandas as pd

def load_strategy_config(config_path="config/strategy_config.json"):
    with open(config_path, "r") as file:
        return json.load(file)

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_bollinger_bands(data, window, std_dev):
    rolling_mean = data.rolling(window=window).mean()
    rolling_std = data.rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * std_dev)
    lower_band = rolling_mean - (rolling_std * std_dev)
    return rolling_mean, upper_band, lower_band

def calculate_moving_average(data, short_window, long_window):
    short_ma = data.rolling(window=short_window).mean()
    long_ma = data.rolling(window=long_window).mean()
    return short_ma, long_ma

def generate_trade_signal(data, config):
    rsi = calculate_rsi(data["close"], window=14)
    short_ma, long_ma = calculate_moving_average(data["close"], 
                                                 config["moving_average"]["short_window"], 
                                                 config["moving_average"]["long_window"])
    _, upper_band, lower_band = calculate_bollinger_bands(data["close"], 
                                                          config["bollinger_bands"]["window"], 
                                                          config["bollinger_bands"]["std_dev"])
    
    buy_signal = (rsi < config["rsi_threshold"]["oversold"]) & (data["close"] < lower_band) & (short_ma > long_ma)
    sell_signal = (rsi > config["rsi_threshold"]["overbought"]) & (data["close"] > upper_band) & (short_ma < long_ma)
    
    return buy_signal, sell_signal

if __name__ == "__main__":
    config = load_strategy_config()
    data = pd.read_csv("data/processed/market_data.csv")
    buy_signal, sell_signal = generate_trade_signal(data, config)
    print("Buy Signals:", buy_signal)
    print("Sell Signals:", sell_signal)
