"""
SQLite 데이터베이스 연결 관리
"""
import sqlite3
from pathlib import Path
from contextlib import contextmanager


# 데이터베이스 파일 경로
DB_DIR = Path(__file__).parent.parent.parent / "data"
DB_PATH = DB_DIR / "coordinates.db"


def init_database():
    """데이터베이스 초기화 및 테이블 생성"""
    # data 디렉토리 생성
    DB_DIR.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 테이블 생성
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS coordinates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nx INTEGER NOT NULL,
            ny INTEGER NOT NULL,
            province TEXT,
            city TEXT,
            town TEXT,
            UNIQUE(nx, ny)
        )
    """)

    # 인덱스 생성
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_nx_ny ON coordinates(nx, ny)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_region ON coordinates(province, city, town)
    """)

    conn.commit()
    conn.close()


@contextmanager
def get_db_connection():
    """데이터베이스 연결 컨텍스트 매니저"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 딕셔너리처럼 접근 가능
    try:
        yield conn
    finally:
        conn.close()


def insert_sample_data():
    """샘플 데이터 삽입 (테스트용)"""
    sample_data = [
        (60, 127, "서울특별시", "중구", "명동"),
        (55, 124, "인천광역시", "중구", "신포동"),
        (98, 76, "부산광역시", "중구", "중앙동"),
        (89, 90, "대구광역시", "중구", "동인동"),
        (58, 74, "광주광역시", "동구", "충장동"),
        (67, 100, "대전광역시", "중구", "은행동"),
        (102, 84, "울산광역시", "중구", "성안동"),
        (52, 38, "제주특별자치도", "제주시", "일도동"),
        (51, 67, "전북특별자치도", "전주시", "완산구"),
        (53, 66, "전북특별자치도", "고창군", "고창읍"),
    ]

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT OR IGNORE INTO coordinates (nx, ny, province, city, town)
            VALUES (?, ?, ?, ?, ?)
        """, sample_data)
        conn.commit()
        print(f"샘플 데이터 {cursor.rowcount}건 삽입 완료")


if __name__ == "__main__":
    # 직접 실행 시 데이터베이스 초기화 및 샘플 데이터 삽입
    init_database()
    insert_sample_data()
    print(f"데이터베이스 초기화 완료: {DB_PATH}")