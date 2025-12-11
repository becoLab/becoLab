"""
로깅 설정 모듈
"""
import logging
import sys
import json
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime


# 로그 디렉토리 경로
LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


class PrettyFormatter(logging.Formatter):
    """이쁜 로그 포맷터 - 색상과 아이콘 추가"""

    # 로그 레벨별 색상 코드 (ANSI)
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    # 로그 레벨별 아이콘
    ICONS = {
        'DEBUG': '🔍',
        'INFO': '✅',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🚨'
    }

    def __init__(self, use_colors: bool = True, use_icons: bool = True):
        super().__init__()
        self.use_colors = use_colors
        self.use_icons = use_icons

    def format(self, record: logging.LogRecord) -> str:
        # 기본 정보
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        level = record.levelname

        # 색상 및 아이콘
        color = self.COLORS.get(level, self.COLORS['RESET']) if self.use_colors else ''
        reset = self.COLORS['RESET'] if self.use_colors else ''
        icon = self.ICONS.get(level, '📝') if self.use_icons else ''

        # Request ID 추출 (middleware에서 설정)
        try:
            from app.middleware.logging_middleware import get_request_id, get_client_ip
            request_id = get_request_id()
            client_ip = get_client_ip()
            req_info = f"[{request_id}] [{client_ip}]" if request_id else ""
        except:
            req_info = ""

        # 메시지 포맷
        if req_info:
            log_line = (
                f"{color}{timestamp} {icon} {level:8s}{reset} "
                f"{req_info} {record.getMessage()}"
            )
        else:
            log_line = (
                f"{color}{timestamp} {icon} {level:8s}{reset} "
                f"{record.getMessage()}"
            )

        # 예외 정보 추가
        if record.exc_info:
            log_line += f"\n{self.formatException(record.exc_info)}"

        return log_line


class JSONFormatter(logging.Formatter):
    """JSON 형식 로그 포맷터 - 로그 분석 도구 연동용"""

    def format(self, record: logging.LogRecord) -> str:
        # Request ID 및 IP 추출
        try:
            from app.middleware.logging_middleware import get_request_id, get_client_ip
            request_id = get_request_id()
            client_ip = get_client_ip()
        except:
            request_id = ""
            client_ip = ""

        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Request 정보 추가
        if request_id:
            log_data["request_id"] = request_id
        if client_ip:
            log_data["client_ip"] = client_ip

        # 예외 정보 추가
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False)


# 로그 포맷 인스턴스
PRETTY_FORMAT = PrettyFormatter(use_colors=True, use_icons=True)
CONSOLE_FORMAT = PrettyFormatter(use_colors=True, use_icons=False)  # 콘솔용 (아이콘 없음)
JSON_FORMAT = JSONFormatter()

# 레거시 포맷 (하위 호환성)
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
    backup_days: int = 30
):
    """
    로깅 설정 초기화 (일자별 로그 파일)

    Args:
        log_level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output: 콘솔 출력 여부
        file_output: 파일 출력 여부
        backup_days: 로그 파일 보관 일수 (기본: 30일)
    """
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # 기존 핸들러 제거 (중복 방지)
    root_logger.handlers.clear()

    # 콘솔 핸들러 (이쁜 포맷 + 색상)
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(CONSOLE_FORMAT)  # 이쁜 포맷 적용
        root_logger.addHandler(console_handler)

    # 파일 핸들러 (일자별 로테이션)
    if file_output:
        # 일반 로그 파일 (INFO 레벨 이상) - 이쁜 포맷
        app_log_file = LOG_DIR / "app.log"
        file_handler = TimedRotatingFileHandler(
            app_log_file,
            when='midnight',  # 매일 자정에 로테이션
            interval=1,  # 1일마다
            backupCount=backup_days,  # 보관 일수
            encoding='utf-8'
        )
        file_handler.suffix = "%Y-%m-%d"  # 백업 파일 날짜 형식
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(PRETTY_FORMAT)  # 이쁜 포맷 (색상 + 아이콘)
        root_logger.addHandler(file_handler)

        # 에러 로그 파일 (ERROR 레벨 이상만) - 이쁜 포맷
        error_log_file = LOG_DIR / "error.log"
        error_handler = TimedRotatingFileHandler(
            error_log_file,
            when='midnight',
            interval=1,
            backupCount=backup_days,
            encoding='utf-8'
        )
        error_handler.suffix = "%Y-%m-%d"
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(PRETTY_FORMAT)  # 이쁜 포맷
        root_logger.addHandler(error_handler)

        # JSON 로그 파일 (분석 도구용)
        json_log_file = LOG_DIR / "app.json.log"
        json_handler = TimedRotatingFileHandler(
            json_log_file,
            when='midnight',
            interval=1,
            backupCount=backup_days,
            encoding='utf-8'
        )
        json_handler.suffix = "%Y-%m-%d"
        json_handler.setLevel(logging.INFO)
        json_handler.setFormatter(JSON_FORMAT)  # JSON 포맷
        root_logger.addHandler(json_handler)

    # uvicorn 로거 설정
    uvicorn_access = logging.getLogger("uvicorn.access")
    uvicorn_access.handlers.clear()

    if file_output:
        # 액세스 로그 파일 - 매일 자정에 새 파일 생성
        access_log_file = LOG_DIR / "access.log"
        access_handler = TimedRotatingFileHandler(
            access_log_file,
            when='midnight',
            interval=1,
            backupCount=backup_days,
            encoding='utf-8'
        )
        access_handler.suffix = "%Y-%m-%d"
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
    logging.info(f"로그 보관 일수: {backup_days}일")
    logging.info(f"일반 로그: {LOG_DIR}/app.log (매일 자정 로테이션)")
    logging.info(f"에러 로그: {LOG_DIR}/error.log (매일 자정 로테이션)")
    logging.info(f"액세스 로그: {LOG_DIR}/access.log (매일 자정 로테이션)")
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