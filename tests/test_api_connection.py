import unittest
import time
import asyncio
from utils.api_connector import BinanceAPI
from utils.websocket_handler import BinanceWebSocket
from utils import error_handler

class TestBinanceAPI(unittest.TestCase):
    def setUp(self):
        """테스트 설정"""
        self.api = BinanceAPI()
        self.symbol = "BTCUSDT"

    def test_server_time(self):
        """서버 시간 조회 테스트"""
        try:
            server_time = self.api.get_server_time()
            self.assertIsNotNone(server_time)
            self.assertIsInstance(server_time, int)
            error_handler.log_info(f"서버 시간 테스트 성공: {server_time}")
        except Exception as e:
            error_handler.log_error(e, "서버 시간 테스트 실패")
            raise

    def test_connection(self):
        """API 연결 테스트"""
        try:
            result = self.api.test_connection()
            self.assertTrue(result)
            error_handler.log_info("API 연결 테스트 성공")
        except Exception as e:
            error_handler.log_error(e, "API 연결 테스트 실패")
            raise

    def test_price_data_consistency(self):
        """가격 데이터 일관성 테스트"""
        try:
            # REST API로 현재가 조회
            ticker_price = self.api.get_ticker_price(self.symbol)
            
            # 최근 체결 내역 조회
            trade_price = self.api.get_recent_trades(self.symbol)['price']
            
            # 두 가격의 차이를 백분율로 계산
            price_diff_percent = abs(ticker_price - trade_price) / ticker_price * 100
            
            # 가격 차이가 0.1% 이내인지 확인
            self.assertLess(price_diff_percent, 0.1)
            error_handler.log_info(f"가격 일관성 테스트 성공: 차이 = {price_diff_percent:.4f}%")
            
            # 추가 정보 로깅
            error_handler.log_info(f"Ticker 가격: {ticker_price}")
            error_handler.log_info(f"최근 체결가: {trade_price}")
            
        except Exception as e:
            error_handler.log_error(e, "가격 데이터 일관성 테스트 실패")
            raise

    def test_price_update_speed(self):
        """가격 업데이트 속도 테스트"""
        try:
            start_time = time.time()
            
            # REST API 호출
            ticker_price = self.api.get_ticker_price(self.symbol)
            
            rest_time = time.time() - start_time
            error_handler.log_info(f"REST API 응답 시간: {rest_time:.3f}초")
            
            # 응답 시간이 1초 이내인지 확인
            self.assertLess(rest_time, 1.0)
            
        except Exception as e:
            error_handler.log_error(e, "가격 업데이트 속도 테스트 실패")
            raise

    def test_price_update_interval(self):
        """가격 업데이트 간격 테스트"""
        try:
            # 첫 번째 요청
            price1 = self.api.get_ticker_price(self.symbol)
            
            # 0.5초 대기
            time.sleep(0.5)
            
            # 두 번째 요청 (캐시된 가격이어야 함)
            price2 = self.api.get_ticker_price(self.symbol)
            self.assertEqual(price1, price2)
            
            # 1초 이상 대기
            time.sleep(1.0)
            
            # 세 번째 요청 (새로운 가격이어야 함)
            price3 = self.api.get_ticker_price(self.symbol)
            error_handler.log_info(f"가격 업데이트 간격 테스트 성공: {price1} -> {price3}")
            
        except Exception as e:
            error_handler.log_error(e, "가격 업데이트 간격 테스트 실패")
            raise

    def test_websocket_connection(self):
        """WebSocket 연결 및 재연결 테스트"""
        async def async_test():
            ws_client = BinanceWebSocket()
            try:
                # 초기 연결 테스트
                connected = await ws_client.connect()
                self.assertTrue(connected)
                error_handler.log_info("WebSocket 초기 연결 성공")
                
                # 메시지 수신 테스트
                message = await ws_client.receive_message()
                self.assertIsNotNone(message)
                # 'p'가 가격을 나타내는 필드입니다
                self.assertIn('p', message)
                price = float(message['p'])
                error_handler.log_info(f"WebSocket 메시지 수신 성공: 가격 = {price}")
                
                # 연결 종료 후 재연결 테스트
                await ws_client.close()
                self.assertFalse(ws_client.is_connected)
                
                # 재연결 테스트
                reconnected = await ws_client.reconnect()
                self.assertTrue(reconnected)
                error_handler.log_info("WebSocket 재연결 성공")
                
            except Exception as e:
                error_handler.log_error(e, "WebSocket 테스트 실패")
                raise
            finally:
                # 정리
                await ws_client.close()

        # 비동기 테스트 실행
        asyncio.run(async_test())

    def test_rate_limit(self):
        """Rate Limit 대응 테스트"""
        try:
            # 1분당 1200개 제한을 테스트하기 위해 1300개 요청
            test_requests = 1300
            success_count, total_time = self.api.test_rate_limit(test_requests)
            
            # 모든 요청이 성공적으로 처리되었는지 확인
            self.assertEqual(success_count, test_requests)
            
            # 평균 처리 시간이 적절한지 확인 (2초 이내)
            avg_time_per_request = total_time / test_requests
            self.assertLess(avg_time_per_request, 2.0)
            
            error_handler.log_info(f"Rate Limit 테스트 성공: 평균 처리 시간 = {avg_time_per_request:.3f}초/요청")
            
        except Exception as e:
            error_handler.log_error(e, "Rate Limit 테스트 실패")
            raise

    def test_order_creation(self):
        """주문 생성 테스트"""
        try:
            # 현재가 조회
            current_price = self.api.get_ticker_price(self.symbol)
            
            # LIMIT 매수 주문 테스트 (현재가보다 5% 낮게)
            test_price = float(self._format_number(current_price * 0.95, 2))  # 가격 소수점 2자리로 조정
            test_quantity = 0.001  # 최소 주문 수량
            
            # 테스트 주문 실행
            order_result = self.api.create_order(
                symbol=self.symbol,
                order_type="LIMIT",
                side="BUY",
                quantity=test_quantity,
                price=test_price,
                test=True  # 테스트 모드
            )
            
            # 주문 결과 검증
            self.assertIsNotNone(order_result)
            error_handler.log_info(f"주문 테스트 성공: {test_quantity} BTC @ ${test_price}")
            
        except Exception as e:
            error_handler.log_error(e, "주문 생성 테스트 실패")
            raise

    def _format_number(self, number, decimals):
        """숫자 포맷팅 (테스트용)"""
        format_str = f"{{:.{decimals}f}}"
        return format_str.format(number)

    def test_order_validation(self):
        """주문 파라미터 검증 테스트"""
        try:
            # 잘못된 심볼 테스트
            with self.assertRaises(ValueError):
                self.api.create_order(symbol="INVALID", test=True)
            
            # 잘못된 주문 타입 테스트
            with self.assertRaises(ValueError):
                self.api.create_order(order_type="INVALID", test=True)
            
            # 잘못된 거래 구분 테스트
            with self.assertRaises(ValueError):
                self.api.create_order(side="INVALID", test=True)
            
            # 잘못된 수량 테스트
            with self.assertRaises(ValueError):
                self.api.create_order(quantity=-1, test=True)
            
            # LIMIT 주문 시 가격 누락 테스트
            with self.assertRaises(ValueError):
                self.api.create_order(order_type="LIMIT", price=None, test=True)
            
            error_handler.log_info("주문 파라미터 검증 테스트 성공")
            
        except Exception as e:
            error_handler.log_error(e, "주문 파라미터 검증 테스트 실패")
            raise

    def test_order_cancellation(self):
        """주문 취소 테스트"""
        try:
            # 테스트용 가상 주문 ID 생성
            test_order_id = 12345  # 테스트용 임의 주문 ID
            
            # 주문 취소 시도
            with self.assertRaises(Exception):
                cancel_result = self.api.cancel_order(
                    symbol=self.symbol,
                    order_id=test_order_id,
                    test=True
                )
            
            error_handler.log_info("주문 취소 테스트 성공: 예상된 에러 발생")
            
        except Exception as e:
            error_handler.log_error(e, "주문 취소 테스트 실패")
            raise

    def test_order_test_mode(self):
        """주문 테스트 모드 검증"""
        try:
            # 현재가 조회
            current_price = self.api.get_ticker_price(self.symbol)
            test_price = float(self._format_number(current_price * 0.95, 2))
            
            # 테스트 주문 실행
            test_result = self.api.create_order(
                symbol=self.symbol,
                order_type="LIMIT",
                side="BUY",
                quantity=0.001,
                price=test_price,
                test=True
            )
            
            # 테스트 모드에서는 빈 객체가 반환되는 것이 정상
            self.assertIsNotNone(test_result)
            error_handler.log_info(f"주문 테스트 모드 검증 성공: {test_result}")
            
        except Exception as e:
            error_handler.log_error(e, "주문 테스트 모드 검증 실패")
            raise

    def test_order_query(self):
        """주문 조회 테스트"""
        try:
            # 현재가 조회
            current_price = self.api.get_ticker_price(self.symbol)
            test_price = float(self._format_number(current_price * 0.95, 2))
            
            # 테스트 주문 생성
            order = self.api.create_order(
                symbol=self.symbol,
                order_type="LIMIT",
                side="BUY",
                quantity=0.001,
                price=test_price,
                test=True
            )
            
            # 테스트 모드에서는 주문 조회가 404를 반환하는 것이 정상
            with self.assertRaises(Exception):
                order_status = self.api.get_order(
                    symbol=self.symbol,
                    order_id=12345,  # 테스트용 임의 주문 ID
                    test=True
                )
            
            error_handler.log_info("주문 조회 테스트 성공: 예상된 에러 발생")
            
        except Exception as e:
            error_handler.log_error(e, "주문 조회 테스트 실패")
            raise

    def test_open_orders(self):
        """미체결 주문 목록 조회 테스트"""
        try:
            # 미체결 주문 목록 조회
            open_orders = self.api.get_open_orders(self.symbol)
            
            # 응답이 리스트인지 확인
            self.assertIsInstance(open_orders, list)
            error_handler.log_info(f"미체결 주문 조회 성공: {len(open_orders)}개 주문")
            
        except Exception as e:
            error_handler.log_error(e, "미체결 주문 조회 테스트 실패")
            raise

    def test_account_info(self):
        """계정 정보 조회 테스트"""
        try:
            # 계정 정보 조회
            account_info = self.api.get_account_info()
            
            # 필수 필드 확인
            self.assertIn('balances', account_info)
            self.assertIn('permissions', account_info)
            
            # 권한 목록이 비어있지 않은지 확인
            self.assertTrue(len(account_info['permissions']) > 0)
            
            # 권한 정보 로깅
            error_handler.log_info(f"계정 권한: {account_info['permissions']}")
            error_handler.log_info("계정 정보 조회 테스트 성공")
            
        except Exception as e:
            error_handler.log_error(e, "계정 정보 조회 테스트 실패")
            raise

    def test_asset_balance(self):
        """자산 잔고 조회 테스트"""
        try:
            # BTC 잔고 조회
            btc_balance = self.api.get_asset_balance("BTC")
            
            # 필수 필드 확인
            self.assertIn('free', btc_balance)
            self.assertIn('locked', btc_balance)
            self.assertIn('total', btc_balance)
            
            # 값 타입 확인
            self.assertIsInstance(btc_balance['free'], float)
            self.assertIsInstance(btc_balance['locked'], float)
            self.assertIsInstance(btc_balance['total'], float)
            
            # 총잔고 = 사용가능 + 거래중
            self.assertEqual(btc_balance['total'], 
                           btc_balance['free'] + btc_balance['locked'])
            
            error_handler.log_info(f"자산 잔고 조회 테스트 성공: {btc_balance}")
            
        except Exception as e:
            error_handler.log_error(e, "자산 잔고 조회 테스트 실패")
            raise

    def test_trade_history(self):
        """거래 내역 조회 테스트"""
        try:
            # 거래 내역 조회
            trades = self.api.get_my_trades(self.symbol)
            
            # 응답이 리스트인지 확인
            self.assertIsInstance(trades, list)
            
            # 각 거래 항목의 필수 필드 확인
            if trades:
                trade = trades[0]
                required_fields = ['symbol', 'id', 'orderId', 'price', 'qty', 
                                 'time', 'isBuyer', 'isMaker']
                for field in required_fields:
                    self.assertIn(field, trade)
            
            error_handler.log_info(f"거래 내역 조회 테스트 성공: {len(trades)}건")
            
        except Exception as e:
            error_handler.log_error(e, "거래 내역 조회 테스트 실패")
            raise

    def test_trade_history_summary(self):
        """거래 내역 요약 테스트"""
        try:
            # 거래 내역 요약 조회
            summary = self.api.get_trade_history_summary(self.symbol)
            
            # 필수 필드 확인
            required_fields = ['period', 'total_trades', 'buy_trades', 'sell_trades',
                             'total_buy_quantity', 'total_sell_quantity', 'net_position']
            for field in required_fields:
                self.assertIn(field, summary)
            
            # 값 검증
            self.assertGreaterEqual(summary['total_trades'], 0)
            self.assertEqual(summary['total_trades'], 
                           summary['buy_trades'] + summary['sell_trades'])
            
            error_handler.log_info(f"거래 내역 요약 테스트 성공: {summary}")
            
        except Exception as e:
            error_handler.log_error(e, "거래 내역 요약 테스트 실패")
            raise

    def test_klines_data(self):
        """K라인 데이터 조회 테스트"""
        try:
            # K라인 데이터 조회
            klines = self.api.get_klines(self.symbol, interval="1h", limit=100)
            
            # 응답이 리스트인지 확인
            self.assertIsInstance(klines, list)
            self.assertEqual(len(klines), 100)
            
            # 각 캔들의 데이터 구조 확인
            candle = klines[0]
            self.assertEqual(len(candle), 12)  # 바이낸스 K라인 데이터는 12개 필드
            
            error_handler.log_info(f"K라인 데이터 조회 테스트 성공: {len(klines)}개 캔들")
            
        except Exception as e:
            error_handler.log_error(e, "K라인 데이터 조회 테스트 실패")
            raise

    def test_market_depth(self):
        """시장 깊이 조회 테스트"""
        try:
            # 시장 깊이 조회
            depth = self.api.get_market_depth(self.symbol, limit=10)
            
            # 필수 필드 확인
            self.assertIn('bids', depth)
            self.assertIn('asks', depth)
            
            # 데이터 구조 확인
            self.assertEqual(len(depth['bids']), 10)
            self.assertEqual(len(depth['asks']), 10)
            
            # 가격 정렬 확인 (매수는 내림차순, 매도는 오름차순)
            bids = [float(price) for price, _ in depth['bids']]
            asks = [float(price) for price, _ in depth['asks']]
            self.assertEqual(bids, sorted(bids, reverse=True))
            self.assertEqual(asks, sorted(asks))
            
            error_handler.log_info("시장 깊이 조회 테스트 성공")
            
        except Exception as e:
            error_handler.log_error(e, "시장 깊이 조회 테스트 실패")
            raise

    def test_market_summary(self):
        """시장 요약 정보 조회 테스트"""
        try:
            # 시장 요약 정보 조회
            summary = self.api.get_market_summary(self.symbol)
            
            # 필수 필드 확인
            required_fields = ['symbol', 'price_change', 'price_change_percent',
                             'weighted_avg_price', 'high_price', 'low_price',
                             'volume', 'quote_volume']
            for field in required_fields:
                self.assertIn(field, summary)
            
            # 값 타입 확인
            self.assertIsInstance(summary['price_change'], float)
            self.assertIsInstance(summary['volume'], float)
            
            # 값 범위 확인
            self.assertGreater(summary['high_price'], summary['low_price'])
            
            error_handler.log_info(f"시장 요약 정보 조회 테스트 성공: {summary}")
            
        except Exception as e:
            error_handler.log_error(e, "시장 요약 정보 조회 테스트 실패")
            raise

if __name__ == '__main__':
    unittest.main() 