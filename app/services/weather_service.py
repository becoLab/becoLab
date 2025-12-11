"""
날씨 API 서비스
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional
from fastapi import HTTPException

from app.config import get_settings
from app.utils.api_client import get_api_client
from app.models.weather import WeatherResponse, WeatherItem, WeatherSummary, ForecastItem

logger = logging.getLogger(__name__)

# 기상청 자료구분코드 메타데이터 (이름, 단위)
CATEGORY_METADATA = {
    # 초단기실황
    "T1H": {"name": "기온", "unit": "℃"},
    "RN1": {"name": "1시간 강수량", "unit": "mm"},
    "UUU": {"name": "동서바람성분", "unit": "m/s"},
    "VVV": {"name": "남북바람성분", "unit": "m/s"},
    "REH": {"name": "습도", "unit": "%"},
    "PTY": {"name": "강수형태", "unit": "코드값"},
    "VEC": {"name": "풍향", "unit": "deg"},
    "WSD": {"name": "풍속", "unit": "m/s"},

    # 초단기예보 추가
    "SKY": {"name": "하늘상태", "unit": "코드값"},
    "LGT": {"name": "낙뢰", "unit": "kA"},

    # 단기예보 추가
    "TMP": {"name": "기온", "unit": "℃"},
    "POP": {"name": "강수확률", "unit": "%"},
    "WAV": {"name": "파고", "unit": "M"},
    "PCP": {"name": "강수량", "unit": "mm"},
    "SNO": {"name": "적설량", "unit": "cm"},
    "TMN": {"name": "최저기온", "unit": "℃"},
    "TMX": {"name": "최고기온", "unit": "℃"}
}

# 코드값 매핑 (하늘상태, 강수형태 등)
CODE_VALUE_MAPPINGS = {
    "SKY": {
        "1": "맑음",
        "3": "구름많음",
        "4": "흐림"
    },
    "PTY": {
        "0": "없음",
        "1": "비",
        "2": "비/눈",
        "3": "눈",
        "4": "소나기"
    }
}

# 하위 호환성을 위한 기존 매핑 유지
WEATHER_CATEGORY_MAP = {k: v["name"] for k, v in CATEGORY_METADATA.items() if k in ["T1H", "RN1", "UUU", "VVV", "REH", "PTY", "VEC", "WSD"]}
FORECAST_CATEGORY_MAP = {k: v["name"] for k, v in CATEGORY_METADATA.items() if k in ["T1H", "RN1", "SKY", "UUU", "VVV", "REH", "PTY", "LGT", "VEC", "WSD"]}
SHORT_TERM_FORECAST_CATEGORY_MAP = {k: v["name"] for k, v in CATEGORY_METADATA.items() if k in ["TMP", "UUU", "VVV", "VEC", "WSD", "SKY", "PTY", "POP", "WAV", "PCP", "REH", "SNO", "TMN", "TMX"]}


class WeatherService:
    """날씨 데이터 조회 서비스"""

    def __init__(self):
        self.settings = get_settings()
        self.client = get_api_client(
            base_url=self.settings.weather_api_base_url,
            timeout=self.settings.api_timeout
        )

    async def get_ultra_short_term_ncst(
        self,
        nx: int,
        ny: int,
        base_date: Optional[str] = None,
        base_time: Optional[str] = None,
        num_of_rows: int = 1000,
        page_no: int = 1
    ) -> WeatherResponse:
        """
        초단기실황조회

        Args:
            nx: 예보지점 X 좌표
            ny: 예보지점 Y 좌표
            base_date: 발표일자 (YYYYMMDD), 미지정시 오늘 날짜
            base_time: 발표시각 (HHMM), 미지정시 현재 시각 기준
            num_of_rows: 한 페이지 결과 수
            page_no: 페이지 번호

        Returns:
            WeatherResponse 객체

        Raises:
            HTTPException: API 호출 실패시
        """
        # 기본값 설정
        if base_date is None:
            base_date = datetime.now().strftime("%Y%m%d")

        if base_time is None:
            # 기상청 API는 매시간 정각 데이터 제공
            current_time = datetime.now()
            base_time = f"{current_time.hour:02d}00"

        params = {
            "serviceKey": self.settings.weather_api_key,
            "pageNo": page_no,
            "numOfRows": num_of_rows,
            "dataType": "JSON",
            "base_date": base_date,
            "base_time": base_time,
            "nx": nx,
            "ny": ny
        }

        try:
            logger.info(f"날씨 데이터 조회: nx={nx}, ny={ny}, date={base_date}, time={base_time}")
            data = await self.client.get("getUltraSrtNcst", params=params)

            # API 응답 구조 파싱
            response_data = data.get("response", {})
            header = response_data.get("header", {})
            body = response_data.get("body", {})

            result_code = header.get("resultCode", "")
            result_msg = header.get("resultMsg", "")

            # API 에러 확인
            if result_code != "00":
                logger.error(f"API 에러: {result_code} - {result_msg}")
                raise HTTPException(
                    status_code=502,
                    detail=f"기상청 API 오류: {result_msg}"
                )

            # 데이터 파싱 및 메타데이터 추가
            items_data = body.get("items", {}).get("item", [])
            items = []
            for item_data in items_data:
                category = item_data.get("category")
                obsrValue = item_data.get("obsrValue")
                metadata = CATEGORY_METADATA.get(category, {})

                # 코드값 설명 조회
                value_description = None
                if category in CODE_VALUE_MAPPINGS:
                    value_description = CODE_VALUE_MAPPINGS[category].get(obsrValue)

                item = WeatherItem(
                    **item_data,
                    categoryName=metadata.get("name"),
                    unit=metadata.get("unit"),
                    valueDescription=value_description
                )
                items.append(item)

            return WeatherResponse(
                result_code=result_code,
                result_message=result_msg,
                num_of_rows=body.get("numOfRows", 0),
                page_no=body.get("pageNo", 1),
                total_count=body.get("totalCount", 0),
                items=items
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"날씨 데이터 조회 실패: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"날씨 데이터 조회 중 오류가 발생했습니다: {str(e)}"
            )

    async def get_weather_summary(
        self,
        nx: int,
        ny: int,
        base_date: Optional[str] = None,
        base_time: Optional[str] = None
    ) -> WeatherSummary:
        """
        날씨 요약 정보 조회

        Args:
            nx: 예보지점 X 좌표
            ny: 예보지점 Y 좌표
            base_date: 발표일자 (YYYYMMDD)
            base_time: 발표시각 (HHMM)

        Returns:
            WeatherSummary 객체
        """
        weather_response = await self.get_ultra_short_term_ncst(
            nx=nx,
            ny=ny,
            base_date=base_date,
            base_time=base_time
        )

        # 데이터 변환
        weather_data = {}
        for item in weather_response.items:
            category = item.category
            weather_data[category] = item.obsrValue

        # 기본 정보
        first_item = weather_response.items[0] if weather_response.items else None
        used_base_date = first_item.baseDate if first_item else base_date or datetime.now().strftime("%Y%m%d")
        used_base_time = first_item.baseTime if first_item else base_time or datetime.now().strftime("%H00")

        summary = WeatherSummary(
            location=f"nx:{nx}, ny:{ny}",
            base_date=used_base_date,
            base_time=used_base_time,
            temperature=weather_data.get("T1H"),
            humidity=weather_data.get("REH"),
            precipitation=weather_data.get("RN1"),
            wind_direction=weather_data.get("VEC"),
            wind_speed=weather_data.get("WSD"),
            raw_data={
                "total_count": weather_response.total_count,
                "categories": {
                    cat: {
                        "value": val,
                        "description": WEATHER_CATEGORY_MAP.get(cat, cat)
                    }
                    for cat, val in weather_data.items()
                }
            }
        )

        return summary

    async def get_ultra_short_term_fcst(
        self,
        nx: int,
        ny: int,
        base_date: Optional[str] = None,
        base_time: Optional[str] = None,
        num_of_rows: int = 1000,
        page_no: int = 1
    ) -> list[ForecastItem]:
        """
        초단기예보조회

        Args:
            nx: 예보지점 X 좌표
            ny: 예보지점 Y 좌표
            base_date: 발표일자 (YYYYMMDD), 미지정시 오늘 날짜
            base_time: 발표시각 (HHMM), 미지정시 현재 시각 기준
            num_of_rows: 한 페이지 결과 수
            page_no: 페이지 번호

        Returns:
            ForecastItem 리스트

        Raises:
            HTTPException: API 호출 실패시
        """
        # 기본값 설정
        if base_date is None:
            base_date = datetime.now().strftime("%Y%m%d")

        if base_time is None:
            # 기상청 API는 매시간 정각 데이터 제공
            current_time = datetime.now()
            base_time = f"{current_time.hour:02d}30"  # 초단기예보는 30분 단위

        params = {
            "serviceKey": self.settings.weather_api_key,
            "pageNo": page_no,
            "numOfRows": num_of_rows,
            "dataType": "JSON",
            "base_date": base_date,
            "base_time": base_time,
            "nx": nx,
            "ny": ny
        }

        try:
            logger.info(f"예보 데이터 조회: nx={nx}, ny={ny}, date={base_date}, time={base_time}")
            data = await self.client.get("getUltraSrtFcst", params=params)

            # API 응답 구조 파싱
            response_data = data.get("response", {})
            header = response_data.get("header", {})
            body = response_data.get("body", {})

            result_code = header.get("resultCode", "")
            result_msg = header.get("resultMsg", "")

            # API 에러 확인
            if result_code != "00":
                logger.error(f"API 에러: {result_code} - {result_msg}")
                raise HTTPException(
                    status_code=502,
                    detail=f"기상청 API 오류: {result_msg}"
                )

            # 데이터 파싱 및 메타데이터 추가
            items_data = body.get("items", {}).get("item", [])
            forecast_items = []
            for item_data in items_data:
                category = item_data.get("category")
                fcstValue = item_data.get("fcstValue")
                metadata = CATEGORY_METADATA.get(category, {})

                # 코드값 설명 조회
                value_description = None
                if category in CODE_VALUE_MAPPINGS:
                    value_description = CODE_VALUE_MAPPINGS[category].get(fcstValue)

                item = ForecastItem(
                    **item_data,
                    categoryName=metadata.get("name"),
                    unit=metadata.get("unit"),
                    valueDescription=value_description
                )
                forecast_items.append(item)

            return forecast_items

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"예보 데이터 조회 실패: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"예보 데이터 조회 중 오류가 발생했습니다: {str(e)}"
            )

    async def get_combined_weather(
        self,
        nx: int,
        ny: int,
        base_date: Optional[str] = None,
        base_time: Optional[str] = None,
        num_of_rows: int = 1000,
        page_no: int = 1
    ) -> WeatherResponse:
        """
        초단기실황 + 초단기예보 통합 조회 (병렬 처리)

        Args:
            nx: 예보지점 X 좌표
            ny: 예보지점 Y 좌표
            base_date: 발표일자 (YYYYMMDD), 미지정시 오늘 날짜
            base_time: 발표시각 (HHMM), 미지정시 현재 시각 기준
            num_of_rows: 한 페이지 결과 수
            page_no: 페이지 번호

        Returns:
            WeatherResponse 객체 (forecast_items 포함)

        Raises:
            HTTPException: API 호출 실패시
        """
        # 실황과 예보를 병렬로 조회
        ncst_task = self.get_ultra_short_term_ncst(
            nx=nx,
            ny=ny,
            base_date=base_date,
            base_time=base_time,
            num_of_rows=num_of_rows,
            page_no=page_no
        )
        fcst_task = self.get_ultra_short_term_fcst(
            nx=nx,
            ny=ny,
            base_date=base_date,
            base_time=base_time,
            num_of_rows=num_of_rows,
            page_no=page_no
        )

        # 병렬 실행
        ncst_response, fcst_items = await asyncio.gather(ncst_task, fcst_task)

        # 실황 응답에 예보 데이터 추가
        ncst_response.forecast_items = fcst_items

        return ncst_response

    async def get_short_term_fcst(
        self,
        nx: int,
        ny: int,
        base_date: Optional[str] = None,
        base_time: Optional[str] = None,
        num_of_rows: int = 1000,
        page_no: int = 1
    ) -> list[ForecastItem]:
        """
        단기예보조회 (3일 예보)

        Args:
            nx: 예보지점 X 좌표
            ny: 예보지점 Y 좌표
            base_date: 발표일자 (YYYYMMDD), 미지정시 오늘 날짜
            base_time: 발표시각 (0200, 0500, 0800, 1100, 1400, 1700, 2000, 2300 중 하나)
            num_of_rows: 한 페이지 결과 수
            page_no: 페이지 번호

        Returns:
            ForecastItem 리스트

        Raises:
            HTTPException: API 호출 실패시
        """
        # 기본값 설정
        if base_date is None:
            base_date = datetime.now().strftime("%Y%m%d")

        if base_time is None:
            # 단기예보는 하루 8회 발표 (02:00, 05:00, 08:00, 11:00, 14:00, 17:00, 20:00, 23:00)
            current_time = datetime.now()
            hour = current_time.hour

            # 가장 최근 발표 시각 계산
            if hour < 2:
                base_time = "2300"
            elif hour < 5:
                base_time = "0200"
            elif hour < 8:
                base_time = "0500"
            elif hour < 11:
                base_time = "0800"
            elif hour < 14:
                base_time = "1100"
            elif hour < 17:
                base_time = "1400"
            elif hour < 20:
                base_time = "1700"
            elif hour < 23:
                base_time = "2000"
            else:
                base_time = "2300"

        params = {
            "serviceKey": self.settings.weather_api_key,
            "pageNo": page_no,
            "numOfRows": num_of_rows,
            "dataType": "JSON",
            "base_date": base_date,
            "base_time": base_time,
            "nx": nx,
            "ny": ny
        }

        try:
            logger.info(f"단기예보 데이터 조회: nx={nx}, ny={ny}, date={base_date}, time={base_time}")
            data = await self.client.get("getVilageFcst", params=params)

            # API 응답 구조 파싱
            response_data = data.get("response", {})
            header = response_data.get("header", {})
            body = response_data.get("body", {})

            result_code = header.get("resultCode", "")
            result_msg = header.get("resultMsg", "")

            # API 에러 확인
            if result_code != "00":
                logger.error(f"API 에러: {result_code} - {result_msg}")
                raise HTTPException(
                    status_code=502,
                    detail=f"기상청 API 오류: {result_msg}"
                )

            # 데이터 파싱 및 메타데이터 추가
            items_data = body.get("items", {}).get("item", [])
            forecast_items = []
            for item_data in items_data:
                category = item_data.get("category")
                fcstValue = item_data.get("fcstValue")
                metadata = CATEGORY_METADATA.get(category, {})

                # 코드값 설명 조회
                value_description = None
                if category in CODE_VALUE_MAPPINGS:
                    value_description = CODE_VALUE_MAPPINGS[category].get(fcstValue)

                item = ForecastItem(
                    **item_data,
                    categoryName=metadata.get("name"),
                    unit=metadata.get("unit"),
                    valueDescription=value_description
                )
                forecast_items.append(item)

            return forecast_items

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"단기예보 데이터 조회 실패: {e}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"단기예보 데이터 조회 중 오류가 발생했습니다: {str(e)}"
            )


# 서비스 인스턴스 생성
weather_service = WeatherService()