"""
좌표 API 라우터
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from app.models.coordinate import CoordinateListResponse
from app.services.coordinate_service import coordinate_service

router = APIRouter(
    prefix="/coordinates",
    tags=["coordinates"],
    responses={
        404: {"description": "Not Found"},
        500: {"description": "Internal Server Error"}
    }
)


@router.get(
    "/regions",
    response_model=CoordinateListResponse,
    summary="지역별 좌표 조회",
    description="시/도, 시/군/구, 읍/면/동으로 필터링하여 좌표(nx, ny)를 조회합니다."
)
async def get_coordinates_by_region(
    province: Optional[str] = Query(None, description="시/도 (예: 전북특별자치도)"),
    city: Optional[str] = Query(None, description="시/군/구 (예: 고창군)"),
    town: Optional[str] = Query(None, description="읍/면/동 (예: 고창읍)")
):
    """
    지역명으로 좌표 조회

    **사용 예시:**
    - `/coordinates/regions?province=전북특별자치도` - 전북 전체 조회
    - `/coordinates/regions?province=전북특별자치도&city=고창군` - 고창군 전체 조회
    - `/coordinates/regions?province=전북특별자치도&city=고창군&town=고창읍` - 고창읍만 조회

    **참고:**
    - 필터를 지정하지 않으면 전체 좌표를 조회합니다.
    - 여러 필터를 조합하여 사용할 수 있습니다.
    """
    try:
        # 최소 하나의 필터는 있어야 함 (전체 조회 방지)
        if not any([province, city, town]):
            raise HTTPException(
                status_code=400,
                detail="최소 하나의 필터(province, city, town)를 입력해주세요."
            )

        result = coordinate_service.get_coordinates_by_region(
            province=province,
            city=city,
            town=town
        )

        if result.total_count == 0:
            raise HTTPException(
                status_code=404,
                detail="조회된 좌표가 없습니다. 지역명을 확인해주세요."
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/region",
    response_model=CoordinateListResponse,
    summary="지역별 좌표 조회 (단일 결과용)",
    description="province, city, town을 모두 지정하여 특정 지역의 좌표를 조회합니다."
)
async def get_coordinate_by_full_region(
    province: str = Query(..., description="시/도 (예: 전북특별자치도)"),
    city: str = Query(..., description="시/군/구 (예: 고창군)"),
    town: str = Query(..., description="읍/면/동 (예: 고창읍)")
):
    """
    특정 지역의 좌표 조회

    **사용 예시:**
    - `/coordinates/region?province=전북특별자치도&city=고창군&town=고창읍`

    **참고:**
    - 이 엔드포인트는 세 가지 파라미터가 모두 필수입니다.
    - 정확한 지역명을 입력해야 합니다.
    """
    try:
        result = coordinate_service.get_coordinates_by_region(
            province=province,
            city=city,
            town=town
        )

        if result.total_count == 0:
            raise HTTPException(
                status_code=404,
                detail=f"'{province} {city} {town}'에 해당하는 좌표를 찾을 수 없습니다."
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
