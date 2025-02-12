```mermaid
graph TD;
    A[Start main.py] --> B[trading_decision.py 실행]

    B --> C[signal_processing.py 실행 - 매매 신호 생성]
    B --> D[market_sentiment.py 실행 - 시장 심리 분석]
    B --> E[chart_analysis.py 실행 - 차트 분석]

    C --> B
    D --> B
    E --> B

    B --> F{매매 실행 여부}

    F -- LONG 또는 SHORT --> G[auto_trader.py 실행]
    F -- HOLD --> H[대기 후 재시작]

    G --> I[바이낸스 API 호출 - 매수/매도 주문]
    I --> J[거래 내역 저장 - trade_history.json]

    H -->|60초 후| A
    J -->|60초 후| A
