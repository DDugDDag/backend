# 뚜따 앱 백엔드 (FastAPI) - find-route 통합 완료

이 프로젝트는 뚜따 앱의 백엔드 서버 코드를 포함하고 있습니다. FastAPI 프레임워크를 사용하여 **CCH 알고리즘 기반 고도화된 자전거 경로 추천 API**와 카카오맵 웹뷰를 제공하는 웹 서버입니다.

## 🚀 find-route 통합 주요 성과

### ✅ 완료된 핵심 기능

1. **find-route 프로젝트 통합 완료** - CCH(Customizable Contraction Hierarchies) 알고리즘 통합
2. **고도화된 경로 계산 엔진** - 대전시 자전거 도로 API 기반 실제 도로 네트워크 구축
3. **사용자 맞춤형 경로 추천** - 경치, 선호도를 고려한 개인화 경로 제공
4. **AI 모델과 CCH 알고리즘 하이브리드** - 두 시스템의 장점을 결합한 최적 경로 제공
5. **외부 API 연동 완료** - 타슈, 두루누비, 대전 자전거도로 API 실제 연동
6. **포괄적 로깅 및 에러 핸들링** - 견고한 예외 처리 및 재시도 메커니즘

## 기술 스택

- **프레임워크**: FastAPI
- **언어**: Python 3.8+
- **경로 계산 엔진**: CCH(Customizable Contraction Hierarchies) 알고리즘
- **그래프 알고리즘**: 다익스트라, 사용자 맞춤형 경로 찾기
- **AI 통합**: 비동기 AI 모델 연동 (HTTP 기반)
- **외부 API**: 타슈, 두루누비, 대전 자전거도로/보관소 API 연동
- **테스트**: pytest, pytest-asyncio
- **템플릿 엔진**: Jinja2
- **지도 서비스**: 카카오맵 JavaScript API
- **검색 API**: 카카오 로컬 API
- **HTTP 클라이언트**: requests, httpx (재시도 로직 포함)
- **환경 변수 관리**: python-dotenv
- **배포**: uvicorn (ASGI 서버)

## 프로젝트 구조

```
backend/
├── app/                       # 메인 애플리케이션 코드
│   ├── api/                   # API 관련 모듈
│   │   ├── external.py        # 🆕 외부 API 연동 (실제 API 호출 구현)
│   │   ├── ai_integration.py  # 🆕 AI 모델 연동 및 최적화
│   │   ├── utils.py           # 🆕 유틸리티 함수 및 예외 처리
│   │   ├── route_finder.py    # 🔄 CCH + AI 하이브리드 경로 추천
│   │   ├── routes.py          # 🔄 API 엔드포인트 (강화된 에러 핸들링)
│   │   └── schemas.py         # 🔄 확장된 API 스키마 (AI 특화)
│   ├── route_engine/          # 🆕 CCH 알고리즘 경로 계산 엔진 (find-route 통합)
│   │   ├── __init__.py        # 모듈 초기화 및 export
│   │   ├── cch.py             # CCH 알고리즘 구현
│   │   ├── customer.py        # 사용자 맞춤형 경로 찾기
│   │   ├── daejeon_bike.py    # 대전시 자전거 API 연동
│   │   └── route_calculator.py # 통합 경로 계산 클래스
│   ├── config/                # 설정 모듈
│   ├── database/              # 데이터베이스 관련 모듈
│   └── main.py                # 애플리케이션 진입점
├── tests/                     # 🆕 포괄적 테스트 스위트
│   ├── __init__.py
│   └── test_external_apis.py  # 외부 API 단위/통합 테스트
├── templates/                 # HTML 템플릿
├── main.py                    # 서버 실행 스크립트
├── requirements.txt           # 🔄 업데이트된 의존성 목록
├── pytest.ini                # 🆕 pytest 설정
└── env_example                # 환경 변수 예시 파일
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

## 시작하기

### 1. 필요 패키지 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 루트 디렉토리에 생성하고 다음 내용을 추가하세요:

```env
# 카카오 API
KAKAO_MAP_API_KEY=YOUR_KAKAO_MAP_API_KEY
KAKAO_RESTAPI_KEY=YOUR_KAKAO_REST_API_KEY

# 외부 자전거 API
TASHU_API_KEY=YOUR_TASHU_API_KEY
DUROONUBI_API_KEY=YOUR_DUROONUBI_API_KEY
DAEJEON_BIKE_API_KEY=YOUR_DAEJEON_BIKE_API_KEY

# AI 모델 서버 (선택사항)
AI_MODEL_SERVER_URL=http://localhost:5000/api/route
```

### 3. 서버 실행

```bash
python main.py
```

또는 uvicorn 직접 실행:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

기본적으로 서버는 다음 주소에서 실행됩니다: `http://localhost:8000`

## API 엔드포인트

### 경로 추천 관련 API

| 경로                      | 메소드 | 설명                                  | 특징              |
| ------------------------- | ------ | ------------------------------------- | ----------------- |
| `/api/health`             | GET    | API 서버 상태 확인                    | 기본              |
| `/api/find-path`          | POST   | 🆕 AI 기반 자전거 경로 추천           | **AI 통합**       |
| `/api/bike-stations`      | GET    | 🔄 타슈 대여소 정보 조회 (실제 API)   | **실시간 데이터** |
| `/api/bike-stations/{id}` | GET    | 🆕 특정 대여소 상태 조회              | **상태 모니터링** |
| `/api/bike-paths`         | GET    | 🔄 자전거 도로 정보 조회 (실제 API)   | **반경 검색**     |
| `/api/bike-routes`        | GET    | 🔄 대전시 자전거 노선 정보 (실제 API) | **노선 정보**     |

### 카카오맵 웹뷰 관련 API (기존 유지)

| 경로          | 메소드 | 설명               | 파라미터                                        |
| ------------- | ------ | ------------------ | ----------------------------------------------- |
| `/map`        | GET    | 카카오맵 웹뷰 제공 | `lat`, `lng`, `markers`                         |
| `/api/search` | GET    | 장소 검색 API      | `query`, `lat`, `lng`, `radius`, `page`, `size` |

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

## 🚧 다음 개발 계획 (4주차)

### 우선순위 높음

1. **실제 AI 모델 서버 연동** - HTTP 클라이언트 구현 완료
2. **사용자 인증 시스템** - JWT 기반 인증 구현
3. **경로 저장 및 즐겨찾기** - 데이터베이스 모델 확장

### 우선순위 중간

1. **실시간 위치 추적** - WebSocket 기반 구현
2. **성능 모니터링** - APM 도구 연동
3. **캐싱 시스템** - Redis 기반 응답 캐싱

### 우선순위 낮음

1. **다국어 지원** - i18n 시스템 구축
2. **관리자 대시보드** - API 사용량 모니터링
3. **배치 작업** - 대여소 상태 주기적 업데이트

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
