import os
import time
import ccxt
import requests
from dotenv import load_dotenv
from . import error_handler
import hmac
import hashlib
from datetime import datetime

# .env 파일에서 환경변수 로드
load_dotenv()

class BinanceAPI:
    def __init__(self):
        """Binance API 초기화"""
        try:
            self.exchange = ccxt.binance({
                'apiKey': os.getenv('BINANCE_API_KEY'),
                'secret': os.getenv('BINANCE_SECRET_KEY'),
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot',
                    'adjustForTimeDifference': True,
                    'recvWindow': 10000
                }
            })
            self.base_url = "https://api.binance.com"
            
            # TODO: 실제 운영 시 조정 필요한 설정들
            self.request_count = 0
            self.last_request_time = time.time()
            self.rate_limit = {
                'max_requests': 1200,  # 1분당 최대 요청 수 (실제 제한: 2400)
                'time_window': 60      # 시간 윈도우 (초)
            }
            
            # FIXME: 테스트용 임시 설정
            self.price_update_interval = 1.0  # 가격 업데이트 최소 간격 (초)
            self.use_price_caching = True     # 가격 캐싱 사용 여부
            
            error_handler.log_info("Binance API 초기화 완료")
        except Exception as e:
            error_handler.log_error(e, "Binance API 초기화 실패")
            raise

    def _check_rate_limit(self):
        """Rate Limit 체크 및 대기"""
        current_time = time.time()
        time_passed = current_time - self.last_request_time
        
        # 시간 윈도우가 지나면 카운터 리셋
        if time_passed >= self.rate_limit['time_window']:
            self.request_count = 0
            self.last_request_time = current_time
        
        # Rate Limit 초과 시 대기
        if self.request_count >= self.rate_limit['max_requests']:
            wait_time = self.rate_limit['time_window'] - time_passed
            if wait_time > 0:
                error_handler.log_info(f"Rate Limit 도달, {wait_time:.2f}초 대기")
                time.sleep(wait_time)
                self.request_count = 0
                self.last_request_time = time.time()
        
        self.request_count += 1

    def get_server_time(self):
        """서버 시간 조회"""
        try:
            server_time = self.exchange.fetch_time()
            error_handler.log_info(f"서버 시간 조회 성공: {server_time}")
            return server_time
        except Exception as e:
            error_handler.log_error(e, "서버 시간 조회 실패")
            raise

    def test_connection(self):
        """API 연결 테스트"""
        try:
            self.get_server_time()
            error_handler.log_info("API 연결 테스트 성공")
            return True
        except Exception as e:
            error_handler.log_error(e, "API 연결 테스트 실패")
            return False

    def get_ticker_price(self, symbol="BTCUSDT"):
        """REST API를 통한 현재가 조회 (Rate Limit 적용)"""
        try:
            current_time = time.time()
            
            # FIXME: 테스트 단계에서만 사용하는 캐싱 로직
            # 실제 운영 시에는 WebSocket으로 실시간 가격 수신으로 변경 예정
            if self.use_price_caching and hasattr(self, 'last_price_check'):
                if current_time - self.last_price_check < self.price_update_interval:
                    return self.last_price  # 캐시된 가격 반환
            
            self._check_rate_limit()
            url = f"{self.base_url}/api/v3/ticker/price"
            params = {'symbol': symbol}
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            price = float(data['price'])
            
            # 마지막 요청 시간과 가격 저장
            self.last_price_check = current_time
            self.last_price = price
            
            error_handler.log_info(f"현재가 조회 성공: {symbol} = {price}")
            return price
        except Exception as e:
            error_handler.log_error(e, f"{symbol} 현재가 조회 실패")
            raise

    def get_recent_trades(self, symbol="BTCUSDT", limit=1):
        """최근 체결 내역 조회 (Public API 사용)"""
        try:
            url = f"{self.base_url}/api/v3/trades"
            params = {'symbol': symbol, 'limit': limit}
            response = requests.get(url, params=params)
            response.raise_for_status()
            trades = response.json()
            latest_trade = trades[-1]
            error_handler.log_info(f"최근 거래 조회 성공: {symbol} = {latest_trade['price']}")
            return {'price': float(latest_trade['price'])}
        except Exception as e:
            error_handler.log_error(e, f"{symbol} 최근 거래 조회 실패")
            raise

    def test_rate_limit(self, requests_count=1300):
        """Rate Limit 테스트를 위한 메서드"""
        success_count = 0
        start_time = time.time()
        
        try:
            for i in range(requests_count):
                try:
                    self.get_ticker_price()
                    success_count += 1
                    if (i + 1) % 100 == 0:
                        error_handler.log_info(f"처리된 요청: {i + 1}/{requests_count}")
                except Exception as e:
                    error_handler.log_error(e, f"요청 {i + 1} 실패")
                    continue
            
            total_time = time.time() - start_time
            error_handler.log_info(f"Rate Limit 테스트 완료: {success_count}/{requests_count} 성공, 소요시간: {total_time:.2f}초")
            return success_count, total_time
            
        except Exception as e:
            error_handler.log_error(e, "Rate Limit 테스트 실패")
            raise

    def create_order(self, symbol="BTCUSDT", order_type="LIMIT", side="BUY", 
                    quantity=0.001, price=None, test=True):
        """주문 생성 (테스트 모드 지원)"""
        try:
            self._validate_order_params(symbol, order_type, side, quantity, price)
            
            # 기본 파라미터 설정
            params = {
                'symbol': symbol,
                'side': side,
                'type': order_type,
                'quantity': self._format_number(quantity, 5),
                'timestamp': int(time.time() * 1000),
                'recvWindow': 5000
            }
            
            if order_type == "LIMIT":
                params['price'] = self._format_number(price, 2)
                params['timeInForce'] = 'GTC'
            
            # 파라미터를 정렬된 쿼리 스트링으로 변환
            query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
            
            # 서명 생성 및 추가
            signature = hmac.new(
                self.exchange.secret.encode('utf-8'),
                query_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # 최종 요청 URL 생성
            endpoint = "/api/v3/order/test" if test else "/api/v3/order"
            url = f"{self.base_url}{endpoint}?{query_string}&signature={signature}"
            
            # API 요청 헤더
            headers = {'X-MBX-APIKEY': os.getenv('BINANCE_API_KEY')}
            
            # POST 요청 실행
            response = requests.post(url, headers=headers)
            
            if response.status_code != 200:
                error_handler.log_error(f"API 응답: {response.text}", "주문 생성 실패")
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            error_handler.log_error(e, "주문 생성 실패")
            raise

    def _format_number(self, number, decimals):
        """숫자 포맷팅 (정밀도 조정)"""
        format_str = f"{{:.{decimals}f}}"
        return format_str.format(number)

    def _validate_order_params(self, symbol, order_type, side, quantity, price=None):
        """주문 파라미터 검증"""
        # 심볼 검증
        if not isinstance(symbol, str) or len(symbol) < 5:
            raise ValueError("유효하지 않은 심볼입니다.")
            
        # 주문 타입 검증
        valid_order_types = ["MARKET", "LIMIT"]
        if order_type not in valid_order_types:
            raise ValueError(f"유효하지 않은 주문 타입입니다. 가능한 값: {valid_order_types}")
            
        # 매수/매도 구분 검증
        valid_sides = ["BUY", "SELL"]
        if side not in valid_sides:
            raise ValueError(f"유효하지 않은 거래 구분입니다. 가능한 값: {valid_sides}")
            
        # 수량 검증
        if not isinstance(quantity, (int, float)) or quantity <= 0:
            raise ValueError("수량은 양수여야 합니다.")
            
        # 가격 검증 (LIMIT 주문의 경우)
        if order_type == "LIMIT":
            if not price or not isinstance(price, (int, float)) or price <= 0:
                raise ValueError("LIMIT 주문의 경우 유효한 가격이 필요합니다.")

    def cancel_order(self, symbol="BTCUSDT", order_id=None, test=True):
        """주문 취소 (테스트 모드 지원)"""
        try:
            # 기본 파라미터 설정
            params = {
                'symbol': symbol,
                'orderId': order_id,
                'timestamp': int(time.time() * 1000),
                'recvWindow': 5000
            }
            
            # 파라미터를 정렬된 쿼리 스트링으로 변환
            query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
            
            # 서명 생성 및 추가
            signature = hmac.new(
                self.exchange.secret.encode('utf-8'),
                query_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # 최종 요청 URL 생성
            endpoint = "/api/v3/order/test" if test else "/api/v3/order"
            url = f"{self.base_url}{endpoint}?{query_string}&signature={signature}"
            
            # API 요청 헤더
            headers = {'X-MBX-APIKEY': os.getenv('BINANCE_API_KEY')}
            
            # DELETE 요청 실행
            response = requests.delete(url, headers=headers)
            
            if response.status_code != 200:
                error_handler.log_error(f"API 응답: {response.text}", "주문 취소 실패")
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            error_handler.log_error(e, "주문 취소 실패")
            raise

    def get_order(self, symbol="BTCUSDT", order_id=None, test=True):
        """주문 조회"""
        try:
            # 기본 파라미터 설정
            params = {
                'symbol': symbol,
                'orderId': order_id,
                'timestamp': int(time.time() * 1000),
                'recvWindow': 5000
            }
            
            # 파라미터를 정렬된 쿼리 스트링으로 변환
            query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
            
            # 서명 생성 및 추가
            signature = hmac.new(
                self.exchange.secret.encode('utf-8'),
                query_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # 최종 요청 URL 생성
            endpoint = "/api/v3/order"
            url = f"{self.base_url}{endpoint}?{query_string}&signature={signature}"
            
            # API 요청 헤더
            headers = {'X-MBX-APIKEY': os.getenv('BINANCE_API_KEY')}
            
            # GET 요청 실행
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                error_handler.log_error(f"API 응답: {response.text}", "주문 조회 실패")
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            error_handler.log_error(e, "주문 조회 실패")
            raise

    def get_open_orders(self, symbol="BTCUSDT"):
        """미체결 주문 목록 조회"""
        try:
            # 기본 파라미터 설정
            params = {
                'symbol': symbol,
                'timestamp': int(time.time() * 1000),
                'recvWindow': 5000
            }
            
            # 파라미터를 정렬된 쿼리 스트링으로 변환
            query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
            
            # 서명 생성 및 추가
            signature = hmac.new(
                self.exchange.secret.encode('utf-8'),
                query_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # 최종 요청 URL 생성
            endpoint = "/api/v3/openOrders"
            url = f"{self.base_url}{endpoint}?{query_string}&signature={signature}"
            
            # API 요청 헤더
            headers = {'X-MBX-APIKEY': os.getenv('BINANCE_API_KEY')}
            
            # GET 요청 실행
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                error_handler.log_error(f"API 응답: {response.text}", "미체결 주문 조회 실패")
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            error_handler.log_error(e, "미체결 주문 조회 실패")
            raise

    def get_account_info(self):
        """계정 정보 조회 (잔고 포함)"""
        try:
            # 기본 파라미터 설정
            params = {
                'timestamp': int(time.time() * 1000),
                'recvWindow': 5000
            }
            
            # 파라미터를 정렬된 쿼리 스트링으로 변환
            query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
            
            # 서명 생성 및 추가
            signature = hmac.new(
                self.exchange.secret.encode('utf-8'),
                query_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # 최종 요청 URL 생성
            endpoint = "/api/v3/account"
            url = f"{self.base_url}{endpoint}?{query_string}&signature={signature}"
            
            # API 요청 헤더
            headers = {'X-MBX-APIKEY': os.getenv('BINANCE_API_KEY')}
            
            # GET 요청 실행
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                error_handler.log_error(f"API 응답: {response.text}", "계정 정보 조회 실패")
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            error_handler.log_error(e, "계정 정보 조회 실패")
            raise

    def get_asset_balance(self, asset="BTC"):
        """특정 자산의 잔고 조회"""
        try:
            account_info = self.get_account_info()
            balances = account_info['balances']
            
            # 특정 자산 찾기
            for balance in balances:
                if balance['asset'] == asset:
                    free = float(balance['free'])
                    locked = float(balance['locked'])
                    total = free + locked
                    
                    error_handler.log_info(f"{asset} 잔고 조회 성공: 사용가능={free}, 거래중={locked}, 총잔고={total}")
                    return {
                        'asset': asset,
                        'free': free,
                        'locked': locked,
                        'total': total
                    }
            
            raise ValueError(f"{asset} 자산을 찾을 수 없습니다.")
            
        except Exception as e:
            error_handler.log_error(e, f"{asset} 잔고 조회 실패")
            raise

    def get_my_trades(self, symbol="BTCUSDT", limit=500):
        """내 거래 내역 조회"""
        try:
            # 기본 파라미터 설정
            params = {
                'symbol': symbol,
                'limit': limit,
                'timestamp': int(time.time() * 1000),
                'recvWindow': 5000
            }
            
            # 파라미터를 정렬된 쿼리 스트링으로 변환
            query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
            
            # 서명 생성 및 추가
            signature = hmac.new(
                self.exchange.secret.encode('utf-8'),
                query_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # 최종 요청 URL 생성
            endpoint = "/api/v3/myTrades"
            url = f"{self.base_url}{endpoint}?{query_string}&signature={signature}"
            
            # API 요청 헤더
            headers = {'X-MBX-APIKEY': os.getenv('BINANCE_API_KEY')}
            
            # GET 요청 실행
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                error_handler.log_error(f"API 응답: {response.text}", "거래 내역 조회 실패")
            response.raise_for_status()
            
            trades = response.json()
            error_handler.log_info(f"거래 내역 조회 성공: {len(trades)}건")
            return trades
            
        except Exception as e:
            error_handler.log_error(e, "거래 내역 조회 실패")
            raise

    def get_trade_history_summary(self, symbol="BTCUSDT", days=30):
        """거래 내역 요약 정보 조회"""
        try:
            trades = self.get_my_trades(symbol)
            
            # 최근 N일 동안의 거래만 필터링
            cutoff_time = int(time.time() * 1000) - (days * 24 * 60 * 60 * 1000)
            recent_trades = [t for t in trades if t['time'] > cutoff_time]
            
            # 거래 통계 계산
            total_trades = len(recent_trades)
            buy_trades = [t for t in recent_trades if t['isBuyer']]
            sell_trades = [t for t in recent_trades if not t['isBuyer']]
            
            total_buy_qty = sum(float(t['qty']) for t in buy_trades)
            total_sell_qty = sum(float(t['qty']) for t in sell_trades)
            
            summary = {
                'period': f"최근 {days}일",
                'total_trades': total_trades,
                'buy_trades': len(buy_trades),
                'sell_trades': len(sell_trades),
                'total_buy_quantity': total_buy_qty,
                'total_sell_quantity': total_sell_qty,
                'net_position': total_buy_qty - total_sell_qty
            }
            
            error_handler.log_info(f"거래 내역 요약: {summary}")
            return summary
            
        except Exception as e:
            error_handler.log_error(e, "거래 내역 요약 조회 실패")
            raise

    def get_klines(self, symbol="BTCUSDT", interval="1h", limit=500):
        """K라인(캔들스틱) 데이터 조회"""
        try:
            # 기본 파라미터 설정
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            
            # 엔드포인트 설정
            endpoint = "/api/v3/klines"
            url = f"{self.base_url}{endpoint}"
            
            # GET 요청 실행
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            klines = response.json()
            error_handler.log_info(f"K라인 데이터 조회 성공: {len(klines)}개")
            return klines
            
        except Exception as e:
            error_handler.log_error(e, "K라인 데이터 조회 실패")
            raise

    def get_market_depth(self, symbol="BTCUSDT", limit=100):
        """시장 깊이(호가창) 조회"""
        try:
            # 기본 파라미터 설정
            params = {
                'symbol': symbol,
                'limit': limit
            }
            
            # 엔드포인트 설정
            endpoint = "/api/v3/depth"
            url = f"{self.base_url}{endpoint}"
            
            # GET 요청 실행
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            depth = response.json()
            error_handler.log_info(f"시장 깊이 조회 성공: {len(depth['bids'])}개 매수호가, {len(depth['asks'])}개 매도호가")
            return depth
            
        except Exception as e:
            error_handler.log_error(e, "시장 깊이 조회 실패")
            raise

    def get_market_summary(self, symbol="BTCUSDT"):
        """시장 요약 정보 조회"""
        try:
            # 24시간 티커 정보 조회
            endpoint = "/api/v3/ticker/24hr"
            url = f"{self.base_url}{endpoint}"
            params = {'symbol': symbol}
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            ticker = response.json()
            summary = {
                'symbol': ticker['symbol'],
                'price_change': float(ticker['priceChange']),
                'price_change_percent': float(ticker['priceChangePercent']),
                'weighted_avg_price': float(ticker['weightedAvgPrice']),
                'high_price': float(ticker['highPrice']),
                'low_price': float(ticker['lowPrice']),
                'volume': float(ticker['volume']),
                'quote_volume': float(ticker['quoteVolume'])
            }
            
            error_handler.log_info(f"시장 요약 정보 조회 성공: {symbol}")
            return summary
            
        except Exception as e:
            error_handler.log_error(e, "시장 요약 정보 조회 실패")
            raise

    def get_historical_klines(self, symbol, interval, start_str, end_str=None):
        """과거 K라인(캔들스틱) 데이터 조회"""
        try:
            # 기본 파라미터 설정
            params = {
                'symbol': symbol,
                'interval': interval,
                'startTime': int(datetime.strptime(start_str, '%Y-%m-%d').timestamp() * 1000)
            }
            
            if end_str:
                params['endTime'] = int(datetime.strptime(end_str, '%Y-%m-%d').timestamp() * 1000)
            
            # 엔드포인트 설정
            endpoint = "/api/v3/klines"
            url = f"{self.base_url}{endpoint}"
            
            # GET 요청 실행
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            klines = response.json()
            error_handler.log_info(f"과거 데이터 조회 성공: {len(klines)}개 캔들")
            return klines
            
        except Exception as e:
            error_handler.log_error(e, "과거 데이터 조회 실패")
            raise
