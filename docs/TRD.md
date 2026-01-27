# TRD: FastAPI AI-Native Backend Template

## 기술 스택

| 분류 | 선택 | 비고 |
|------|------|------|
| 언어 | Python 3.12+ | |
| 프레임워크 | FastAPI | 비동기 |
| ORM | SQLModel | Pydantic + SQLAlchemy |
| 패키지 매니저 | uv | astral.sh |
| 린트 | ruff | astral.sh |
| 타입 체크 | ty | astral.sh |
| 테스트 | pytest + pytest-asyncio | |
| 컨테이너 | Docker (multi-stage) | |

## 아키텍처

**Layered Architecture (CSR 패턴)**

```
src/
├── core/               # 앱 내부 프레임워크
│   ├── config.py       # 환경 설정
│   ├── database/       # DB 연결
│   ├── response.py     # API 응답 포맷
│   └── exceptions.py   # 커스텀 예외
│
├── external/           # 외부 서비스 연동 (Strategy Pattern)
│   ├── auth/           # 인증 (JWT, Firebase, Supabase)
│   ├── storage/        # 스토리지 (S3, R2, Supabase)
│   ├── cache/          # 캐시 (Redis, Upstash)
│   ├── email/          # 이메일 (SES, SendGrid)
│   └── payment/        # 결제 (Toss, Stripe)
│
├── common/             # 도메인 간 공유 로직
│   └── pagination/     # 페이지네이션 공통
│
└── modules/            # 비즈니스 도메인
    └── {domain}/       # CSR 패턴
        ├── models.py       # Model
        ├── entities.py     # DTO
        ├── repository.py   # Repository
        ├── service.py      # Service
        └── controller.py   # Controller
```

## 레이어 구분

| 레이어 | 위치 | 역할 | 예시 |
|--------|------|------|------|
| `core/` | 앱 설정, 내부 규칙 | Config, Response, Exceptions | `config.py` |
| `external/` | 외부 시스템 연동 | Auth, Storage, Cache, Email, Payment | `auth/jwt_provider.py` |
| `common/` | 도메인 간 공유 로직 | Pagination | `pagination/` |
| `modules/` | 비즈니스 도메인 | Users, Orders, Products | `users/service.py` |

## CSR 패턴 (Controller-Service-Repository)

```
controller.py → service.py → repository.py → models.py
(HTTP 처리)    (비즈니스)    (데이터 접근)    (테이블)
```

| 레이어 | 파일 | 역할 | 금지 사항 |
|--------|------|------|----------|
| Controller | `controller.py` | HTTP 요청/응답 처리 | 비즈니스 로직 |
| Service | `service.py` | 비즈니스 로직, 검증 | DB 직접 접근 |
| Repository | `repository.py` | 데이터 접근 | 비즈니스 로직 |
| Model | `models.py` | 테이블 정의 | 로직 전부 |
| DTO | `entities.py` | Request/Response | 로직 전부 |

## 응답 통일

```json
{
  "status": "ENGLISH_STATUS",
  "message": "사용자 친화적 한글 메시지",
  "data": { } | null
}
```

## 네이밍 규칙

| 대상 | 규칙 | 예시 |
|------|------|------|
| 요청 클래스 | `Create*Request`, `Update*Request` | `CreateUserRequest` |
| 응답 클래스 | `*Response` | `UserResponse` |
| Status 코드 | `UPPER_SNAKE` | `USER_NOT_FOUND` |
| 파일명 | `snake_case` | `controller.py` |

## 모듈 구조 예시

```
modules/users/
├── models.py           # User 테이블
├── entities.py         # CreateUserRequest, UserResponse
├── repository.py       # create, get_by_id, get_all, update, delete
├── service.py          # register_user, get_user, list_users
└── controller.py       # POST, GET, PUT, DELETE 엔드포인트
```

## External 레이어 (Strategy Pattern)

모든 external 모듈은 인터페이스 기반 설계로 교체 가능:

```
external/{service}/
├── __init__.py          # get_{service}_provider() 팩토리 함수
├── base.py              # I{Service}Provider (ABC)
└── {impl}_provider.py   # 구현체
```

### 인증 (Auth)

```
external/auth/
├── __init__.py          # get_auth_provider()
├── base.py              # IAuthProvider
├── jwt_provider.py      # 기본 JWT 인증
├── firebase_provider.py # Firebase Auth (선택)
└── supabase_provider.py # Supabase Auth (선택)
```

### 스토리지 (Storage)

```
external/storage/
├── __init__.py          # get_storage_provider()
├── base.py              # IStorageProvider
├── s3_provider.py       # AWS S3
├── r2_provider.py       # Cloudflare R2 (S3 호환)
└── supabase_provider.py # Supabase Storage
```

### 캐시 (Cache)

```
external/cache/
├── __init__.py          # get_cache_provider()
├── base.py              # ICacheProvider
├── redis_provider.py    # 표준 Redis
└── upstash_provider.py  # Upstash Redis (서버리스)
```

### 설정 (config.py)

```python
# Auth
AUTH_BACKEND: str = "jwt"  # "jwt" | "firebase" | "supabase"

# Storage (선택)
STORAGE_BACKEND: str | None = None  # "s3" | "r2" | "supabase"

# Cache (선택)
CACHE_BACKEND: str | None = None  # "redis" | "upstash"
```

## 패키지 관리

```bash
# 무조건 uv add로만
uv add fastapi
uv add sqlmodel
uv add --dev pytest
```

## 테스트 구조

```
tests/
├── conftest.py              # 공통 (SQLite DB, Client)
├── factories/               # 테스트 데이터 팩토리
├── fixtures/                # 도메인별 픽스처
├── helpers/                 # 유틸리티 (assertions, api)
└── modules/{domain}/
    ├── test_controller.py   # 엔드포인트 테스트
    ├── test_service.py      # 비즈니스 로직 테스트
    └── test_repository.py   # 데이터 접근 테스트
```
