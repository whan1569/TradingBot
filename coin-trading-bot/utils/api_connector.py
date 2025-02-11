import requests
import time
import hmac
import hashlib
import json
from urllib.parse import urlencode
from utils.config_loader import get_api_keys

# API 키 로드
api_keys = get_api_keys()
BINANCE_API_KEY = api_keys["binance"]["api_key"]
BINANCE_API_SECRET = api_keys["binance"]["api_secret"]
LUNARCRUSH_API_KEY = api_keys["lunarcrush"]["api_key"]

BINANCE_BASE_URL = "https://api.binance.com"
LUNARCRUSH_BASE_URL = "https://api.lunarcrush.com/v2"

# Binance 공용 데이터 가져오기
def get_binance_price(symbol="BTCUSDT"):
    url = f"{BINANCE_BASE_URL}/api/v3/ticker/price"
    params = {"symbol": symbol}
    response = requests.get(url, params=params)
    return response.json()

# Binance 서명된 요청 만들기
def sign_request(params, secret):
    query_string = urlencode(params)
    signature = hmac.new(secret.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    params["signature"] = signature
    return params

# Binance 계정 정보 가져오기
def get_binance_account_info():
    endpoint = "/api/v3/account"
    timestamp = int(time.time() * 1000)
    params = {"timestamp": timestamp}
    headers = {"X-MBX-APIKEY": BINANCE_API_KEY}
    signed_params = sign_request(params, BINANCE_API_SECRET)
    url = f"{BINANCE_BASE_URL}{endpoint}?{urlencode(signed_params)}"
    response = requests.get(url, headers=headers)
    return response.json()

# LunarCrush 데이터 가져오기
def get_lunarcrush_data(symbol="BTC"):
    url = f"{LUNARCRUSH_BASE_URL}/assets"
    params = {"symbol": symbol, "key": LUNARCRUSH_API_KEY}
    response = requests.get(url, params=params)
    return response.json()

if __name__ == "__main__":
    print("Binance BTC Price:", get_binance_price())
    print("LunarCrush BTC Sentiment:", get_lunarcrush_data())
