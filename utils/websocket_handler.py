import json
import asyncio
import websockets
from . import error_handler

class BinanceWebSocket:
    def __init__(self, symbol="btcusdt"):
        self.symbol = symbol.lower()
        self.ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@trade"
        self.ws = None
        self.is_connected = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 3  # 초기 재연결 대기 시간

    async def connect(self):
        """WebSocket 연결 수립"""
        try:
            self.ws = await websockets.connect(self.ws_url)
            self.is_connected = True
            self.reconnect_attempts = 0
            error_handler.log_info(f"WebSocket 연결 성공: {self.symbol}")
            return True
        except Exception as e:
            error_handler.log_error(e, "WebSocket 연결 실패")
            return False

    async def reconnect(self):
        """WebSocket 재연결 시도"""
        while self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            wait_time = self.reconnect_delay * self.reconnect_attempts
            error_handler.log_info(f"WebSocket 재연결 시도 {self.reconnect_attempts}/{self.max_reconnect_attempts} ({wait_time}초 후)")
            
            await asyncio.sleep(wait_time)
            
            if await self.connect():
                return True
        
        error_handler.log_error(None, "최대 재연결 시도 횟수 초과")
        return False

    async def receive_message(self):
        """메시지 수신"""
        if not self.ws:
            return None
        
        try:
            message = await self.ws.recv()
            return json.loads(message)
        except websockets.ConnectionClosed:
            self.is_connected = False
            error_handler.log_info("WebSocket 연결 종료됨, 재연결 시도 중...")
            if await self.reconnect():
                return await self.receive_message()
            return None
        except Exception as e:
            error_handler.log_error(e, "메시지 수신 실패")
            return None

    async def close(self):
        """WebSocket 연결 종료"""
        if self.ws:
            await self.ws.close()
            self.is_connected = False
            error_handler.log_info("WebSocket 연결 종료됨")
