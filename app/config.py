"""
애플리케이션 설정 관리
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """애플리케이션 설정"""

    # API 설정
    weather_api_key: str
    weather_api_base_url: str

    # 애플리케이션 설정
    app_name: str = "날씨 조회 서비스"
    app_version: str = "1.0.0"

    # API 요청 설정
    api_timeout: int = 10  # 초
    api_retry_count: int = 311

    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }


@lru_cache()
def get_settings() -> Settings:
    """설정 싱글톤 인스턴스 반환"""
    return Settings()