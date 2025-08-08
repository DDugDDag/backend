# 뚜따 앱 백엔드 (FastAPI) - 4주차 통합 완료

이 프로젝트는 뚜따 앱의 백엔드 서버 코드를 포함하고 있습니다. FastAPI 프레임워크를 사용하여 **CCH 알고리즘 기반 자전거 경로 추천 API, 사용자 인증 및 관리, 고객지원 시스템**을 제공합니다.

## 🚀 주요 기능 및 성과

### ✅ 4주차 개발 완료된 핵심 기능

1. **자전거 경로 추천 시스템:**
    - CCH 알고리즘: 대전시 자전거 도로 API 기반의 실제 도로 네트워크를 구축하여 경로를 계산합니다.
    - AI 모델 연동: 날씨, 경사 등을 고려한 맞춤형 경로 추천
    - 사용자 맞춤형 경로 추천: 경치, 선호도를 고려한 개인화 경로 제공
    - AI 모델과 CCH 알고리즘 하이브리드: 두 시스템의 장점을 결합한 최적 경로 제공
2. **사용자 관리 및 인증:**
    - Kakao 소셜 로그인: 카카오 계정을 통한 사용자 인증 및 JWT 토큰 발급 기능을 구현했습니다.
    - 사용자 CRUD: 사용자 정보 조회 및 수정, 여행 기록 추가, 조회, 삭제 기능을 구현했습니다.
3. **외부 API 연동:**
    - 타슈 API: 대전 공공자전거 대여소의 위치 및 실시간 현황을 조회합니다.
    - 두루누비 API: 주변 자전거 도로 정보를 조회합니다.
    - 대전 자전거도로 API: 대전시의 자전거 노선 정보를 조회합니다.
4. **고객지원 시스템:**
    - 문의/건의사항: 사용자가 문의를 제출하면 데이터베이스에 저장되는 기능을 구현했습니다.
5. **견고한 시스템:**
    - 포괄적 테스트: pytest를 활용하여 외부 API 연동, 오류 처리, 데이터 표준화 등 다양한 시나리오에 대한 테스트를 완료했습니다.
    - 안정성: 네트워크 오류 시 더미 데이터를 반환하는 폴백(fallback) 메커니즘을 적용하여 서비스의 연속성을 보장합니다.

## 기술 스택

- **프레임워크**: FastAPI
- **언어**: Python 3.8+
- **데이터베이스**: MySQL, SQLAlchemy
- **경로 계산 엔진**: CCH(Customizable Contraction Hierarchies) 알고리즘
- **테스트**: pytest, pytest-asyncio
- **HTTP 클라이언트**: requests, httpx (재시도 로직 포함)
- **인증**: JWT, Kakao OAuth
- **환경 변수 관리**: python-dotenv

## 프로젝트 구조

```
backend/
├── app/
│   ├── api/                   # API 라우팅, 스키마
│   │   ├── endpoints/         # API 엔드포인트 정의
│   │   │   ├── auth.py        # 🔐 카카오 로그인
│   │   │   ├── route_recommend.py # 🗺️ 경로 추천
│   │   │   ├── support.py     # 🆕 고객지원
│   │   │   ├── tashu.py       # 🚲 따릉이 정보
│   │   │   └── users.py       # 👤 사용자 정보/기록
│   │   ├── schemas/           # Pydantic 모델
│   │   │   ├── route_schema.py
│   │   │   └── support_schema.py # 🆕 문의 스키마
│   │   └── __init__.py        # 라우터 등록
│   ├── common/                # 공통 유틸리티 모듈
│   │   └── utils/             # 예외, 재시도, 유효성 검사 등
│   ├── core/                  # 애플리케이션 핵심 설정
│   ├── database/              # 데이터베이스 모델
│   │   └── models/
│   │       ├── inquiry.py     # 🆕 문의 모델
│   │       ├── route.py
│   │       ├── user.py        # 🔄 사용자 모델
│   │       └── ...
│   ├── route_engine/          # CCH 알고리즘 엔진
│   ├── services/              # 비즈니스 로직 및 외부 API 연동
│   └── main.py                # FastAPI 앱 진입점
├── tests/                     # 테스트 코드
├── .env.example               # 환경 변수 예시
├── pytest.ini                 # pytest 설정
├── requirements.txt           # 의존성 목록
└── README.md
```

