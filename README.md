# TradingBot

자동 트레이딩 시스템

## 현재 제한사항 및 임시 설정

### API 관련
- Rate Limit: 실제 2400/분 중 1200/분만 사용 (안전마진 확보)
- 가격 조회 간격: 최소 1초 (캐싱 적용)
- WebSocket 재연결: 최대 5회 시도

### 테스트 관련
- 실제 거래 기능 비활성화 (테스트 모드)
- 일부 에러 케이스 시뮬레이션 제외
- WebSocket 연결 테스트 시 짧은 시간만 유지

### 향후 개선 사항
- [ ] WebSocket으로 실시간 가격 수신 전환
- [ ] Rate Limit 동적 조정 기능
- [ ] 실제 거래 기능 활성화
- [ ] 전체 에러 케이스 테스트 추가

## 환경 설정

### 테스트 환경
- `auto_trading = False`: 자동 거래 비활성화
- `test = True`: API 호출 시 테스트 모드 사용
- `.env.test` 파일의 설정 사용

### 운영 환경
- `auto_trading = True`: 자동 거래 활성화 필수
- `test = False`: 실제 API 호출 사용
- `.env.prod` 파일의 설정 사용

> ⚠️ **주의**: 실제 운영 환경에서는 반드시 `auto_trading = True`로 설정해야 자동 거래가 작동합니다.

## 설정 파일 예시

**.env.prod**:
```
AUTO_TRADING=true
API_TEST_MODE=false
...
```

**.env.test**:
```
AUTO_TRADING=false
API_TEST_MODE=true
...
```