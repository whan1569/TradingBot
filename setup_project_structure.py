import os
import json

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"✅ 디렉토리 생성: {path}")

def create_file(path, content=""):
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 파일 생성: {path}")

# 기본 설정 파일 내용
config_json = {
    "api": {
        "binance": {
            "api_key": "",
            "api_secret": ""
        }
    },
    "trading": {
        "symbol": "BTC/USDT",
        "trade_amount": 0.001,
        "stop_loss": 0.5,
        "take_profit": 1.0
    }
}

trading_rules_json = {
    "max_trades_per_day": 10,
    "min_trade_interval": 60,
    "risk_percentage": 1.0
}

database_config_json = {
    "sqlite": {
        "path": "data/database.db"
    },
    "redis": {
        "host": "localhost",
        "port": 6379
    }
}

logging_config_json = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}

# 프로젝트 루트 디렉토리
root_dir = "D:/TradingBot/coin-trading-bot"

# 디렉토리 구조 생성
directories = [
    "config",
    "data/raw",
    "utils",
    "strategies",
    "execution",
    "models/saved_models",
    "models/backtest_results",
    "dashboard/components",
    "dashboard/templates",
    "dashboard/static",
    "notification",
    "exchanges",
    "tests/performance",
    "scripts"
]

for directory in directories:
    create_directory(os.path.join(root_dir, directory))

# 설정 파일 생성
config_files = {
    "config/config.json": json.dumps(config_json, indent=4),
    "config/trading_rules.json": json.dumps(trading_rules_json, indent=4),
    "config/database_config.json": json.dumps(database_config_json, indent=4),
    "config/logging_config.json": json.dumps(logging_config_json, indent=4),
    "config/api_keys.json": "{}"
}

for file_path, content in config_files.items():
    create_file(os.path.join(root_dir, file_path), content)

# Python 파일 생성
python_files = [
    "main.py",
    "setup.py",
    "data/market_data.py",
    "data/websocket_client.py",
    "data/database_manager.py",
    "data/data_preprocessor.py",
    "data/feature_engineering.py",
    "utils/logger.py",
    "utils/config_loader.py",
    "utils/api_connector.py",
    "utils/websocket_handler.py",
    "utils/cache_manager.py",
    "utils/error_handler.py",
    "utils/notification_manager.py",
    "strategies/signal_generator.py",
    "strategies/event_detector.py",
    "strategies/auto_strategy_selector.py",
    "strategies/reinforcement_learning.py",
    "strategies/risk_management.py",
    "execution/order_execution.py",
    "execution/adaptive_execution.py",
    "execution/position_sizing.py",
    "execution/market_impact.py",
    "models/reinforcement_learning.py",
    "models/auto_optimize.py",
    "models/model_trainer.py",
    "models/model_evaluator.py",
    "dashboard/dashboard_main.py",
    "dashboard/dashboard_api.py",
    "notification/telegram_bot.py",
    "notification/email_alerts.py",
    "notification/webhook_manager.py",
    "exchanges/upbit_api.py",
    "exchanges/binance_api.py",
    "exchanges/binance_order_manager.py",
    "exchanges/exchange_utils.py",
    "exchanges/api_rate_limiter.py",
    "tests/test_risk_management.py",
    "tests/test_order_execution.py",
    "tests/test_strategy_performance.py",
    "tests/test_websocket.py",
    "scripts/install.sh",
    "scripts/install.bat",
    "scripts/backtest_runner.py",
    "scripts/model_trainer.py",
    "scripts/db_cleanup.py",
    "scripts/update_checker.py"
]

for file_path in python_files:
    create_file(os.path.join(root_dir, file_path))

# requirements.txt 생성
with open('설계/라이브러리.txt', 'r', encoding='utf-8') as f:
    requirements_content = f.read()
create_file(os.path.join(root_dir, "requirements.txt"), requirements_content)

# README.md 생성
readme_content = """# Binance Trading Bot

## 개요
- 1분 단위 자동 트레이딩
- AutoML + 강화학습 기반 전략
- Binance API + WebSocket 활용
- 실시간 모니터링 대시보드

## 설치 방법
```bash
pip install -r requirements.txt
```

## 실행 방법
```bash
python main.py
```
"""

create_file(os.path.join(root_dir, "README.md"), readme_content)

print("✅ 프로젝트 구조 생성 완료!")