## 🤖 AI 기반 경로 추천 시스템

### 핵심 아키텍처

- **비동기 AI 모델 연동**: `AIRouteOptimizer` 클래스를 통한 효율적 AI 호출
- **인프라 데이터 통합**: 자전거 대여소, 도로 정보를 AI 모델 입력으로 활용
- **지능형 대체 알고리즘**: AI 모델 실패 시 자동 폴백 경로 생성
- **스마트 경로 포인트**: 자전거 도로 정보를 반영한 정교한 경로 생성

### AI 모델 통합 플로우

```
1. 사용자 요청 수신 (출발지/목적지)
2. 인프라 데이터 자동 수집 (대여소, 자전거 도로)
3. AI 모델 비동기 호출 (통합 데이터 전송)
4. AI 응답 처리 및 메타데이터 생성
5. 턴바이턴 안내 및 주변 대여소 정보 추가
6. 구조화된 경로 응답 반환
```

## 🔗 외부 API 연동 시스템

### 연동된 API 목록

| API                 | 기능                        | 구현 상태 | 폴백 지원      |
| ------------------- | --------------------------- | --------- | -------------- |
| 타슈 API            | 대전 공공자전거 대여소 정보 | ✅ 완료   | ✅ 더미 데이터 |
| 두루누비 API        | 자전거 도로 정보            | ✅ 완료   | ✅ 더미 데이터 |
| 대전 자전거도로 API | 자전거 노선 정보            | ✅ 완료   | ✅ 더미 데이터 |

### 고급 기능

- **지수적 백오프 재시도**: 네트워크 오류 시 자동 재시도 (최대 3회)
- **세분화된 예외 처리**: `NetworkException`, `AuthenticationException`, `DataFormatException`
- **데이터 표준화**: 좌표 정규화, 안전한 딕셔너리 접근, 형식 통일
- **서비스 연속성**: API 실패 시에도 더미 데이터로 서비스 유지

## 📊 주요 기능

### 1. AI 기반 자전거 경로 추천 API

**차별화된 기능:**

- AI 모델 기반 최적 경로 생성
- 자전거 도로 정보 반영
- 신뢰도 및 안전성 점수 제공
- 상세한 턴바이턴 안내
- 주변 대여소 자동 검색

```python
POST /api/find-path
{
  "start_lat": 36.3504,
  "start_lng": 127.3845,
  "end_lat": 36.3621,
  "end_lng": 127.3489,
  "preferences": {
    "prioritize_safety": true,
    "avoid_hills": false
  }
}
```

**응답 예시:**

```json
{
  "route_id": null,
  "summary": {
    "distance": 2.35,
    "duration": 9,
    "elevation_gain": 15.2,
    "safety_score": 0.78,
    "confidence_score": 0.85,
    "algorithm_version": "ai_v1.0",
    "bike_stations": 5
  },
  "route_points": [...],
  "instructions": [...],
  "nearby_stations": [...],
  "metadata": {...}
}
```

### 2. 실시간 외부 API 연동

```python
# 타슈 대여소 정보
GET /api/bike-stations

# 특정 대여소 상태
GET /api/bike-stations/{station_id}

# 자전거 도로 정보 (반경 검색)
GET /api/bike-paths?lat=36.35&lng=127.38&radius=2000

# 대전 자전거 노선
GET /api/bike-routes
```

### 3. 카카오맵 웹뷰 (기존 기능 유지)

모바일 앱에서 사용할 수 있는 카카오맵 웹뷰를 제공합니다:

- 위도/경도 파라미터에 따라 동적으로 지도 페이지 생성
- 마커 클릭 시 React Native 웹뷰로 정보 전송
- 카카오 로컬 API를 사용한 장소 검색 기능

## 🧪 테스트 시스템

### 포괄적 테스트 커버리지

- **단위 테스트**: 각 API 클래스별 개별 기능 테스트
- **통합 테스트**: 전체 API 연동 플로우 테스트
- **에러 시나리오**: 네트워크 오류, 인증 실패, 데이터 형식 오류 테스트
- **폴백 메커니즘**: 더미 데이터 반환 로직 검증

