"""
HTTP API 클라이언트 유틸리티
"""
import httpx
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class APIClient:
    """HTTP API 클라이언트"""

    def __init__(self, base_url: str, timeout: int = 10):
        """
        Args:
            base_url: API 베이스 URL
            timeout: 요청 타임아웃 (초)
        """
        self.base_url = base_url
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """클라이언트 연결 종료"""
        await self.client.aclose()

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        GET 요청 수행

        Args:
            endpoint: API 엔드포인트
            params: 쿼리 파라미터
            headers: 요청 헤더

        Returns:
            JSON 응답 데이터

        Raises:
            httpx.HTTPError: HTTP 요청 실패
            ValueError: JSON 파싱 실패
        """
        url = f"{self.base_url}/{endpoint}"

        try:
            logger.info(f"GET 요청: {url}")
            logger.debug(f"파라미터: {params}")

            response = await self.client.get(url, params=params, headers=headers)
            response.raise_for_status()

            data = response.json()
            logger.debug(f"응답 데이터: {data}")

            return data

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP 에러 ({e.response.status_code}): {e}")
            raise
        except httpx.RequestError as e:
            logger.error(f"요청 에러: {e}")
            raise
        except ValueError as e:
            logger.error(f"JSON 파싱 에러: {e}")
            raise

    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        POST 요청 수행

        Args:
            endpoint: API 엔드포인트
            data: 폼 데이터
            json: JSON 데이터
            headers: 요청 헤더

        Returns:
            JSON 응답 데이터

        Raises:
            httpx.HTTPError: HTTP 요청 실패
            ValueError: JSON 파싱 실패
        """
        url = f"{self.base_url}/{endpoint}"

        try:
            logger.info(f"POST 요청: {url}")
            response = await self.client.post(
                url,
                data=data,
                json=json,
                headers=headers
            )
            response.raise_for_status()

            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP 에러 ({e.response.status_code}): {e}")
            raise
        except httpx.RequestError as e:
            logger.error(f"요청 에러: {e}")
            raise
        except ValueError as e:
            logger.error(f"JSON 파싱 에러: {e}")
            raise


# 전역 클라이언트 인스턴스 관리
_client_instance: Optional[APIClient] = None


def get_api_client(base_url: str, timeout: int = 10) -> APIClient:
    """
    API 클라이언트 싱글톤 인스턴스 반환

    Args:
        base_url: API 베이스 URL
        timeout: 요청 타임아웃

    Returns:
        APIClient 인스턴스
    """
    global _client_instance
    if _client_instance is None:
        _client_instance = APIClient(base_url, timeout)
    return _client_instance


async def close_api_client():
    """전역 API 클라이언트 종료"""
    global _client_instance
    if _client_instance is not None:
        await _client_instance.close()
        _client_instance = None