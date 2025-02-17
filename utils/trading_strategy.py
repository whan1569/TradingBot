import time
import os
from . import error_handler

class TradingStrategy:
    def __init__(self, api_connector):
        """거래 전략 초기화"""
        self.api = api_connector
        self.symbol = "BTCUSDT"
        self.position = None
        self.last_trade_price = None
        self.trade_count = 0
        self.profit_loss = 0.0
        
        # 전략 파라미터
        self.min_price_change = 0.5  # 최소 가격 변동폭 (%)
        self.position_size = 0.001   # 기본 거래 수량 (BTC)
        self.stop_loss = 1.0         # 손절 기준 (%)
        self.take_profit = 2.0       # 익절 기준 (%)
        
        # 환경 변수에서 auto_trading 설정 가져오기
        self.auto_trading = os.getenv('AUTO_TRADING', 'false').lower() == 'true'
        
        error_handler.log_info(f"거래 전략 초기화 완료 (auto_trading: {self.auto_trading})")

    def analyze_market(self):
        """시장 분석"""
        try:
            # 시장 데이터 수집
            current_price = self.api.get_ticker_price(self.symbol)
            market_summary = self.api.get_market_summary(self.symbol)
            depth = self.api.get_market_depth(self.symbol, limit=10)
            
            # 기본 시장 분석
            price_change_24h = market_summary['price_change_percent']
            volume_24h = market_summary['volume']
            
            # 호가 분석
            bid_volume = sum(float(qty) for _, qty in depth['bids'])
            ask_volume = sum(float(qty) for _, qty in depth['asks'])
            buy_sell_ratio = bid_volume / ask_volume if ask_volume > 0 else 0
            
            analysis = {
                'current_price': current_price,
                'price_change_24h': price_change_24h,
                'volume_24h': volume_24h,
                'buy_sell_ratio': buy_sell_ratio,
                'market_sentiment': self._get_market_sentiment(price_change_24h, buy_sell_ratio)
            }
            
            error_handler.log_info(f"시장 분석 완료: {analysis}")
            return analysis
            
        except Exception as e:
            error_handler.log_error(e, "시장 분석 실패")
            raise

    def _get_market_sentiment(self, price_change, buy_sell_ratio):
        """시장 심리 분석"""
        if price_change > 1.0 and buy_sell_ratio > 1.1:
            return "STRONG_BUY"
        elif price_change > 0.5 and buy_sell_ratio > 1.0:
            return "BUY"
        elif price_change < -1.0 and buy_sell_ratio < 0.9:
            return "STRONG_SELL"
        elif price_change < -0.5 and buy_sell_ratio < 1.0:
            return "SELL"
        else:
            return "NEUTRAL"

    def should_open_position(self, analysis):
        """포지션 진입 조건 확인"""
        try:
            # 포지션이 이미 있거나 자동 거래가 비활성화된 경우
            if self.position is not None or not self.auto_trading:
                return False
                
            sentiment = analysis['market_sentiment']
            
            if sentiment in ["STRONG_BUY", "BUY"]:
                return "BUY"
            elif sentiment in ["STRONG_SELL", "SELL"]:
                return "SELL"
                
            return False
            
        except Exception as e:
            error_handler.log_error(e, "포지션 진입 조건 확인 실패")
            raise

    def should_close_position(self, analysis):
        """포지션 청산 조건 확인"""
        try:
            if self.position is None or self.last_trade_price is None:
                return False
                
            current_price = analysis['current_price']
            price_change = ((current_price - self.last_trade_price) / 
                          self.last_trade_price * 100)
                          
            if self.position == "BUY":
                if price_change <= -self.stop_loss:
                    return "STOP_LOSS"
                elif price_change >= self.take_profit:
                    return "TAKE_PROFIT"
                    
            elif self.position == "SELL":
                if price_change >= self.stop_loss:
                    return "STOP_LOSS"
                elif price_change <= -self.take_profit:
                    return "TAKE_PROFIT"
                    
            return False
            
        except Exception as e:
            error_handler.log_error(e, "포지션 청산 조건 확인 실패")
            raise

    def execute_trade(self, side, price=None):
        """거래 실행"""
        try:
            if price is None:
                price = self.api.get_ticker_price(self.symbol)
            
            order = self.api.create_order(
                symbol=self.symbol,
                order_type="LIMIT",
                side=side,
                quantity=self.position_size,
                price=price,
                test=True  # 테스트 모드
            )
            
            self.last_trade_price = float(price)
            self.position = "BUY" if side == "BUY" else "SELL"
            self.trade_count += 1
            
            error_handler.log_info(f"거래 실행 성공: {side} {self.position_size} @ {price}")
            return order
            
        except Exception as e:
            error_handler.log_error(e, "거래 실행 실패")
            raise

    def close_position(self, reason="MANUAL"):
        """포지션 청산"""
        try:
            if self.position is None:
                return False
                
            current_price = self.api.get_ticker_price(self.symbol)
            close_side = "SELL" if self.position == "BUY" else "BUY"
            
            order = self.api.create_order(
                symbol=self.symbol,
                order_type="LIMIT",
                side=close_side,
                quantity=self.position_size,
                price=current_price,
                test=True
            )
            
            # 거래 횟수 증가 (청산도 거래로 카운트)
            self.trade_count += 1
            
            # 손익 계산
            if self.last_trade_price:
                pl_percent = ((current_price - self.last_trade_price) / 
                            self.last_trade_price * 100)
                if self.position == "SELL":
                    pl_percent = -pl_percent
                    
                self.profit_loss += pl_percent
                error_handler.log_info(f"포지션 청산: {reason}, P/L = {pl_percent:.2f}%")
            
            # 포지션 초기화
            self.position = None
            self.last_trade_price = None
            
            return order
            
        except Exception as e:
            error_handler.log_error(e, "포지션 청산 실패")
            raise

    def update_position(self):
        """포지션 업데이트 및 관리"""
        try:
            # 시장 분석은 항상 수행
            analysis = self.analyze_market()
            
            # 자동 거래가 비활성화되어 있으면 분석 결과만 반환
            if not self.auto_trading:
                return {
                    'analysis': analysis,
                    'position': self.position,
                    'action': None
                }
            
            # 포지션이 없는 경우, 진입 신호 확인
            if self.position is None:
                signal = self.should_open_position(analysis)
                if signal in ["BUY", "SELL"]:
                    return self.execute_trade(signal, analysis['current_price'])
            
            # 포지션이 있는 경우, 청산 신호 확인
            else:
                signal = self.should_close_position(analysis)
                if signal in ["STOP_LOSS", "TAKE_PROFIT"]:
                    return self.close_position(signal)
            
            return None
            
        except Exception as e:
            error_handler.log_error(e, "포지션 업데이트 실패")
            raise

    def get_performance_metrics(self):
        """거래 전략 성능 지표 계산"""
        try:
            metrics = {
                'total_trades': self.trade_count,
                'total_profit_loss': self.profit_loss,
                'average_profit_loss': self.profit_loss / self.trade_count if self.trade_count > 0 else 0,
                'win_rate': 0,  # 승률은 trade_history 구현 후 계산
                'risk_reward_ratio': self.take_profit / self.stop_loss,
                'current_position': self.position,
                'position_size': self.position_size
            }
            
            error_handler.log_info(f"성능 지표 계산 완료: {metrics}")
            return metrics
            
        except Exception as e:
            error_handler.log_error(e, "성능 지표 계산 실패")
            raise

    def simulate_trades(self, days=30):
        """거래 시뮬레이션 실행"""
        try:
            # 시뮬레이션 초기화
            self.trade_count = 0
            self.profit_loss = 0.0
            self.position = None
            self.last_trade_price = None
            
            # 자동 거래 활성화
            self.auto_trading = True
            
            # 시뮬레이션 실행
            for _ in range(days):
                self.update_position()
                time.sleep(0.1)  # API 호출 제한 고려
            
            # 마지막 포지션 청산
            if self.position:
                self.close_position("SIMULATION_END")
            
            # 성능 지표 반환
            return self.get_performance_metrics()
            
        except Exception as e:
            error_handler.log_error(e, "거래 시뮬레이션 실패")
            raise

    def backtest(self, start_date, end_date, initial_balance=10000):
        """백테스트 실행"""
        try:
            # 백테스트 초기화
            self.trade_count = 0
            self.profit_loss = 0.0
            self.position = None
            self.last_trade_price = None
            self.balance = initial_balance
            
            # 과거 데이터 수집
            historical_data = self.api.get_historical_klines(
                self.symbol,
                interval="1h",
                start_str=start_date,
                end_str=end_date
            )
            
            # 백테스트 실행
            results = []
            for kline in historical_data:
                timestamp = kline[0]
                open_price = float(kline[1])
                high_price = float(kline[2])
                low_price = float(kline[3])
                close_price = float(kline[4])
                volume = float(kline[5])
                
                # 시장 분석 데이터 생성
                analysis = {
                    'current_price': close_price,
                    'price_change_24h': ((close_price - open_price) / open_price) * 100,
                    'volume_24h': volume,
                    'buy_sell_ratio': 1.0,  # 백테스트에서는 임시로 1.0 사용
                    'market_sentiment': self._get_market_sentiment(
                        ((close_price - open_price) / open_price) * 100,
                        1.0
                    )
                }
                
                # 포지션 업데이트
                if self.position is None:
                    signal = self.should_open_position(analysis)
                    if signal:
                        self.execute_trade(signal, close_price)
                else:
                    signal = self.should_close_position(analysis)
                    if signal:
                        self.close_position(signal)
                
                # 결과 기록
                results.append({
                    'timestamp': timestamp,
                    'price': close_price,
                    'position': self.position,
                    'balance': self.balance,
                    'profit_loss': self.profit_loss
                })
            
            # 마지막 포지션 청산
            if self.position:
                self.close_position("BACKTEST_END")
            
            error_handler.log_info(f"백테스트 완료: {len(results)}개 데이터 처리")
            return results
            
        except Exception as e:
            error_handler.log_error(e, "백테스트 실행 실패")
            raise

    def optimize_parameters(self, start_date, end_date, initial_balance=10000):
        """전략 파라미터 최적화"""
        try:
            # 최적화할 파라미터 범위 설정
            param_ranges = {
                'min_price_change': [0.3, 0.5, 0.7, 1.0],
                'position_size': [0.001, 0.002, 0.003],
                'stop_loss': [0.5, 1.0, 1.5],
                'take_profit': [1.0, 1.5, 2.0, 2.5]
            }
            
            # 최적화 결과 저장
            best_params = None
            best_profit = float('-inf')
            optimization_results = []
            
            # 모든 파라미터 조합에 대해 백테스트 실행
            for min_price_change in param_ranges['min_price_change']:
                for position_size in param_ranges['position_size']:
                    for stop_loss in param_ranges['stop_loss']:
                        for take_profit in param_ranges['take_profit']:
                            # 파라미터 설정
                            self.min_price_change = min_price_change
                            self.position_size = position_size
                            self.stop_loss = stop_loss
                            self.take_profit = take_profit
                            
                            # 백테스트 실행
                            results = self.backtest(start_date, end_date, initial_balance)
                            final_result = results[-1]
                            
                            # 결과 저장
                            params = {
                                'min_price_change': min_price_change,
                                'position_size': position_size,
                                'stop_loss': stop_loss,
                                'take_profit': take_profit,
                                'profit': final_result['profit_loss'],
                                'trades': self.trade_count
                            }
                            optimization_results.append(params)
                            
                            # 최고 수익률 갱신 확인
                            if final_result['profit_loss'] > best_profit:
                                best_profit = final_result['profit_loss']
                                best_params = params.copy()
            
            # 최적 파라미터 적용
            if best_params:
                self.min_price_change = best_params['min_price_change']
                self.position_size = best_params['position_size']
                self.stop_loss = best_params['stop_loss']
                self.take_profit = best_params['take_profit']
            
            error_handler.log_info(f"전략 최적화 완료: 최적 파라미터 = {best_params}")
            return {
                'best_parameters': best_params,
                'all_results': optimization_results
            }
            
        except Exception as e:
            error_handler.log_error(e, "전략 최적화 실패")
            raise

    def calculate_risk_metrics(self):
        """리스크 지표 계산"""
        try:
            # 기본 리스크 지표 계산
            metrics = {
                'max_position_size': self.position_size * 3,  # 최대 포지션 크기
                'max_daily_loss': 2.0,                        # 일일 최대 손실 제한 (%)
                'max_trade_count': 10,                        # 일일 최대 거래 횟수
                'current_daily_loss': abs(min(0, self.profit_loss)),  # 현재 일일 손실
                'current_trade_count': self.trade_count,      # 현재 거래 횟수
                'risk_level': self._calculate_risk_level()    # 현재 리스크 수준
            }
            
            error_handler.log_info(f"리스크 지표 계산 완료: {metrics}")
            return metrics
            
        except Exception as e:
            error_handler.log_error(e, "리스크 지표 계산 실패")
            raise

    def _calculate_risk_level(self):
        """리스크 수준 계산"""
        if self.profit_loss < -1.5:
            return "HIGH"
        elif self.profit_loss < -0.5:
            return "MEDIUM"
        else:
            return "LOW"

    def check_risk_limits(self):
        """리스크 한도 체크"""
        try:
            metrics = self.calculate_risk_metrics()
            
            # 리스크 한도 체크
            checks = {
                'position_size_ok': self.position_size <= metrics['max_position_size'],
                'daily_loss_ok': metrics['current_daily_loss'] <= metrics['max_daily_loss'],
                'trade_count_ok': metrics['current_trade_count'] <= metrics['max_trade_count']
            }
            
            # 종합 리스크 평가
            overall_status = all(checks.values())
            
            error_handler.log_info(f"리스크 한도 체크 완료: {checks}, 전체 상태: {overall_status}")
            return {
                'status': overall_status,
                'checks': checks,
                'metrics': metrics
            }
            
        except Exception as e:
            error_handler.log_error(e, "리스크 한도 체크 실패")
            raise

    def start_monitoring(self, callback=None):
        """실시간 모니터링 시작"""
        try:
            self.monitoring_active = True
            self.monitoring_callback = callback
            
            # 모니터링 데이터 초기화
            self.monitoring_data = {
                'start_time': time.time(),
                'last_update': None,
                'alerts': [],
                'status': 'RUNNING'
            }
            
            error_handler.log_info("실시간 모니터링 시작")
            return True
            
        except Exception as e:
            error_handler.log_error(e, "모니터링 시작 실패")
            raise

    def stop_monitoring(self):
        """실시간 모니터링 중지"""
        try:
            self.monitoring_active = False
            self.monitoring_data['status'] = 'STOPPED'
            self.monitoring_data['end_time'] = time.time()
            
            error_handler.log_info("실시간 모니터링 중지")
            return self.monitoring_data
            
        except Exception as e:
            error_handler.log_error(e, "모니터링 중지 실패")
            raise

    def update_monitoring_data(self):
        """모니터링 데이터 업데이트"""
        try:
            if not self.monitoring_active:
                return None
                
            current_time = time.time()
            analysis = self.analyze_market()
            risk_check = self.check_risk_limits()
            
            update = {
                'timestamp': current_time,
                'market_data': analysis,
                'position': self.position,
                'profit_loss': self.profit_loss,
                'risk_status': risk_check['status'],
                'trade_count': self.trade_count
            }
            
            # 모니터링 데이터 업데이트
            self.monitoring_data['last_update'] = update
            
            # 콜백 함수 실행 (있는 경우)
            if self.monitoring_callback:
                self.monitoring_callback(update)
            
            error_handler.log_info(f"모니터링 데이터 업데이트: {update}")
            return update
            
        except Exception as e:
            error_handler.log_error(e, "모니터링 데이터 업데이트 실패")
            raise

    def add_alert(self, alert_type, message, level="INFO"):
        """알림 추가"""
        try:
            alert = {
                'timestamp': time.time(),
                'type': alert_type,
                'message': message,
                'level': level
            }
            
            if hasattr(self, 'monitoring_data'):
                self.monitoring_data['alerts'].append(alert)
            
            error_handler.log_info(f"알림 추가: {alert}")
            return alert
            
        except Exception as e:
            error_handler.log_error(e, "알림 추가 실패")
            raise

    def check_alerts(self, analysis):
        """알림 조건 체크"""
        try:
            alerts = []
            
            # 가격 변동 알림
            price_change = analysis['price_change_24h']
            if abs(price_change) >= 5.0:
                alerts.append(self.add_alert(
                    "PRICE_CHANGE",
                    f"큰 폭의 가격 변동: {price_change:.2f}%",
                    "WARNING" if abs(price_change) >= 10.0 else "INFO"
                ))
            
            # 리스크 한도 알림
            risk_check = self.check_risk_limits()
            if not risk_check['status']:
                for check, ok in risk_check['checks'].items():
                    if not ok:
                        alerts.append(self.add_alert(
                            "RISK_LIMIT",
                            f"리스크 한도 초과: {check}",
                            "WARNING"
                        ))
            
            # 수익률 알림
            if self.profit_loss <= -1.5:
                alerts.append(self.add_alert(
                    "PROFIT_LOSS",
                    f"큰 손실 발생: {self.profit_loss:.2f}%",
                    "CRITICAL"
                ))
            
            return alerts
            
        except Exception as e:
            error_handler.log_error(e, "알림 체크 실패")
            raise

    def get_alerts(self, min_level="INFO"):
        """알림 조회"""
        try:
            if not hasattr(self, 'monitoring_data'):
                return []
                
            # 알림 레벨 우선순위
            level_priority = {
                "INFO": 0,
                "WARNING": 1,
                "CRITICAL": 2
            }
            
            min_priority = level_priority.get(min_level, 0)
            
            # 지정된 레벨 이상의 알림만 필터링
            filtered_alerts = [
                alert for alert in self.monitoring_data['alerts']
                if level_priority.get(alert['level'], 0) >= min_priority
            ]
            
            return filtered_alerts
            
        except Exception as e:
            error_handler.log_error(e, "알림 조회 실패")
            raise

    def generate_report(self, report_type="DAILY"):
        """거래 전략 보고서 생성"""
        try:
            # 기본 보고서 데이터 수집
            metrics = self.get_performance_metrics()
            risk_status = self.check_risk_limits()
            alerts = self.get_alerts(min_level="WARNING")
            
            report = {
                'timestamp': time.time(),
                'report_type': report_type,
                'performance': metrics,
                'risk_status': risk_status,
                'alerts': alerts,
                'current_market': self.analyze_market(),
                'summary': {
                    'total_profit_loss': f"{self.profit_loss:.2f}%",
                    'trade_count': self.trade_count,
                    'risk_level': self._calculate_risk_level(),
                    'active_position': self.position
                }
            }
            
            error_handler.log_info(f"보고서 생성 완료: {report_type}")
            return report
            
        except Exception as e:
            error_handler.log_error(e, "보고서 생성 실패")
            raise 