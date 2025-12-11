"""
좌표 관련 데이터 모델
"""
from pydantic import BaseModel, Field
from typing import Optional


class Coordinate(BaseModel):
    """좌표 데이터 모델"""
    id: int = Field(..., description="좌표 ID")
    nx: int = Field(..., description="격자 X 좌표")
    ny: int = Field(..., description="격자 Y 좌표")
    province: Optional[str] = Field(None, description="시/도")
    city: Optional[str] = Field(None, description="시/군/구")
    town: Optional[str] = Field(None, description="읍/면/동")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "nx": 60,
                "ny": 127,
                "province": "서울특별시",
                "city": "중구",
                "town": "명동"
            }
        }


class CoordinateListResponse(BaseModel):
    """좌표 목록 응답 모델"""
    total_count: int = Field(..., description="조회된 좌표 수")
    coordinates: list[Coordinate] = Field(..., description="좌표 데이터 목록")

    class Config:
        json_schema_extra = {
            "example": {
                "total_count": 3,
                "coordinates": [
                    {
                        "id": 1,
                        "nx": 53,
                        "ny": 66,
                        "province": "전북특별자치도",
                        "city": "고창군",
                        "town": "고창읍"
                    }
                ]
            }
        }