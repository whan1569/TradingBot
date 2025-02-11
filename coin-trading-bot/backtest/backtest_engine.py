import pandas as pd

class BacktestEngine:
    def __init__(self, initial_balance=10000, trading_fee=0.001):
        self.initial_balance = initial_balance  # 초기 자본
        self.balance = initial_balance  # 현재 잔고
        self.trading_fee = trading_fee  # 거래 수수료
        self.positions = []  # 열린 포지션 리스트
        self.history = []  # 거래 내역

    def load_data(self, file_path):
        """CSV 파일에서 과거 데이터를 로드합니다."""
        self.data = pd.read_csv(file_path, parse_dates=['timestamp'])
        self.data.sort_values(by='timestamp', inplace=True)
    
    def run(self):
        """기본적인 백테스트 실행 루프."""
        for index, row in self.data.iterrows():
            price = row['close']  # 종가를 기준으로 계산
            
            # (예제) 간단한 매매 논리: 일정 금액 이하로 내려가면 매수, 올라가면 매도
            if price < 9500 and self.balance > 0:  # 매수 예제
                amount = self.balance / price  # 최대 매수 가능한 수량
                self.positions.append({'price': price, 'amount': amount})
                self.balance = 0  # 잔고 소진
                self.history.append({'action': 'buy', 'price': price, 'amount': amount})
            
            elif price > 10500 and self.positions:  # 매도 예제
                position = self.positions.pop(0)
                self.balance = position['amount'] * price * (1 - self.trading_fee)
                self.history.append({'action': 'sell', 'price': price, 'amount': position['amount']})
        
        self.final_report()
    
    def final_report(self):
        """최종 수익률 보고서."""
        final_balance = self.balance
        profit = final_balance - self.initial_balance
        print(f"최종 잔고: {final_balance:.2f} USD")
        print(f"총 수익: {profit:.2f} USD")
        print(f"거래 횟수: {len(self.history)}")

# 사용 예시
if __name__ == "__main__":
    engine = BacktestEngine()
    engine.load_data("historical_data.csv")  # 예제 데이터 파일 필요
    engine.run()
