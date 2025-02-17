from .error_handler import log_error, log_info

class DataCollector:
    def __init__(self, api):
        self.api = api
        self.symbol = 'BTCUSDT'
        self.interval = '1m'
        log_info("데이터 수집기 초기화 완료")

    def get_recent_data(self, limit=100):
        """최근 OHLCV 데이터 조회"""
        try:
            klines = self.api.get_klines(
                symbol=self.symbol,
                interval=self.interval,
                limit=limit
            )
            return klines
        except Exception as e:
            log_error(e, "OHLCV 데이터 조회 실패")
            raise

    def get_current_price(self):
        """현재가 조회"""
        try:
            ticker = self.api.get_ticker(symbol=self.symbol)
            return float(ticker['lastPrice'])
        except Exception as e:
            log_error(e, "현재가 조회 실패")
            raise 