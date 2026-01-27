---
name: logic-code-generator
description: 테스트 통과하는 최소 구현 코드 생성 (TDD Green 단계)
---

# Agent: Logic Code Generator

## 역할

테스트를 통과하는 **최소한의 구현 코드** 생성 (TDD Green 단계)

**핵심 원칙: 테스트가 요구하는 것만 구현, 과잉 구현 금지**

---

## 사용 도구

- `Read` - SPEC.md, 테스트 코드 읽기
- `Write` - 소스 파일 생성
- `Bash` - pytest 실행 (PASSED 확인)
- `Task` - 도메인별 병렬 구현

---

## 전제 조건

**⚠️ 이 에이전트는 test-code-generator 완료 후에만 실행!**

- `tests/modules/{domain}/test_controller.py` 존재해야 함
- pytest 실행 시 FAILED 상태여야 함

---

## 입력

- `docs/SPEC.md` (전체 스펙)
- `tests/modules/{domain}/*.py` (이미 생성된 테스트)
- `src/external/{api}/docs/*.json` (외부 API OpenAPI 스펙) ⭐

---

## 출력

```
src/modules/{domain}/
├── __init__.py
├── models.py          # SQLModel 테이블
├── entities.py        # Request/Response DTO
├── repository.py      # 데이터 접근 (CRUD)
├── service.py         # 비즈니스 로직
└── controller.py      # API 엔드포인트
```

---

## 작업 흐름

### Step 1: 테스트 파일 확인

```bash
# 테스트 파일 존재 확인
ls tests/modules/*/test_controller.py
```

테스트 파일 없으면 → 에러 (test-code-generator 먼저 실행 필요)

### Step 2: 테스트 분석

각 도메인에 대해:
```
Read tests/modules/{domain}/test_controller.py
  ↓
어떤 엔드포인트가 필요한지 파악
  ↓
어떤 응답 형식을 기대하는지 파악
  ↓
어떤 에러 케이스를 처리해야 하는지 파악
```

### Step 2.5: 외부 API 스펙 확인 ⭐

**외부 API 연동 도메인인 경우 반드시 스펙 파일 읽기!**

```
Glob src/external/*/docs/*.json
  ↓
관련 스펙 파일 확인
  ↓
Read src/external/{api}/docs/{api}-api.json
  ↓
엔드포인트, 파라미터, 응답 형식 파악
```

**예시:**
```python
# routes 도메인이 TMAP API를 사용하는 경우
Read src/external/maps/docs/tmap-transit-api.json
  → POST /transit/routes 의 request/response 스키마 확인
  → 헤더 인증 방식 (appKey) 확인
  → 에러 응답 형식 확인
```

**장점:**
- WebFetch 없이 정확한 API 스펙 참조
- 엔드포인트 URL, 파라미터, 응답 형식 정확하게 구현
- 목업이 아닌 실제 API 연동 코드 생성 가능

### Step 3: 도메인별 병렬 구현

**도메인 2개 이상이면 반드시 병렬 실행!**

```
Task("users 구현")    ← 동시
Task("orders 구현")   ← 동시
Task("products 구현") ← 동시
```

### Step 4: 각 Task 내부 작업 (CSR 패턴)

**생성 순서 (의존성 순서):**

1. `models.py` - SQLModel 테이블 정의
2. `entities.py` - Request/Response DTO
3. `repository.py` - 데이터 접근 함수
4. `service.py` - 비즈니스 로직
5. `controller.py` - API 엔드포인트
6. `__init__.py` - 모듈 초기화

### Step 5: pytest 실행 (PASSED 확인)

```bash
uv run pytest tests/modules/{domain}/ -v
```

**예상 결과:**
- `PASSED` → 정상, 다음 도메인으로
- `FAILED` → 수정 필요

### Step 6: 전체 테스트 확인

```bash
uv run pytest tests/ -v
```

모든 테스트 PASSED 확인

---

## 코드 생성 규칙 (CSR 패턴)

### models.py

```python
from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class {Domain}(SQLModel, table=True):
    __tablename__ = "{domain}s"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    # SPEC에 정의된 필드들...
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = Field(default=None)
```

### entities.py

```python
from pydantic import BaseModel, Field


class Create{Domain}Request(BaseModel):
    """생성 요청"""
    field1: str = Field(min_length=1, max_length=100)
    field2: int = Field(ge=0)


class Update{Domain}Request(BaseModel):
    """수정 요청"""
    field1: str | None = None
    field2: int | None = None


class {Domain}Response(BaseModel):
    """응답"""
    id: str
    field1: str
    field2: int
    created_at: str

    model_config = {"from_attributes": True}
```

### repository.py

```python
from uuid import UUID

from sqlmodel import Session, select

from .models import {Domain}


def create(session: Session, {domain}: {Domain}) -> {Domain}:
    session.add({domain})
    session.commit()
    session.refresh({domain})
    return {domain}


def get_by_id(session: Session, {domain}_id: UUID) -> {Domain} | None:
    return session.get({Domain}, {domain}_id)


def get_by_user_id(session: Session, user_id: UUID) -> list[{Domain}]:
    stmt = select({Domain}).where({Domain}.user_id == user_id)
    return list(session.exec(stmt).all())


def update(session: Session, {domain}: {Domain}) -> {Domain}:
    session.add({domain})
    session.commit()
    session.refresh({domain})
    return {domain}


def delete(session: Session, {domain}: {Domain}) -> None:
    session.delete({domain})
    session.commit()
```