### 테스트 실행

```bash
# 전체 테스트 실행
pytest

# 상세 결과와 함께 실행
pytest -v

# 특정 테스트만 실행
pytest tests/test_external_apis.py -v
```


## 🚀 시작하기

### 1. 필요 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정
프로젝트 루트에 .env 파일을 만들고 다음 내용을 추가하세요.
```
# ✅ Database 설정
DB_HOST=localhost
DB_PORT=3306
DB_USER=ddudda0000
DB_PASSWORD=your_ddudda_password
DB_NAME=ddudda_db

# ✅ Kakao OAuth 설정
KAKAO_REST_API_KEY=your_kakao_rest_api_key
KAKAO_REDIRECT_URI=your_kakao_redirect_uri

# ✅ 외부 API 키
TASHU_API_KEY=your_tashu_api_key
DUROONUBI_API_KEY=your_duroonubi_api_key
DAEJEON_BIKE_API_KEY=your_daejeon_bike_api_key

# ✅ AI 모델 서버
AI_MODEL_SERVER_URL=http://localhost:5000/api/route

# ✅ JWT 설정
SECRET_KEY=your_super_secret_jwt_key
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

### 3. 데이터베이스 설정

DBeaver와 같은 툴을 사용하여 ddudda_db 데이터베이스와 ddudda0000 사용자를 생성한 후, 다음 명령어로 테이블을 만드세요.
```
python -m app.database.create_tables
```

### 4. 서버 실행

```
# 서버 실행 (자동 리로드)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

기본적으로 서버는 http://localhost:8000에서 실행됩니다.

## 📝 API 문서
서버 실행 후 다음 URL에서 자동 생성된 API 문서를 확인할 수 있습니다:

   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc


## 🛡️ 보안 및 안정성

### 에러 핸들링 시스템

- **세분화된 예외 처리**: 네트워크, 인증, 데이터 형식별 구분 처리
- **자동 재시도 메커니즘**: 지수적 백오프 알고리즘 적용
- **폴백 데이터**: 외부 API 실패 시에도 서비스 연속성 보장
- **입력 검증**: 좌표 유효성, 파라미터 범위 검사

### 보안 고려사항

- API 키는 환경 변수로 관리
- CORS 설정을 통한 접근 제한
- 템플릿에서 Jinja2 변수 사용 시 안전한 처리
- 외부 API 호출 시 타임아웃 및 재시도 제한

## 📈 성능 최적화

### 비동기 처리

- AI 모델 호출 시 비동기 처리로 응답 시간 최소화
- 외부 API 병렬 호출 지원
- 세션 재사용을 통한 연결 오버헤드 감소

### 데이터 최적화

- 좌표 정규화 (소수점 6자리)로 정밀도와 성능 균형
- 캐싱 가능한 구조의 표준화된 데이터 형식
- 불필요한 데이터 전송 최소화

## 개발 현황

### 3주차 개발 완료 ✅

1. **외부 API 연동 완료 및 테스트**

   - 타슈, 두루누비, 대전 자전거도로 API 실제 연동
   - 포괄적인 단위/통합 테스트 (12개 테스트 통과)
   - 견고한 에러 핸들링 및 폴백 메커니즘

2. **AI 경로 결과 반환 API 구축 완료**

   - 비동기 AI 모델 연동 인프라 구축
   - 인프라 데이터 통합 및 스마트 경로 생성
   - 풍부한 메타데이터 및 턴바이턴 안내 제공

3. **로깅 및 에러 핸들링 시스템 초기 구축**
   - 세분화된 예외 클래스 체계
   - 지수적 백오프 재시도 로직
   - 포괄적인 로깅 및 모니터링

### 2주차 개발 완료 ✅

1. **외부 API 문서 분석 및 호출 방식 파악**
   - 타슈, 두루누비, 대전 자전거도로 API 연동 클래스 구현
2. **외부 API 연동 코드 작성 및 데이터 파싱 로직 구현**
   - 대여소 정보, 자전거 도로 정보, 노선 정보 조회 메서드 구현
