"""
좌표 서비스 레이어
"""
from typing import Optional
from app.database.db import get_db_connection
from app.models.coordinate import Coordinate, CoordinateListResponse


class CoordinateService:
    """좌표 관련 비즈니스 로직"""

    def get_coordinates_by_region(
        self,
        province: Optional[str] = None,
        city: Optional[str] = None,
        town: Optional[str] = None
    ) -> CoordinateListResponse:
        """
        지역명으로 좌표 조회

        Args:
            province: 시/도
            city: 시/군/구
            town: 읍/면/동

        Returns:
            CoordinateListResponse: 조회된 좌표 목록
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # 동적 쿼리 생성
            query = "SELECT * FROM coordinates WHERE 1=1"
            params = []

            if province:
                query += " AND province = ?"
                params.append(province)

            if city:
                query += " AND city = ?"
                params.append(city)

            if town:
                query += " AND town = ?"
                params.append(town)

            query += " ORDER BY id"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            # 결과를 Coordinate 모델로 변환
            coordinates = []
            for row in rows:
                coordinates.append(Coordinate(
                    id=row['id'],
                    nx=row['nx'],
                    ny=row['ny'],
                    province=row['province'],
                    city=row['city'],
                    town=row['town']
                ))

            return CoordinateListResponse(
                total_count=len(coordinates),
                coordinates=coordinates
            )

    def get_coordinate_by_grid(self, nx: int, ny: int) -> Optional[Coordinate]:
        """
        격자 좌표로 조회

        Args:
            nx: X 좌표
            ny: Y 좌표

        Returns:
            Coordinate: 좌표 정보 (없으면 None)
        """
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM coordinates WHERE nx = ? AND ny = ?",
                (nx, ny)
            )
            row = cursor.fetchone()

            if row:
                return Coordinate(
                    id=row['id'],
                    nx=row['nx'],
                    ny=row['ny'],
                    province=row['province'],
                    city=row['city'],
                    town=row['town']
                )
            return None


# 싱글톤 인스턴스
coordinate_service = CoordinateService()