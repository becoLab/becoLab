# 날씨 조회 서비스 (Weather API Service)

기상청 공공데이터 API를 활용한 FastAPI 기반 날씨 조회 서비스입니다.

## 프로젝트 구조

```
FastAPIProject/
├── main.py                 # FastAPI 애플리케이션 진입점
├── app/
│   ├── config.py          # 설정 관리
│   ├── routers/
│   │   └── weather.py     # 날씨 API 엔드포인트
│   ├── services/
│   │   └── weather_service.py  # 날씨 API 비즈니스 로직
│   ├── models/
│   │   └── weather.py     # Pydantic 데이터 모델
│   └── utils/
│       └── api_client.py  # HTTP 클라이언트 유틸리티
├── .env                    # 환경변수 (API 키)
├── requirements.txt        # 패키지 의존성
└── README.md
```

## 설치 및 실행

### 1. 가상환경 생성 및 활성화

```bash
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정

`.env` 파일에 기상청 API 키가 설정되어 있는지 확인하세요:

```env
WEATHER_API_KEY=your_api_key_here
WEATHER_API_BASE_URL=https://apis.data.go.kr/1360000/VilageFcstInfoService_2.0
```

### 4. 애플리케이션 실행

```bash
# 방법 1: uvicorn 직접 실행
uvicorn main:app --reload

# 방법 2: Python으로 실행
python main.py
```

서버가 실행되면 http://127.0.0.1:8000 에서 접속할 수 있습니다.

## API 문서

서버 실행 후 자동 생성되는 API 문서를 확인할 수 있습니다:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

## API 엔드포인트

### 1. 루트 엔드포인트
```
GET /
```
서비스 정보 및 사용 가능한 엔드포인트 목록을 반환합니다.

### 2. 헬스 체크
```
GET /health
```
서비스 상태를 확인합니다.

### 3. 날씨 API 정보
```
GET /weather
```
날씨 API 사용 안내를 제공합니다.

### 4. 초단기실황 조회
```
GET /weather/current?nx={x좌표}&ny={y좌표}
```

**파라미터:**
- `nx` (필수): 예보지점 X 좌표 (1-149)
- `ny` (필수): 예보지점 Y 좌표 (1-253)
- `base_date` (선택): 발표일자 (YYYYMMDD)
- `base_time` (선택): 발표시각 (HHMM)
- `num_of_rows` (선택): 결과 수 (기본값: 1000)
- `page_no` (선택): 페이지 번호 (기본값: 1)

**예시:**
```bash
curl "http://127.0.0.1:8000/weather/current?nx=60&ny=127"
```

### 5. 날씨 요약 정보
```
GET /weather/summary?nx={x좌표}&ny={y좌표}
```

**파라미터:**
- `nx` (필수): 예보지점 X 좌표 (1-149)
- `ny` (필수): 예보지점 Y 좌표 (1-253)
- `base_date` (선택): 발표일자 (YYYYMMDD)
- `base_time` (선택): 발표시각 (HHMM)

**예시:**
```bash
curl "http://127.0.0.1:8000/weather/summary?nx=60&ny=127"
```

**응답 예시:**
```json
{
  "location": "nx:60, ny:127",
  "base_date": "20231110",
  "base_time": "1000",
  "temperature": "15.0",
  "humidity": "70",
  "precipitation": "0",
  "wind_direction": "270",
  "wind_speed": "3.5",
  "raw_data": {...}
}
```

## 주요 도시 격자 좌표

| 도시 | X (nx) | Y (ny) |
|------|--------|--------|
| 서울 시청 | 60 | 127 |
| 부산 시청 | 98 | 76 |
| 대구 시청 | 89 | 90 |
| 인천 시청 | 55 | 124 |
| 광주 시청 | 58 | 74 |
| 대전 시청 | 67 | 100 |
| 울산 시청 | 102 | 84 |
| 제주시 | 52 | 38 |

더 많은 좌표는 [기상청 홈페이지](https://www.weather.go.kr)에서 확인할 수 있습니다.

## 기술 스택

- **FastAPI**: 최신 Python 웹 프레임워크
- **Uvicorn**: ASGI 서버
- **httpx**: 비동기 HTTP 클라이언트
- **Pydantic**: 데이터 검증 및 설정 관리
- **Python-dotenv**: 환경변수 관리

## 아키텍처

### 계층 구조

1. **Router 계층** (`app/routers/`): HTTP 요청/응답 처리
2. **Service 계층** (`app/services/`): 비즈니스 로직 및 외부 API 호출
3. **Model 계층** (`app/models/`): 데이터 검증 및 스키마 정의
4. **Utils 계층** (`app/utils/`): 공통 유틸리티 (HTTP 클라이언트 등)

### 주요 기능

- **비동기 처리**: 효율적인 API 호출을 위한 async/await 사용
- **에러 핸들링**: 체계적인 예외 처리 및 HTTP 상태 코드 관리
- **설정 관리**: 환경변수 기반 설정 (`.env`)
- **자동 문서화**: Swagger UI 및 ReDoc 자동 생성
- **CORS 지원**: 크로스 오리진 리소스 공유 활성화
- **로깅**: 애플리케이션 로그 기록

## 개발 가이드

### 새로운 엔드포인트 추가

1. `app/models/` 에 데이터 모델 정의
2. `app/services/` 에 비즈니스 로직 구현
3. `app/routers/` 에 라우터 추가
4. `main.py` 에 라우터 등록

### 환경변수 추가

`app/config.py`의 `Settings` 클래스에 새 필드를 추가하고 `.env` 파일에 값을 설정하세요.

## 공공데이터 API

이 서비스는 기상청의 공공데이터 API를 사용합니다:
- **API**: 동네예보 조회서비스 - 초단기실황조회
- **제공기관**: 기상청
- **활용신청**: [공공데이터포털](https://www.data.go.kr/)

## 라이선스

이 프로젝트는 학습 및 개발 목적으로 만들어졌습니다.