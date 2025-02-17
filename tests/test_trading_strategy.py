import unittest
from utils.api_connector import BinanceAPI
from utils.trading_strategy import TradingStrategy
from utils import error_handler
import time

class TestTradingStrategy(unittest.TestCase):
    def setUp(self):
        """테스트 설정"""
        self.api = BinanceAPI()
        self.symbol = "BTCUSDT"
        self.strategy = TradingStrategy(self.api)
        self.strategy.auto_trading = False  # 명시적으로 비활성화

    def test_market_analysis(self):
        """시장 분석 테스트"""
        try:
            # 시장 분석 실행
            analysis = self.strategy.analyze_market()
            
            # 필수 필드 확인
            required_fields = ['current_price', 'price_change_24h', 'volume_24h',
                             'buy_sell_ratio', 'market_sentiment']
            for field in required_fields:
                self.assertIn(field, analysis)
            
            # 값 타입 확인
            self.assertIsInstance(analysis['current_price'], float)
            self.assertIsInstance(analysis['market_sentiment'], str)
            
            error_handler.log_info(f"시장 분석 테스트 성공: {analysis}")
            
        except Exception as e:
            error_handler.log_error(e, "시장 분석 테스트 실패")
            raise

    def test_position_signals(self):
        """포지션 신호 테스트"""
        try:
            # 시장 분석 데이터 준비
            analysis = self.strategy.analyze_market()
            
            # 포지션 진입 신호 테스트
            entry_signal = self.strategy.should_open_position(analysis)
            self.assertIn(entry_signal, [False, "BUY", "SELL"])
            
            # 가상의 포지션 설정
            self.strategy.position = "BUY"
            self.strategy.last_trade_price = analysis['current_price']
            
            # 포지션 청산 신호 테스트
            exit_signal = self.strategy.should_close_position(analysis)
            self.assertIn(exit_signal, [False, "STOP_LOSS", "TAKE_PROFIT"])
            
            error_handler.log_info(f"포지션 신호 테스트 성공: 진입={entry_signal}, 청산={exit_signal}")
            
        except Exception as e:
            error_handler.log_error(e, "포지션 신호 테스트 실패")
            raise

    def test_market_sentiment(self):
        """시장 심리 분석 테스트"""
        try:
            test_cases = [
                (2.0, 1.2, "STRONG_BUY"),
                (0.8, 1.1, "BUY"),
                (-2.0, 0.8, "STRONG_SELL"),
                (-0.8, 0.9, "SELL"),
                (0.1, 1.0, "NEUTRAL")
            ]
            
            for price_change, buy_sell_ratio, expected in test_cases:
                sentiment = self.strategy._get_market_sentiment(price_change, buy_sell_ratio)
                self.assertEqual(sentiment, expected)
            
            error_handler.log_info("시장 심리 분석 테스트 성공")
            
        except Exception as e:
            error_handler.log_error(e, "시장 심리 분석 테스트 실패")
            raise

    def test_trade_execution(self):
        """거래 실행 테스트"""
        try:
            # 시장 분석
            analysis = self.strategy.analyze_market()
            current_price = analysis['current_price']
            
            # 매수 주문 테스트
            buy_order = self.strategy.execute_trade("BUY", current_price)
            self.assertIsNotNone(buy_order)
            self.assertEqual(self.strategy.position, "BUY")
            
            # 포지션 청산 테스트
            close_order = self.strategy.close_position("TEST")
            self.assertIsNotNone(close_order)
            self.assertIsNone(self.strategy.position)
            
            error_handler.log_info("거래 실행 테스트 성공")
            
        except Exception as e:
            error_handler.log_error(e, "거래 실행 테스트 실패")
            raise

    def test_position_management(self):
        """포지션 관리 테스트"""
        try:
            # 전략 초기화
            self.strategy = TradingStrategy(self.api)  # 새로운 인스턴스 생성
            
            # 초기 상태 확인
            self.assertIsNone(self.strategy.position)
            
            # 자동 거래 활성화
            self.strategy.auto_trading = True
            
            # 포지션 업데이트 실행
            result = self.strategy.update_position()
            
            # 결과 검증 (시장 상황에 따라 포지션이 있을 수도, 없을 수도 있음)
            if result:
                # 포지션이 열린 경우
                position_type = self.strategy.position  # 현재 포지션 저장
                self.assertIsNotNone(position_type)
                self.assertIsNotNone(self.strategy.last_trade_price)
                self.assertIn(position_type, ["BUY", "SELL"])
                
                # 포지션 청산
                close_result = self.strategy.close_position("TEST")
                self.assertIsNotNone(close_result)
                
                # 청산 후 상태 확인
                self.assertIsNone(self.strategy.position)
                error_handler.log_info(f"포지션 관리 테스트 성공: {position_type} 포지션 생성 후 청산")
            else:
                # 포지션이 열리지 않은 경우
                self.assertIsNone(self.strategy.position)
                error_handler.log_info("포지션 관리 테스트 성공: 포지션 없음")
            
        except Exception as e:
            error_handler.log_error(e, "포지션 관리 테스트 실패")
            raise

    def test_profit_loss_calculation(self):
        """손익 계산 테스트"""
        try:
            # 가상의 거래 시나리오 생성
            current_price = self.strategy.api.get_ticker_price(self.strategy.symbol)
            
            # 매수 포지션 시뮬레이션
            self.strategy.execute_trade("BUY", current_price)
            
            # 가격 변동 시뮬레이션 (2% 상승)
            simulated_price = current_price * 1.02
            self.strategy.api.last_price = simulated_price  # 테스트용 가격 설정
            
            # 포지션 청산
            self.strategy.close_position("TEST")
            
            # 손익이 계산되었는지 확인
            self.assertGreater(self.strategy.profit_loss, 0)
            
            error_handler.log_info(f"손익 계산 테스트 성공: P/L = {self.strategy.profit_loss:.2f}%")
            
        except Exception as e:
            error_handler.log_error(e, "손익 계산 테스트 실패")
            raise

    def test_performance_metrics(self):
        """성능 지표 계산 테스트"""
        try:
            # 가상의 거래 시나리오 생성
            current_price = self.strategy.api.get_ticker_price(self.strategy.symbol)
            
            # 여러 거래 실행
            self.strategy.execute_trade("BUY", current_price)
            self.strategy.close_position("TEST")
            
            self.strategy.execute_trade("SELL", current_price)
            self.strategy.close_position("TEST")
            
            # 성능 지표 계산
            metrics = self.strategy.get_performance_metrics()
            
            # 필수 필드 확인
            required_fields = ['total_trades', 'total_profit_loss', 'average_profit_loss',
                             'win_rate', 'risk_reward_ratio', 'current_position']
            for field in required_fields:
                self.assertIn(field, metrics)
            
            # 값 검증
            self.assertEqual(metrics['total_trades'], 4)  # 매수/매도 각 2회
            self.assertIsNone(metrics['current_position'])
            self.assertEqual(metrics['risk_reward_ratio'], 2.0)  # take_profit / stop_loss
            
            error_handler.log_info(f"성능 지표 테스트 성공: {metrics}")
            
        except Exception as e:
            error_handler.log_error(e, "성능 지표 테스트 실패")
            raise

    def test_trade_simulation(self):
        """거래 시뮬레이션 테스트"""
        try:
            # 짧은 기간으로 시뮬레이션 실행
            simulation_days = 1
            metrics = self.strategy.simulate_trades(days=simulation_days)
            
            # 결과 검증
            self.assertIsInstance(metrics, dict)
            self.assertGreaterEqual(metrics['total_trades'], 0)
            self.assertIsNone(metrics['current_position'])  # 시뮬레이션 종료 시 포지션 없어야 함
            
            error_handler.log_info(f"거래 시뮬레이션 테스트 성공: {metrics}")
            
        except Exception as e:
            error_handler.log_error(e, "거래 시뮬레이션 테스트 실패")
            raise

    def test_backtest(self):
        """백테스트 기능 테스트"""
        try:
            # 백테스트 기간 설정 (최근 7일)
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            # 백테스트 실행
            results = self.strategy.backtest(
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                initial_balance=10000
            )
            
            # 결과 검증
            self.assertIsInstance(results, list)
            self.assertGreater(len(results), 0)
            
            # 각 결과 항목 검증
            first_result = results[0]
            required_fields = ['timestamp', 'price', 'position', 'balance', 'profit_loss']
            for field in required_fields:
                self.assertIn(field, first_result)
            
            # 최종 결과 로깅
            final_result = results[-1]
            error_handler.log_info(
                f"백테스트 테스트 성공: 기간={len(results)}시간, "
                f"최종잔고=${final_result['balance']:.2f}, "
                f"수익률={final_result['profit_loss']:.2f}%"
            )
            
        except Exception as e:
            error_handler.log_error(e, "백테스트 테스트 실패")
            raise

    def test_strategy_optimization(self):
        """전략 최적화 테스트"""
        try:
            # 최적화 기간 설정 (최근 3일)
            from datetime import datetime, timedelta
            end_date = datetime.now()
            start_date = end_date - timedelta(days=3)
            
            # 최적화 실행
            results = self.strategy.optimize_parameters(
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d'),
                initial_balance=10000
            )
            
            # 결과 검증
            self.assertIn('best_parameters', results)
            self.assertIn('all_results', results)
            
            best_params = results['best_parameters']
            required_fields = ['min_price_change', 'position_size', 
                             'stop_loss', 'take_profit', 'profit', 'trades']
            
            # 최적 파라미터 필드 확인
            for field in required_fields:
                self.assertIn(field, best_params)
            
            # 최적화 결과 검증
            self.assertGreater(len(results['all_results']), 0)
            self.assertGreaterEqual(best_params['profit'], 
                                  max(r['profit'] for r in results['all_results']))
            
            error_handler.log_info(
                f"전략 최적화 테스트 성공: 최적 파라미터 = {best_params}, "
                f"예상 수익률 = {best_params['profit']:.2f}%"
            )
            
        except Exception as e:
            error_handler.log_error(e, "전략 최적화 테스트 실패")
            raise

    def test_risk_management(self):
        """리스크 관리 테스트"""
        try:
            # 초기 리스크 지표 확인
            metrics = self.strategy.calculate_risk_metrics()
            self.assertIn('risk_level', metrics)
            self.assertEqual(metrics['risk_level'], "LOW")  # 초기 리스크 레벨
            
            # 가상의 손실 시나리오 생성
            self.strategy.profit_loss = -1.8  # 큰 손실 상황
            metrics = self.strategy.calculate_risk_metrics()
            self.assertEqual(metrics['risk_level'], "HIGH")
            
            # 리스크 한도 체크
            risk_check = self.strategy.check_risk_limits()
            self.assertIn('status', risk_check)
            self.assertIn('checks', risk_check)
            self.assertIn('metrics', risk_check)
            
            # 리스크 한도 초과 시나리오
            self.strategy.trade_count = 15  # 일일 최대 거래 횟수 초과
            risk_check = self.strategy.check_risk_limits()
            self.assertFalse(risk_check['status'])  # 리스크 한도 초과
            self.assertFalse(risk_check['checks']['trade_count_ok'])
            
            error_handler.log_info(f"리스크 관리 테스트 성공: {risk_check}")
            
        except Exception as e:
            error_handler.log_error(e, "리스크 관리 테스트 실패")
            raise

    def test_monitoring(self):
        """실시간 모니터링 테스트"""
        try:
            # 모니터링 콜백 함수 정의
            received_updates = []
            def monitoring_callback(update):
                received_updates.append(update)
            
            # 모니터링 시작
            self.strategy.start_monitoring(callback=monitoring_callback)
            self.assertTrue(self.strategy.monitoring_active)
            
            # 여러 번 업데이트 실행
            for _ in range(3):
                update = self.strategy.update_monitoring_data()
                self.assertIsNotNone(update)
                self.assertIn('timestamp', update)
                self.assertIn('market_data', update)
                self.assertIn('position', update)
                time.sleep(0.1)  # API 호출 제한 고려
            
            # 콜백 함수 호출 확인
            self.assertEqual(len(received_updates), 3)
            
            # 모니터링 중지
            final_data = self.strategy.stop_monitoring()
            self.assertFalse(self.strategy.monitoring_active)
            self.assertEqual(final_data['status'], 'STOPPED')
            
            error_handler.log_info(f"모니터링 테스트 성공: {len(received_updates)}개 업데이트 수신")
            
        except Exception as e:
            error_handler.log_error(e, "모니터링 테스트 실패")
            raise

    def test_alert_system(self):
        """알림 시스템 테스트"""
        try:
            # 모니터링 시작
            self.strategy.start_monitoring()
            
            # 알림 추가 테스트
            alert = self.strategy.add_alert(
                "TEST",
                "테스트 알림",
                "INFO"
            )
            self.assertIn('timestamp', alert)
            self.assertEqual(alert['type'], "TEST")
            
            # 시장 분석 기반 알림 체크
            analysis = self.strategy.analyze_market()
            alerts = self.strategy.check_alerts(analysis)
            
            # 가상의 위험 상황 생성
            self.strategy.profit_loss = -2.0  # 큰 손실 상황
            self.strategy.trade_count = 15    # 거래 한도 초과
            
            alerts = self.strategy.check_alerts(analysis)
            self.assertGreater(len(alerts), 0)
            
            # 알림 조회 테스트
            warning_alerts = self.strategy.get_alerts(min_level="WARNING")
            self.assertGreater(len(warning_alerts), 0)
            
            error_handler.log_info(f"알림 시스템 테스트 성공: {len(alerts)}개 알림 생성")
            
        except Exception as e:
            error_handler.log_error(e, "알림 시스템 테스트 실패")
            raise

    def test_report_generation(self):
        """보고서 생성 테스트"""
        try:
            # 테스트 데이터 생성
            self.strategy.trade_count = 5
            self.strategy.profit_loss = -1.2
            self.strategy.position = "BUY"
            
            # 모니터링 시작 (알림 기능 활성화)
            self.strategy.start_monitoring()
            
            # 알림 추가
            self.strategy.add_alert(
                "TEST_ALERT",
                "테스트 경고 메시지",
                "WARNING"
            )
            
            # 보고서 생성
            report = self.strategy.generate_report()
            
            # 필수 필드 확인
            required_fields = ['timestamp', 'report_type', 'performance', 
                             'risk_status', 'alerts', 'current_market', 'summary']
            for field in required_fields:
                self.assertIn(field, report)
            
            # 보고서 내용 검증
            self.assertEqual(report['report_type'], "DAILY")
            self.assertEqual(report['summary']['trade_count'], 5)
            self.assertEqual(report['summary']['active_position'], "BUY")
            self.assertEqual(report['summary']['risk_level'], "MEDIUM")
            self.assertGreater(len(report['alerts']), 0)
            
            error_handler.log_info(f"보고서 생성 테스트 성공: {report['summary']}")
            
        except Exception as e:
            error_handler.log_error(e, "보고서 생성 테스트 실패")
            raise

if __name__ == '__main__':
    unittest.main() 