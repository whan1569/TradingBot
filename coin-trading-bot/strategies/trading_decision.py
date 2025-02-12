import json
import pandas as pd
from utils.config_loader import load_strategy_config
from strategies.market_sentiment import analyze_market_sentiment
from strategies.chart_analysis import calculate_moving_average, calculate_rsi


def load_trade_signals():
    """signals.json에서 트레이딩 신호 로드"""
    try:
        with open("data/signals.json", "r") as file:
            signals = json.load(file)
        return signals
    except FileNotFoundError:
        print("[Error] signals.json 파일을 찾을 수 없습니다.")
        return None

def make_trading_decision():
    """최종 트레이딩 결정"""
    config = load_strategy_config()
    signals = load_trade_signals()
    
    if not signals:
        return None
    
    # 최신 신호 가져오기
    last_signal = signals[-1]
    
    # 시장 심리 분석
    market_sentiment = analyze_market_sentiment()
    
    # 차트 분석 값 로드 (예제: 이동평균선, RSI)
    price_data = pd.read_csv("data/processed/chart_analysis_BTC.csv")
    short_ma = calculate_moving_average(price_data, config["moving_average"]["short_window"])
    long_ma = calculate_moving_average(price_data, config["moving_average"]["long_window"])
    rsi = calculate_rsi(price_data, 14)
    
    # 트레이딩 결정 로직
    decision = "HOLD"
    
    if last_signal["type"] == "BUY" and market_sentiment > 50 and short_ma.iloc[-1] > long_ma.iloc[-1] and rsi.iloc[-1] < config["rsi_threshold"]["overbought"]:
        decision = "LONG"
    elif last_signal["type"] == "SELL" and market_sentiment < 50 and short_ma.iloc[-1] < long_ma.iloc[-1] and rsi.iloc[-1] > config["rsi_threshold"]["oversold"]:
        decision = "SHORT"
    
    return decision

if __name__ == "__main__":
    trade_decision = make_trading_decision()
    print(f"[Decision] 최종 트레이딩 결정: {trade_decision}")
