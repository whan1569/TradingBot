import os
import json
import pandas as pd
from utils.api_connector import get_binance_price, get_lunarcrush_data

# 데이터 저장 경로 설정
RAW_DATA_PATH = "data/raw/"
PROCESSED_DATA_PATH = "data/processed/"

# 디렉토리 생성 함수
def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

ensure_directory(RAW_DATA_PATH)
ensure_directory(PROCESSED_DATA_PATH)

# Binance 가격 데이터 저장
def save_binance_price(symbol="BTCUSDT"):
    data = get_binance_price(symbol)
    file_path = os.path.join(RAW_DATA_PATH, f"binance_{symbol}.json")
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Binance {symbol} 가격 데이터 저장 완료: {file_path}")

# LunarCrush 심리 데이터 저장
def save_lunarcrush_data(symbol="BTC"):
    data = get_lunarcrush_data(symbol)
    file_path = os.path.join(RAW_DATA_PATH, f"lunarcrush_{symbol}.json")
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"LunarCrush {symbol} 심리 데이터 저장 완료: {file_path}")

# JSON 데이터를 Pandas DataFrame으로 변환
def json_to_dataframe(json_file):
    with open(json_file, "r") as f:
        data = json.load(f)
    return pd.DataFrame([data])

if __name__ == "__main__":
    save_binance_price()
    save_lunarcrush_data()
    
    # 데이터프레임 변환 테스트
    btc_price_df = json_to_dataframe(os.path.join(RAW_DATA_PATH, "binance_BTCUSDT.json"))
    print(btc_price_df.head())
