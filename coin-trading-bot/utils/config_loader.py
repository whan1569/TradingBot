import json
import os

def load_config(file_path):
    """ JSON 파일을 로드하는 함수 """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Config file not found: {file_path}")
    
    with open(file_path, 'r') as file:
        return json.load(file)

# 설정 파일 로드
def get_system_config():
    return load_config("config/config.json")

def get_strategy_config():
    return load_config("config/strategy_config.json")

def get_api_keys():
    return load_config("config/api_keys.json")
