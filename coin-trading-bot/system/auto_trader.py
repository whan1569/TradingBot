import json
import time
import logging
from binance.client import Client
from utils.api_connector import get_binance_price
from utils.config_loader import load_config

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 설정 로드
config = load_config("config/api_keys.json")
strategy_config = load_config("config/strategy_config.json")

# 바이낸스 API 클라이언트 초기화
client = Client(config["binance_api_key"], config["binance_api_secret"])

class AutoTrader:
    def __init__(self, symbol="BTCUSDT"):
        self.symbol = symbol
        self.position = None  # 현재 포지션 (LONG, SHORT, None)

    def execute_trade(self, signal, quantity):
        """ 트레이딩 신호에 따라 매매 주문 실행 """
        try:
            if signal == "BUY":
                order = client.order_market_buy(symbol=self.symbol, quantity=quantity)
                self.position = "LONG"
                logging.info(f"매수 주문 실행: {order}")
            elif signal == "SELL":
                order = client.order_market_sell(symbol=self.symbol, quantity=quantity)
                self.position = "SHORT"
                logging.info(f"매도 주문 실행: {order}")
        except Exception as e:
            logging.error(f"주문 실행 오류: {e}")

    def check_trade_signal(self):
        """ 신호 파일에서 매매 신호 확인 """
        try:
            with open("data/signals.json", "r") as file:
                signals = json.load(file)
                return signals.get(self.symbol, None)
        except Exception as e:
            logging.error(f"신호 파일 읽기 오류: {e}")
            return None

    def run(self):
        """ 자동 매매 실행 루프 """
        while True:
            signal = self.check_trade_signal()
            if signal:
                quantity = strategy_config["trade_quantity"]
                self.execute_trade(signal, quantity)
            time.sleep(10)  # 10초마다 신호 체크

if __name__ == "__main__":
    trader = AutoTrader()
    trader.run()
