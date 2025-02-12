import time
from strategies.trading_decision import make_trading_decision
from system.auto_trader import execute_trade

# 실행 간격 (초 단위)
INTERVAL = 60  # 60초마다 실행

if __name__ == "__main__":
    print("### Real-time Trading System Started ###")

    while True:
        try:
            # 트레이딩 결정 수행
            decision = make_trading_decision()
            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Final Decision: {decision}")

            # 자동 매매 실행
            if decision in ["LONG", "SHORT"]:
                execute_trade(decision)

            # 일정 시간 대기
            time.sleep(INTERVAL)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)  # 오류 발생 시 5초 후 재시도