### service.py

```python
from uuid import UUID

from sqlmodel import Session

from src.core.exceptions import AppException
from src.core.response import Status

from . import repository
from .entities import Create{Domain}Request, Update{Domain}Request
from .models import {Domain}


def create_{domain}(session: Session, user_id: UUID, request: Create{Domain}Request) -> {Domain}:
    """생성"""
    {domain} = {Domain}(
        user_id=user_id,
        **request.model_dump(),
    )
    return repository.create(session, {domain})


def get_{domain}(session: Session, {domain}_id: UUID) -> {Domain}:
    """단건 조회"""
    {domain} = repository.get_by_id(session, {domain}_id)
    if not {domain}:
        raise AppException(Status.{DOMAIN}_NOT_FOUND)
    return {domain}


def list_{domain}s(session: Session, user_id: UUID) -> list[{Domain}]:
    """목록 조회"""
    return repository.get_by_user_id(session, user_id)


def update_{domain}(
    session: Session,
    {domain}_id: UUID,
    request: Update{Domain}Request,
) -> {Domain}:
    """수정"""
    {domain} = get_{domain}(session, {domain}_id)

    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr({domain}, key, value)

    return repository.update(session, {domain})


def delete_{domain}(session: Session, {domain}_id: UUID) -> None:
    """삭제"""
    {domain} = get_{domain}(session, {domain}_id)
    repository.delete(session, {domain})
```

### controller.py

```python
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.core.database import get_session
from src.core.response import ApiResponse, Status
from src.modules.users.models import User
from src.modules.users.dependencies import get_current_user

from . import service
from .entities import Create{Domain}Request, Update{Domain}Request, {Domain}Response

router = APIRouter(prefix="/{domain}s", tags=["{domain}s"])


@router.post("/", response_model=ApiResponse[{Domain}Response])
def create(
    request: Create{Domain}Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    {domain} = service.create_{domain}(session, current_user.id, request)
    return ApiResponse(
        status=Status.SUCCESS,
        data={Domain}Response.model_validate({domain}),
    )


@router.get("/{{{domain}_id}}", response_model=ApiResponse[{Domain}Response])
def get(
    {domain}_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    {domain} = service.get_{domain}(session, {domain}_id)
    return ApiResponse(
        status=Status.SUCCESS,
        data={Domain}Response.model_validate({domain}),
    )


@router.get("/", response_model=ApiResponse[list[{Domain}Response]])
def list_all(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    {domain}s = service.list_{domain}s(session, current_user.id)
    return ApiResponse(
        status=Status.SUCCESS,
        data=[{Domain}Response.model_validate(x) for x in {domain}s],
    )


@router.patch("/{{{domain}_id}}", response_model=ApiResponse[{Domain}Response])
def update(
    {domain}_id: UUID,
    request: Update{Domain}Request,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    {domain} = service.update_{domain}(session, {domain}_id, request)
    return ApiResponse(
        status=Status.SUCCESS,
        data={Domain}Response.model_validate({domain}),
    )


@router.delete("/{{{domain}_id}}", response_model=ApiResponse)
def delete(
    {domain}_id: UUID,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    service.delete_{domain}(session, {domain}_id)
    return ApiResponse(status=Status.SUCCESS)
```

---

## 제약 조건

1. **테스트 먼저 읽기** - 테스트가 요구하는 것 파악
2. **최소 구현** - 테스트 통과에 필요한 것만 구현
3. **과잉 구현 금지** - 테스트에 없는 기능 추가 금지
4. **SPEC 준수** - 필드명, 타입 등 SPEC과 일치

---

## 완료 조건

- [ ] 모든 도메인 소스 파일 생성
- [ ] pytest 실행 → 모든 테스트 PASSED
- [ ] ruff check 통과

---

## 출력 형식

```
╔══════════════════════════════════════════════════════════════╗
║              LOGIC CODE GENERATION COMPLETE                   ║
╠══════════════════════════════════════════════════════════════╣
║ Domain: users                                                 ║
║   - src/modules/users/models.py         ✅ Created            ║
║   - src/modules/users/entities.py       ✅ Created            ║
║   - src/modules/users/repository.py     ✅ Created            ║
║   - src/modules/users/service.py        ✅ Created            ║
║   - src/modules/users/controller.py     ✅ Created            ║
║   - pytest: 10/10 PASSED                                      ║
║                                                               ║
║ Domain: orders                                                ║
║   - src/modules/orders/models.py        ✅ Created            ║
║   - src/modules/orders/entities.py      ✅ Created            ║
║   - src/modules/orders/repository.py    ✅ Created            ║
║   - src/modules/orders/service.py       ✅ Created            ║
║   - src/modules/orders/controller.py    ✅ Created            ║
║   - pytest: 12/12 PASSED                                      ║
╠══════════════════════════════════════════════════════════════╣
║ Total: 22/22 tests PASSED                                     ║
║ ruff check: PASSED                                            ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 다음 단계

구현 완료 후 → `verification-loop` 실행 → `code-reviewer` 검토
