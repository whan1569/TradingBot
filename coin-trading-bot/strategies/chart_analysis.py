import os
import pandas as pd
import numpy as np
from utils.data_loader import json_to_dataframe

# 데이터 경로 설정
PROCESSED_DATA_PATH = "data/processed/"

# 디렉토리 생성 함수
def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

ensure_directory(PROCESSED_DATA_PATH)

# 이동평균선 계산 함수
def calculate_moving_average(df, window=14):
    df[f"SMA_{window}"] = df["close"].rolling(window=window).mean()
    return df

# RSI 계산 함수
def calculate_rsi(df, window=14):
    delta = df["close"].diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)
    
    avg_gain = pd.Series(gain).rolling(window=window).mean()
    avg_loss = pd.Series(loss).rolling(window=window).mean()
    
    rs = avg_gain / (avg_loss + 1e-10)
    df["RSI"] = 100 - (100 / (1 + rs))
    return df

# 차트 분석 실행 함수
def analyze_chart(symbol="BTC"):
    file_path = os.path.join(PROCESSED_DATA_PATH, f"price_{symbol}.csv")
    if not os.path.exists(file_path):
        print(f"데이터 파일이 없습니다: {file_path}")
        return None
    
    df = pd.read_csv(file_path)
    df = calculate_moving_average(df, window=14)
    df = calculate_rsi(df, window=14)
    
    output_path = os.path.join(PROCESSED_DATA_PATH, f"chart_analysis_{symbol}.csv")
    df.to_csv(output_path, index=False)
    print(f"차트 분석 데이터 저장 완료: {output_path}")
    return df

if __name__ == "__main__":
    analyze_chart("BTC")
