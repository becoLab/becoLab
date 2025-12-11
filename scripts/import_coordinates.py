"""
Excel 파일에서 좌표 데이터를 읽어서 데이터베이스에 저장하는 스크립트
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from app.database.db import get_db_connection, init_database

# Excel 파일 경로
EXCEL_PATH = project_root / "data" / "raw" / "기상청41_단기예보 조회서비스_오픈API활용가이드_격자_위경도.xlsx"


def preview_excel():
    """Excel 파일 구조 미리보기"""
    print(f"Excel 파일 경로: {EXCEL_PATH}")
    print(f"파일 존재 여부: {EXCEL_PATH.exists()}\n")

    if not EXCEL_PATH.exists():
        print("파일을 찾을 수 없습니다!")
        return None

    # Excel 파일 읽기
    df = pd.read_excel(EXCEL_PATH)

    print("=" * 80)
    print("Excel 파일 정보:")
    print("=" * 80)
    print(f"총 행 수: {len(df)}")
    print(f"총 열 수: {len(df.columns)}")
    print(f"\n컬럼명:\n{list(df.columns)}")
    print(f"\n첫 5행 미리보기:")
    print(df.head())
    print(f"\n데이터 타입:")
    print(df.dtypes)
    print("=" * 80)

    return df


def import_data():
    """Excel 데이터를 데이터베이스에 저장"""
    # 데이터베이스 초기화
    init_database()

    # Excel 파일 읽기
    print("Excel 파일 읽는 중...")
    df = pd.read_excel(EXCEL_PATH)

    # 컬럼명 확인 (실제 컬럼명에 맞게 수정 필요)
    print(f"\n실제 컬럼명: {list(df.columns)}\n")

    # 데이터 삽입
    with get_db_connection() as conn:
        cursor = conn.cursor()

        inserted_count = 0
        skipped_count = 0

        print("데이터 삽입 시작...")

        for idx, row in df.iterrows():
            try:
                # Excel 컬럼명에 맞게 데이터 추출
                nx = int(row['격자 X'])
                ny = int(row['격자 Y'])

                # 지역 정보 추출
                province = str(row['1단계']) if pd.notna(row['1단계']) else None
                city = str(row['2단계']) if pd.notna(row['2단계']) else None
                town = str(row['3단계']) if pd.notna(row['3단계']) else None

                # 데이터베이스에 삽입
                cursor.execute("""
                    INSERT OR IGNORE INTO coordinates (nx, ny, province, city, town)
                    VALUES (?, ?, ?, ?, ?)
                """, (nx, ny, province, city, town))

                if cursor.rowcount > 0:
                    inserted_count += 1
                else:
                    skipped_count += 1

                # 진행상황 출력 (100건마다)
                if (idx + 1) % 100 == 0:
                    print(f"처리 중... {idx + 1}/{len(df)} 행 (삽입: {inserted_count}, 중복: {skipped_count})")

            except Exception as e:
                print(f"행 {idx + 1} 처리 중 오류: {e}")
                print(f"문제가 된 데이터: {row.to_dict()}")
                continue

        conn.commit()

        print("\n" + "=" * 80)
        print(f"데이터 가져오기 완료!")
        print(f"총 처리: {len(df)} 행")
        print(f"삽입 성공: {inserted_count} 건")
        print(f"중복 스킵: {skipped_count} 건")
        print("=" * 80)

        # 저장된 데이터 확인
        cursor.execute("SELECT COUNT(*) FROM coordinates")
        total = cursor.fetchone()[0]
        print(f"\n데이터베이스 총 레코드 수: {total} 건")


if __name__ == "__main__":
    print("1. Excel 파일 미리보기")
    print("2. 데이터 가져오기")
    print()

    choice = input("선택 (1 또는 2, Enter=2): ").strip() or "2"

    if choice == "1":
        preview_excel()
    elif choice == "2":
        import_data()
    else:
        print("잘못된 선택입니다.")