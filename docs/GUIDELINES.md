# Coding Guidelines

## 코드 스타일

### 원칙

1. **가독성 최우선** - 한 라인이 길면 개행
2. **의도 파악 가능** - 지나친 축약 금지
3. **타입 안전성** - 문자열 리터럴 → StrEnum

### 개행 규칙
```python
# ❌ 한 줄에 너무 많음
result = await session.exec(select(User).where(User.email == email, User.is_active == True))

# ✅ 적절한 개행
stmt = (
    select(User)
    .where(
        User.email == email,
        User.is_active == True,
    )
)
result = await session.exec(stmt)
```

### 변수명
```python
# ❌ 지나친 축약
u = await r.get(i)
if not u: raise E()

# ✅ 의도 파악 가능
user = await repo.get_by_id(user_id)
if not user:
    raise UserNotFoundError()
```

### 함수 인자 (3개 이상이면 개행)
```python
async def create_user(
    request: CreateUserRequest,
    repo: UserR AuthBackend.FIREBASE
```

## 응답 작성

### 성공
```python
return ApiResponse(
    status=Status.SUCCESS,
    message="회원가입이 완료됐어요",
    data=UserResponse.model_validate(user),
)
```

### 실패
```python
return ApiResponse(
    status=Status.EMAIL_ALREADY_EXISTS,
    message="이미 가입된 이메일이에요",
    data=None,
)
```

## Status 코드 목록

프론트엔드에서 `status` 값으로 분기 처리 가능:

| 분류 | Status | 설명 |
|------|--------|------|
| 성공 | `SUCCESS` | 요청 성공 |
| 인증 | `USER_AUTHENTICATION_FAILED` | 인증 실패 |
| 인증 | `TOKEN_EXPIRED` | 토큰 만료 |
| 인증 | `TOKEN_INVALID` | 유효하지 않은 토큰 |
| 사용자 | `USER_NOT_FOUND` | 사용자 없음 |
| 사용자 | `EMAIL_ALREADY_EXISTS` | 이메일 중복 |
| 사용자 | `USER_INACTIVE` | 비활성 사용자 |
| 권한 | `PERMISSION_DENIED` | 권한 없음 |
| 리소스 | `RESOURCE_NOT_FOUND` | 리소스 없음 |
| 리소스 | `RESOURCE_ALREADY_EXISTS` | 리소스 중복 |
| 유효성 | `VALIDATION_FAILED` | 입력 검증 실패 |
| 서버 | `INTERNAL_ERROR` | 내부 서버 오류 |
| 서버 | `DATABASE_ERROR` | DB 오류 |
| 서버 | `EXTERNAL_SERVICE_ERROR` | 외부 서비스 오류 |

## 예외 클래스 사용법

`src/core/exceptions.py`의 Error 클래스 사용:

```python
from src.core.exceptions import NotFoundError, ConflictError, UnauthorizedError

# 리소스 없음 (404)
raise NotFoundError("주문을 찾을 수 없어요")

# 리소스 중복 (409)
raise ConflictError("이미 등록된 상품이에요")

# 인증 실패 (401)
raise UnauthorizedError("로그인이 필요해요")
```

### 예외 클래스 목록

| 클래스 | HTTP | Status | 기본 메시지 |
|--------|------|--------|------------|
| `NotFoundError` | 404 | `RESOURCE_NOT_FOUND` | 찾으시는 정보가 없어요 |
| `UnauthorizedError` | 401 | `USER_AUTHENTICATION_FAILED` | 로그인이 필요해요 |
| `ForbiddenError` | 403 | `PERMISSION_DENIED` | 이 기능을 사용할 수 없어요 |
| `ConflictError` | 409 | `RESOURCE_ALREADY_EXISTS` | 이미 등록된 정보예요 |
| `ValidationError` | 422 | `VALIDATION_FAILED` | 입력 내용을 확인해주세요 |
| `TokenExpiredError` | 401 | `TOKEN_EXPIRED` | 다시 로그인해주세요 |
| `TokenInvalidError` | 401 | `TOKEN_INVALID` | 보안 정책으로 로그아웃되었어요 |
| `DatabaseError` | 503 | `DATABASE_ERROR` | 잠시 후 다시 시도해주세요 |
| `ExternalServiceError` | 502 | `EXTERNAL_SERVICE_ERROR` | 외부 서비스 연결에 문제가 있어요 |

### 메시지 작성 원칙

비개발자(일반 사용자)가 이해할 수 있는 자연스러운 한글.

| ❌ 개발자 용어 | ✅ 사용자 친화적 |
|--------------|----------------|
| "인증되지 않은 요청입니다" | "로그인이 필요해요" |
| "토큰이 만료되었습니다" | "로그인이 만료됐어요. 다시 로그인해 주세요" |
| "유효성 검사 실패" | "입력 정보를 다시 확인해 주세요" |
| "내부 서버 오류" | "일시적인 오류가 발생했어요. 잠시 후 다시 시도해 주세요" |

## 테스트 작성 (TDD 필수)

### TDD 사이클

```
1. RED    - 실패하는 테스트 먼저 작성 (구현 전이니 당연히 실패)
2. GREEN  - 테스트 통과하는 최소 코드 작성
3. REFACTOR - 코드 품질 개선 (테스트는 계속 통과)
```

### 테스트 환경

```python
# 로컬 SQLite 사용 (실제 DB 트래픽 없음)
TEST_DATABASE_URL = "sqlite://"  # 인메모리
```