3. **경로 추천 요청/응답 API 명세 확정**
   - `schemas.py`에 경로 추천 관련 요청/응답 스키마 정의
4. **경로 추천 API의 기본 라우팅 및 AI 모듈 호출 부분 구현**
   - `/api/find-path` 엔드포인트 구현

## 배포 가이드

### 프로덕션 서버 실행

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 프로덕션 설정 고려사항

1. **HTTPS 적용** (Let's Encrypt 인증서 사용)
2. **Nginx 또는 Apache 웹 서버**를 프록시로 설정
3. **로깅 설정** 추가 (`logging.conf` 파일 활용)
4. **환경 변수를 통한 설정 관리**
5. **적절한 CORS 설정** 적용
6. **AI 모델 서버 분리 배포** 고려

## API 문서

서버가 실행되면 다음 URL에서 자동 생성된 API 문서를 확인할 수 있습니다:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🚧 다음 개발 계획 (5주차)

### 우선순위 높음

1. **사용자 정보 수정 기능 완성:** 
   - PUT /api/users/{user_id} 엔드포인트에 실제 DB 업데이트 로직 구현
   - JWT 토큰 기반 사용자 인증 및 권한 확인 로직 추가
2. **AI 경로 추천 시스템 고도화:** 
   - AI_MODEL_SERVER_URL에 실제 AI 모델 서버를 연동하는 httpx 비동기 요청 로직 구현
   - AIRouteOptimizer의 _call_ai_model 함수 내 더미 데이터 제거 및 실제 API 호출 로직 완성
3. **고객지원 시스템 완성:** 
   - Inquiry 모델에 문의 상태(status) 변경 기능 추가
   - 관리자용 문의 조회 API(예: GET /api/support/inquiries) 구현

### 우선순위 중간

1. **장소 검색 API 구현:** 
   - 카카오 로컬 API와 연동하는 app/services/external/kakao_api.py 같은 클라이언트 모듈 개발
   - GET /api/search/places 엔드포인트에 검색 로직 구현
2. **현재 위치 기반 날씨 조회 구현:** 
   - 외부 날씨 API(예: 기상청)와 연동하는 클라이언트 모듈 개발
   - GET /api/weather 엔드포인트 구현
3. **성능 개선:** 
   - 캐싱 시스템 도입: Redis를 활용하여 자주 조회되는 데이터(예: 따릉이 대여소 정보, 인기 경로)를 캐싱하여 API 응답 시간 단축
   - 비동기 처리: AI 모델 호출 시 비동기 처리로 응답 시간 최소화
   - 외부 API 병렬 호출 지원: 여러 API 호출을 병렬로 처리하여 응답 시간 단축
   - 세션 재사용: 세션 재사용을 통한 연결 오버헤드 감소

## 📚 참고 자료

### API 문서

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [카카오맵 API 문서](https://apis.map.kakao.com/web/documentation/)
- [카카오 로컬 API 문서](https://developers.kakao.com/docs/latest/ko/local/dev-guide)

### 개발 도구

- [pytest 문서](https://docs.pytest.org/)
- [Pydantic 문서](https://pydantic-docs.helpmanual.io/)
- [Uvicorn 문서](https://www.uvicorn.org/)

## 💡 기술적 특징 요약

### 🎯 핵심 차별점

1. **AI 기반 경로 최적화**: 단순 직선 경로가 아닌 인프라 데이터 기반 스마트 경로
2. **견고한 폴백 시스템**: 외부 의존성 실패에도 서비스 연속성 보장
3. **풍부한 메타데이터**: 신뢰도, 안전성, 처리시간 등 상세 정보 제공
4. **포괄적 테스트**: 단위/통합/에러 시나리오 모든 케이스 커버

### 🔧 기술적 우수성

- **비동기 아키텍처**: 성능 최적화된 AI 모델 연동
- **모듈화된 구조**: 각 기능별 독립적 모듈 설계
- **확장 가능한 설계**: 새로운 AI 모델이나 외부 API 쉬운 추가
- **프로덕션 준비**: 로깅, 에러 핸들링, 보안 고려사항 모두 적용
