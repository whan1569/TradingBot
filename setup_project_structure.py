import os

def create_directory_structure():
    # 기본 디렉토리 구조 정의
    directories = [
        'config',
        'utils',
        'tests'
    ]

    # 필요한 파일 목록 정의
    files = {
        'config/config.json': '{}',
        'config/api_keys.json': '{}',
        
        'utils/api_connector.py': '',
        'utils/error_handler.py': '',
        
        'tests/test_api_connection.py': '',
        
        '.env': 'BINANCE_API_KEY=your_api_key_here\nBINANCE_SECRET_KEY=your_secret_key_here',
        'requirements.txt': ''
    }

    # 디렉토리 생성
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

    # 파일 생성
    for file_path, content in files.items():
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created file: {file_path}")

def main():
    try:
        create_directory_structure()
        print("\n프로젝트 구조가 성공적으로 생성되었습니다!")
    except Exception as e:
        print(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    main() 