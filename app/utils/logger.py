"""
로깅 설정 모듈
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime


# 로그 디렉토리 경로
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 로그 파일 경로
APP_LOG_FILE = LOG_DIR / "app.log"
ERROR_LOG_FILE = LOG_DIR / "error.log"
ACCESS_LOG_FILE = LOG_DIR / "access.log"

# 로그 포맷
DETAILED_FORMAT = logging.Formatter(
    fmt='%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

SIMPLE_FORMAT = logging.Formatter(
    fmt='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def setup_logging(
    log_level: str = "INFO",
    console_output: bool = True,
    file_output: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
):
    """
    로깅 설정 초기화

    Args:
        log_level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output: 콘솔 출력 여부
        file_output: 파일 출력 여부
        max_bytes: 로그 파일 최대 크기 (바이트)
        backup_count: 백업 파일 개수
    """
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # 기존 핸들러 제거 (중복 방지)
    root_logger.handlers.clear()

    # 콘솔 핸들러
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(SIMPLE_FORMAT)
        root_logger.addHandler(console_handler)

    # 파일 핸들러
    if file_output:
        # 일반 로그 파일 (INFO 레벨 이상)
        file_handler = RotatingFileHandler(
            APP_LOG_FILE,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(DETAILED_FORMAT)
        root_logger.addHandler(file_handler)

        # 에러 로그 파일 (ERROR 레벨 이상만)
        error_handler = RotatingFileHandler(
            ERROR_LOG_FILE,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(DETAILED_FORMAT)
        root_logger.addHandler(error_handler)

    # uvicorn 로거 설정
    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.handlers.clear()

    if file_output:
        # 액세스 로그 파일
        access_handler = RotatingFileHandler(
            ACCESS_LOG_FILE,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        access_handler.setLevel(logging.INFO)
        access_handler.setFormatter(SIMPLE_FORMAT)
        uvicorn_access.addHandler(access_handler)

    # httpx 로거 레벨 조정 (너무 많은 디버그 로그 방지)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

    logging.info("=" * 80)
    logging.info(f"로깅 시스템 초기화 완료 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"로그 레벨: {log_level.upper()}")
    logging.info(f"로그 디렉토리: {LOG_DIR}")
    logging.info(f"일반 로그: {APP_LOG_FILE}")
    logging.info(f"에러 로그: {ERROR_LOG_FILE}")
    logging.info(f"액세스 로그: {ACCESS_LOG_FILE}")
    logging.info("=" * 80)


def get_logger(name: str) -> logging.Logger:
    """
    모듈별 로거 반환

    Args:
        name: 로거 이름 (보통 __name__ 사용)

    Returns:
        Logger 객체
    """
    return logging.getLogger(name)