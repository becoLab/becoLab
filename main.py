from fastapi import FastAPI
from app.routers.weather_router import router as weather_router
from app.routers.coordinate_router import router as coordinate_router
from app.database.db import init_database
from app.utils.logger import setup_logging

# 로깅 설정 초기화
setup_logging(
    log_level="INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    console_output=True,  # 콘솔 출력 여부
    file_output=True  # 파일 출력 여부
)

app = FastAPI(
    title="KMA Weather API",
    description="기상청 공공데이터 포털 날씨 조회 API",
    version="1.0.0"
)

# 데이터베이스 초기화
init_database()

app.include_router(weather_router)
app.include_router(coordinate_router)
@app.get("/")
async def root():
    return {"status": "ok", "msg": "라우터 연결 정상"}