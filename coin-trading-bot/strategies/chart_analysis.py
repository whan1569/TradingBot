import pandas as pd

def calculate_moving_averages(data, short_window=10, long_window=50):
    """단기 및 장기 이동평균선을 계산합니다."""
    data['SMA_Short'] = data['close'].rolling(window=short_window).mean()
    data['SMA_Long'] = data['close'].rolling(window=long_window).mean()
    return data

def generate_signals(data):
    """이동평균선 교차 전략에 기반한 매수/매도 신호 생성."""
    data['Signal'] = 0  # 기본값 (0: 보유)
    data.loc[data['SMA_Short'] > data['SMA_Long'], 'Signal'] = 1  # 매수 신호
    data.loc[data['SMA_Short'] < data['SMA_Long'], 'Signal'] = -1  # 매도 신호
    return data
