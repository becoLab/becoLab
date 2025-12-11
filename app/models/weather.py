"""
날씨 관련 데이터 모델
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class WeatherRequest(BaseModel):
    """날씨 조회 요청 모델"""
    nx: int = Field(..., description="예보지점 X 좌표", ge=1, le=149)
    ny: int = Field(..., description="예보지점 Y 좌표", ge=1, le=253)
    base_date: Optional[str] = Field(None, description="발표일자 (YYYYMMDD)", pattern=r"^\d{8}$")
    base_time: Optional[str] = Field(None, description="발표시각 (HHMM)", pattern=r"^\d{4}$")

    class Config:
        json_schema_extra = {
            "example": {
                "nx": 55,
                "ny": 127,
                "base_date": "20231110",
                "base_time": "0600"
            }
        }


class WeatherItem(BaseModel):
    """날씨 데이터 항목"""
    category: str = Field(..., description="자료구분코드")
    categoryName: Optional[str] = Field(None, description="자료구분명")
    obsrValue: str = Field(..., description="실황값")
    valueDescription: Optional[str] = Field(None, description="값 설명 (코드값인 경우)")
    unit: Optional[str] = Field(None, description="단위")
    baseDate: str = Field(..., description="발표일자")
    baseTime: str = Field(..., description="발표시각")
    nx: int = Field(..., description="예보지점 X 좌표")
    ny: int = Field(..., description="예보지점 Y 좌표")


class ForecastItem(BaseModel):
    """예보 데이터 항목"""
    category: str = Field(..., description="자료구분코드")
    categoryName: Optional[str] = Field(None, description="자료구분명")
    fcstValue: str = Field(..., description="예보값")
    valueDescription: Optional[str] = Field(None, description="값 설명 (코드값인 경우)")
    unit: Optional[str] = Field(None, description="단위")
    fcstDate: str = Field(..., description="예보일자")
    fcstTime: str = Field(..., description="예보시각")
    baseDate: str = Field(..., description="발표일자")
    baseTime: str = Field(..., description="발표시각")
    nx: int = Field(..., description="예보지점 X 좌표")
    ny: int = Field(..., description="예보지점 Y 좌표")


class WeatherResponse(BaseModel):
    """날씨 조회 응답 모델"""
    result_code: str = Field(..., description="응답 코드")
    result_message: str = Field(..., description="응답 메시지")
    num_of_rows: int = Field(..., description="한 페이지 결과 수")
    page_no: int = Field(..., description="페이지 번호")
    total_count: int = Field(..., description="전체 결과 수")
    items: list[WeatherItem] = Field(default=[], description="날씨 데이터 목록")
    forecast_items: Optional[list[ForecastItem]] = Field(default=None, description="예보 데이터 목록 (선택적)")


class WeatherSummary(BaseModel):
    """날씨 요약 정보"""
    location: str = Field(..., description="위치 (좌표)")
    base_date: str = Field(..., description="발표일자")
    base_time: str = Field(..., description="발표시각")
    temperature: Optional[str] = Field(None, description="기온 (℃)")
    humidity: Optional[str] = Field(None, description="습도 (%)")
    precipitation: Optional[str] = Field(None, description="1시간 강수량 (mm)")
    wind_direction: Optional[str] = Field(None, description="풍향 (deg)")
    wind_speed: Optional[str] = Field(None, description="풍속 (m/s)")
    raw_data: Optional[dict] = Field(None, description="원본 데이터")

    class Config:
        json_schema_extra = {
            "example": {
                "location": "nx:55, ny:127",
                "base_date": "20231110",
                "base_time": "0600",
                "temperature": "15.0",
                "humidity": "70",
                "precipitation": "0",
                "wind_direction": "270",
                "wind_speed": "3.5"
            }
        }


class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    error: str = Field(..., description="에러 메시지")
    detail: Optional[str] = Field(None, description="에러 상세 정보")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="에러 발생 시각")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "External API Error",
                "detail": "Failed to fetch weather data from public API",
                "timestamp": "2023-11-10T10:30:00"
            }
        }