### 테스트 구조 (CSR 패턴)

```
tests/
├── conftest.py              # 공통 픽스처 (DB, Client)
├── factories/               # 테스트 데이터 팩토리
├── fixtures/                # 도메인별 픽스처
├── helpers/                 # 유틸리티 (assertions, api)
└── modules/{domain}/        # 도메인별 테스트
    ├── conftest.py          # 도메인 전용 픽스처
    ├── test_controller.py   # 엔드포인트 테스트 (통합)
    └── test_service.py      # 비즈니스 로직 테스트 (단위)
```

### 파일 구조

- 한 파일 = 한 기능 (test_create.py, test_get.py 분리)
- 도메인별가
```bash
# 무조건 uv add로만
uv add fastapi
uv add sqlmodel
uv add --dev pytest
```

## Import 순서 (ruff 자동 정렬)
```python
# 1. 표준 라이브러리
from typing import Optional

# 2. 서드파티
from fastapi import APIRouter, Depends

# 3. 로컬
from src.core.response import ApiResponse
```

## 외부 도구 스크립트 작성 규칙

### 1. 설치 후 옵션 확인 필수

```bash
# ❌ 바로 스크립트 작성
uv add --dev pydeps
# 스크립트에 --no-cycles 옵션 사용 (존재하지 않음!)

# ✅ 옵션 먼저 확인
uv add --dev pydeps
uv run pydeps --help | head -30   # 사용 가능한 옵션 확인
```

### 2. dev dependency는 항상 `uv run`

```bash
# ❌ 직접 호출 (환경에 없음)
pydeps src/
pyreverse src/

# ✅ uv run으로 실행
uv run pydeps src/
uv run pyreverse src/
```

### 3. 스크립트는 단계별 테스트

```bash
# ❌ 한 번에 완성
# 100줄 스크립트 작성 → 실행 → 실패 → 디버깅 지옥

# ✅ 단계별 검증
# Step 1 작성 → 테스트 → Step 2 작성 → 테스트 → ...
```

## 커밋 메시지
```
feat: 사용자 생성 API 추가
fix: 중복 이메일 검증 버그 수정
refactor: UserRepository 쿼리 최적화
docs: README 업데이트
test: 로그인 테스트 추가
```

## 보안 가이드라인

### 비밀정보 관리
```python
# ❌ 하드코딩 금지
SECRET_KEY = "my-secret-key"

# ✅ 환경변수 사용
from src.core.config import settings
SECRET_KEY = settings.SECRET_KEY
```

### SQL 인젝션 방지
```python
# ❌ 문자열 포매팅
query = f"SELECT * FROM users WHERE email = '{email}'"

# ✅ SQLModel 파라미터 바인딩
stmt = select(User).where(User.email == email)
```

### 입력 검증
```python
# ✅ Pydantic으로 모든 입력 검증
class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
```

### 민감정보 로깅 금지
```python
# ❌ 비밀번호 로깅
logger.info(f"Login: {email}, password: {password}")

# ✅ 민감정보 제외
logger.info(f"Login attempt: {email}")
```

## 검증 체크리스트 (verification-loop)

코드 작성 후 7단계 검증 필수:

| Level | 검증 항목 | 명령어 |
|-------|----------|--------|
| 0 | Syntax | `python -m py_compile` |
| 1 | Style | `ruff check` |
| 2 | Type | `ty check` |
| 3 | Guidelines | 이 문서 준수 확인 |
| 4 | Test | `uv run pytest` (warning 0 필수) |
| 5 | Security | 보안 체크리스트 |
| 6 | Architecture | `./scripts/verify-architecture.sh` |

**pytest 설정 (pyproject.toml):**
- `filterwarnings = ["error"]` - 모든 warning을 에러로 처리
- 라이브러리 warning만 선택적으로 ignore

**모든 Level PASS + 다이어그램 생성 후에만 커밋 가능**

### 다이어그램 생성 (필수)

```bash
# 작업 완료 시 반드시 실행
./scripts/verify-architecture.sh

# 생성 확인
ls docs/diagrams/
# - module-dependencies.svg (필수)
# - classes_project.mmd (필수)
# - packages_project.mmd (필수)
# - {domain}_erd.png (선택)
```

## 아키텍처 시각화 도구

코드 변경 후 아키텍처 건전성 검증 및 문서 자동 갱신:

### 도구 목록

| 도구 | 용도 | 출력 |
|------|------|------|
| `pydeps` | 순환참조 탐지 + 모듈 의존성 | SVG (사람용) |
| `pyreverse` | 클래스 다이어그램 | Mermaid (AI용) |
| `erdantic` | Pydantic 모델 ER | PNG (사람용) |

### 명령어

```bash
# 전체 검증 (순환참조 + 다이어그램 생성)
./scripts/verify-architecture.sh

# 개별 실행 (uv run 필수)
uv run pydeps src/ --show-cycles --no-show                      # 순환참조 체크 (출력 있으면 순환 존재)
uv run pydeps src/ --rankdir TB -o docs/diagrams/deps.svg       # 의존성 그래프 (트리 레이아웃)
uv run pyreverse src/ -o mmd -d docs/diagrams/                  # Mermaid 클래스 다이어그램
```

### 순환참조 금지 (DDD 원칙)

```
❌ 금지: modules/users → modules/orders → modules/users

✅ 허용:
   modules/users → common/auth
   modules/orders → common/auth
```

순환참조 발생 시 빌드 실패 (CI 연동)
