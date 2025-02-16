import os
import json

def create_directory_structure():
    # 기본 경로 설정 (D 드라이브)
    base_path = "D:/TradingBot/coin-trading-bot"
    
    # 디렉토리 구조 정의
    directories = [
        "config",
        "data/raw",
        "data/processed",
        "data/historical",
        "strategies",
        "models",
        "execution",
        "backtest/test_results",
        "system",
        "utils",
        "dashboard/components",
        "dashboard/utils"
    ]
    
    # 기본 설정 파일 구조
    config_files = {
        "config/config.json": {
            "data_path": "D:/coin-trading-bot/data",
            "max_ram_usage": "8GB",
            "max_gpu_memory": "8GB",
            "cpu_cores": 6
        },
        "config/strategy_config.json": {
            "risk_level": "medium",
            "max_position_size": 0.1,
            "stop_loss_percentage": 2.0
        },
        "config/api_keys.json": {
            "exchange_api_key": "",
            "exchange_secret_key": "",
            "telegram_bot_token": ""
        }
    }
    
    # 디렉토리 생성
    for directory in directories:
        full_path = os.path.join(base_path, directory)
        os.makedirs(full_path, exist_ok=True)
        print(f"Created directory: {full_path}")
    
    # 설정 파일 생성
    for file_path, content in config_files.items():
        full_path = os.path.join(base_path, file_path)
        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=4)
        print(f"Created config file: {full_path}")
    
    # 주요 Python 파일 생성
    python_files = [
        "main.py",
        "strategies/market_sentiment.py",
        "strategies/chart_analysis.py",
        "strategies/signal_processing.py",
        "strategies/trading_decision.py",
        "strategies/adaptive_model_selector.py",
        "strategies/event_detector.py",
        "models/sentiment_model.py",
        "models/auto_optimize.py",
        "models/reinforcement_learning.py",
        "execution/trade_executor.py",
        "execution/risk_management.py",
        "execution/order_execution.py",
        "execution/adaptive_execution.py",
        "utils/config_loader.py",
        "utils/data_loader.py",
        "utils/api_connector.py",
        "utils/websocket_handler.py",
        "utils/logger.py",
        "dashboard/dashboard_main.py"
    ]
    
    for file_path in python_files:
        full_path = os.path.join(base_path, file_path)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write("# TODO: Implement this module\n")
        print(f"Created Python file: {full_path}")

if __name__ == "__main__":
    create_directory_structure()
    print("\n프로젝트 구조가 성공적으로 생성되었습니다!")
    print("다음 단계: API 연동 및 데이터 수집 구현을 시작하세요.") 