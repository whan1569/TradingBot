import os
import json
import pandas as pd
from utils.data_loader import json_to_dataframe

# 데이터 경로 설정
RAW_DATA_PATH = "data/raw/"
PROCESSED_DATA_PATH = "data/processed/"

# 디렉토리 생성 함수
def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

ensure_directory(PROCESSED_DATA_PATH)

# 시장 심리 분석 함수
def analyze_market_sentiment(symbol="BTC"):
    file_path = os.path.join(RAW_DATA_PATH, f"lunarcrush_{symbol}.json")
    if not os.path.exists(file_path):
        print(f"데이터 파일이 없습니다: {file_path}")
        return None
    
    df = json_to_dataframe(file_path)
    
    # 공포 & 탐욕 지수 계산 (예제: 소셜 미디어 활동량 기반)
    df["sentiment_score"] = (df["social_volume"] * 0.5 + df["bullish_score"] * 0.5) / (df["social_volume"] + df["bearish_score"] + 1)
    
    # 데이터 저장
    output_path = os.path.join(PROCESSED_DATA_PATH, f"sentiment_{symbol}.csv")
    df.to_csv(output_path, index=False)
    print(f"시장 심리 분석 데이터 저장 완료: {output_path}")
    return df

if __name__ == "__main__":
    analyze_market_sentiment("BTC")
