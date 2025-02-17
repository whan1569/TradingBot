import sys
import time
from utils.api_connector import BinanceAPI
from utils.trading_strategy import TradingStrategy
from utils.error_handler import log_info, log_error

class TradingBot:
    def __init__(self, test_mode=True):
        self.test_mode = test_mode
        self.api = None
        self.strategy = None
        
    def initialize(self):
        """시스템 초기화"""
        try:
            # API 초기화
            self.api = BinanceAPI()
            log_info(f"API 초기화 성공 ({'테스트 모드' if self.test_mode else '실제 거래'})")
            
            # 전략 초기화 (실제 구현된 파라미터에 맞춤)
            self.strategy = TradingStrategy(
                binance_api=self.api,
                symbol='BTCUSDT',
                auto_trading=not self.test_mode  # 테스트 모드면 자동거래 비활성화
            )
            log_info("전략 초기화 성공")
            
            return True
            
        except Exception as e:
            log_error(e, "시스템 초기화 실패")
            return False
            
    def run(self):
        """트레이딩 봇 실행"""
        try:
            log_info(f"트레이딩 봇 시작 ({'테스트 모드' if self.test_mode else '실제 거래'})")
            
            while True:
                try:
                    # 시장 데이터 분석
                    market_data = self.strategy.analyze_market()
                    log_info(f"시장 분석 결과: {market_data}")
                    
                    if not self.test_mode:
                        # 실제 거래 모드에서만 포지션 업데이트
                        self.strategy.update_position()
                    
                    time.sleep(1)
                    
                except KeyboardInterrupt:
                    log_info("프로그램 종료 요청")
                    break
                    
                except Exception as e:
                    log_error(e, "전략 실행 중 에러")
                    time.sleep(5)
                    
        except Exception as e:
            log_error(e, "실행 중 치명적 에러")
            return False
            
        return True

def main():
    # 트레이딩 봇 인스턴스 생성 (테스트 모드)
    bot = TradingBot(test_mode=True)
    
    # 초기화
    if not bot.initialize():
        sys.exit(1)
    
    # 실행
    if not bot.run():
        sys.exit(1)

if __name__ == "__main__":
    main()
