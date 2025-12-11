"""
날씨 API 라우터
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from app.models.weather import WeatherResponse, WeatherSummary, ErrorResponse
from app.services.weather_service import weather_service

router = APIRouter(
    prefix="/weather",
    tags=["weather"],
    responses={
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
        502: {"model": ErrorResponse, "description": "Bad Gateway - External API Error"}
    }
)


@router.get(
    "/current",
    response_model=WeatherResponse,
    summary="초단기실황 조회",
    description="기상청 초단기실황 데이터를 조회합니다. 격자 좌표(nx, ny)를 입력하여 해당 지역의 현재 날씨를 확인할 수 있습니다. include_forecast=true로 예보 데이터도 함께 조회할 수 있습니다."
)
async def get_current_weather(
    nx: int = Query(..., description="예보지점 X 좌표 (1-149)", ge=1, le=149),
    ny: int = Query(..., description="예보지점 Y 좌표 (1-253)", ge=1, le=253),
    base_date: Optional[str] = Query(None, description="발표일자 (YYYYMMDD 형식)", regex=r"^\d{8}$"),
    base_time: Optional[str] = Query(None, description="발표시각 (HHMM 형식)", regex=r"^\d{4}$"),
    num_of_rows: int = Query(1000, description="한 페이지 결과 수", ge=1, le=1000),
    page_no: int = Query(1, description="페이지 번호", ge=1),
    include_forecast: bool = Query(False, description="초단기예보 포함 여부")
):
    """
    초단기실황 날씨 데이터 조회

    **격자 좌표 안내:**
    - 서울 시청: nx=60, ny=127
    - 부산 시청: nx=98, ny=76
    - 제주시: nx=52, ny=38

    격자 좌표는 [기상청 격자 변환](https://www.weather.go.kr/w/index.do) 페이지에서 확인할 수 있습니다.

    **예보 포함:**
    - include_forecast=true 설정 시 초단기실황과 초단기예보를 함께 조회합니다.
    - 예보 데이터는 response의 forecast_items 필드에 포함됩니다.
    """
    try:
        if include_forecast:
            # 실황 + 예보 통합 조회
            result = await weather_service.get_combined_weather(
                nx=nx,
                ny=ny,
                base_date=base_date,
                base_time=base_time,
                num_of_rows=num_of_rows,
                page_no=page_no
            )
        else:
            # 실황만 조회
            result = await weather_service.get_ultra_short_term_ncst(
                nx=nx,
                ny=ny,
                base_date=base_date,
                base_time=base_time,
                num_of_rows=num_of_rows,
                page_no=page_no
            )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/forecast",
    response_model=list,
    summary="단기예보 조회",
    description="기상청 단기예보 데이터를 조회합니다. 발표시각 기준 +3일(72시간) 예보를 제공합니다."
)
async def get_forecast(
    nx: int = Query(..., description="예보지점 X 좌표 (1-149)", ge=1, le=149),
    ny: int = Query(..., description="예보지점 Y 좌표 (1-253)", ge=1, le=253),
    base_date: Optional[str] = Query(None, description="발표일자 (YYYYMMDD 형식)", regex=r"^\d{8}$"),
    base_time: Optional[str] = Query(None, description="발표시각 (0200, 0500, 0800, 1100, 1400, 1700, 2000, 2300)", regex=r"^(0200|0500|0800|1100|1400|1700|2000|2300)$"),
    num_of_rows: int = Query(1000, description="한 페이지 결과 수", ge=1, le=1000),
    page_no: int = Query(1, description="페이지 번호", ge=1)
):
    """
    단기예보 조회 (3일 예보)

    **격자 좌표 안내:**
    - 서울 시청: nx=60, ny=127
    - 부산 시청: nx=98, ny=76
    - 제주시: nx=52, ny=38

    격자 좌표는 [기상청 격자 변환](https://www.weather.go.kr/w/index.do) 페이지에서 확인할 수 있습니다.

    **발표시각 안내:**
    - 하루 8회 발표: 02:00, 05:00, 08:00, 11:00, 14:00, 17:00, 20:00, 23:00
    - base_time 미지정 시 가장 최근 발표 시각 자동 선택

    **예보 카테고리:**
    - TMP: 기온, SKY: 하늘상태, PTY: 강수형태
    - POP: 강수확률, PCP: 강수량, REH: 습도
    - TMN: 최저기온, TMX: 최고기온
    - VEC: 풍향, WSD: 풍속, WAV: 파고, SNO: 적설량
    """
    try:
        result = await weather_service.get_short_term_fcst(
            nx=nx,
            ny=ny,
            base_date=base_date,
            base_time=base_time,
            num_of_rows=num_of_rows,
            page_no=page_no
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/summary",
    response_model=WeatherSummary,
    summary="날씨 요약 정보",
    description="초단기실황 데이터를 요약하여 주요 날씨 정보만 제공합니다."
)
async def get_weather_summary(
    nx: int = Query(..., description="예보지점 X 좌표 (1-149)", ge=1, le=149),
    ny: int = Query(..., description="예보지점 Y 좌표 (1-253)", ge=1, le=253),
    base_date: Optional[str] = Query(None, description="발표일자 (YYYYMMDD 형식)", regex=r"^\d{8}$"),
    base_time: Optional[str] = Query(None, description="발표시각 (HHMM 형식)", regex=r"^\d{4}$")
):
    """
    날씨 요약 정보 조회

    기온, 습도, 강수량, 풍향, 풍속 등 주요 날씨 정보를 간편하게 확인할 수 있습니다.

    **격자 좌표 예시:**
    - 서울 시청: nx=60, ny=127
    - 부산 시청: nx=98, ny=76
    - 대구 시청: nx=89, ny=90
    - 인천 시청: nx=55, ny=124
    - 광주 시청: nx=58, ny=74
    - 대전 시청: nx=67, ny=100
    - 울산 시청: nx=102, ny=84
    """
    try:
        result = await weather_service.get_weather_summary(
            nx=nx,
            ny=ny,
            base_date=base_date,
            base_time=base_time
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
