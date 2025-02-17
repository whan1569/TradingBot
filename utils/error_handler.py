from loguru import logger
import sys

# 로거 설정
logger.remove()  # 기본 핸들러 제거
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/error.log",  # 에러 로그 파일
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="1 day",  # 매일 로그 파일 갱신
    retention="7 days"  # 7일간 보관
)

def log_error(error, additional_info=None):
    """에러 로깅 함수"""
    error_message = f"Error: {str(error)}"
    if additional_info:
        error_message += f" | Additional Info: {additional_info}"
    logger.error(error_message)
    return error_message

def log_info(message):
    """정보 로깅 함수"""
    logger.info(message)
    return message
