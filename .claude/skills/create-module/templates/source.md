# 소스 코드 템플릿 (Vertical Slice 패턴)

> create-module 스킬에서 참조하는 소스 코드 템플릿

**Vertical Slice 구조:**
```
src/modules/{domain}/
├── __init__.py           # router 조합
├── {feature1}.py         # 기능 1 (DTO + Service + Controller)
├── {feature2}.py         # 기능 2 (DTO + Service + Controller)
├── _models.py            # 공유: SQLModel 정의
├── _repository.py        # 공유: DB 접근
└── _utils.py             # 공유: 유틸리티 함수 (선택)
```

---

## _models.py (공유)

```python
"""도메인 모델"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(UTC)


class {Domain}(SQLModel, table=True):
    __tablename__ = "{domain}s"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    profile_id: UUID = Field(foreign_key="profiles.id", index=True)
    created_at: datetime = Field(default_factory=_utcnow)
```

---

## _repository.py (공유)

```python
"""도메인 Repository"""

from uuid import UUID
from sqlmodel import Session, select
from ._models import {Domain}


def create(session: Session, item: {Domain}) -> {Domain}:
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def get_by_id(session: Session, item_id: UUID) -> {Domain} | None:
    return session.get({Domain}, item_id)
```

---

## {feature}.py (기능별 파일)

> **한 파일에 DTO + Service + Controller 모두 포함**

```python
"""기능 설명

METHOD /endpoint
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import CurrentProfile
from src.core.response import ApiResponse, Status

from . import _repository
from ._models import {Domain}


# ─────────────────────────────────────────────────
# Request/Response DTO
# ─────────────────────────────────────────────────

class SomeRequest(BaseModel):
    field1: str

class SomeResponse(BaseModel):
    id: str
    field1: str


# ─────────────────────────────────────────────────
# Service (비즈니스 로직)
# ─────────────────────────────────────────────────

def do_something(session: Session, profile_id, request) -> {Domain}:
    item = {Domain}(profile_id=profile_id, **request.model_dump())
    return _repository.create(session, item)


# ─────────────────────────────────────────────────
# Controller (엔드포인트)
# ─────────────────────────────────────────────────

router = APIRouter()

@router.post("/", response_model=ApiResponse[SomeResponse])
def create_endpoint(
    request: SomeRequest,
    profile: CurrentProfile,
    session: Session = Depends(get_session),
) -> ApiResponse[SomeResponse]:
    result = do_something(session, profile.id, request)
    return ApiResponse(
        status=Status.SUCCESS,
        message="완료됐어요",
        data=SomeResponse(id=str(result.id), field1=result.field1),
    )
```

---

## __init__.py (router 조합)

```python
"""{domain} 도메인"""

from fastapi import APIRouter

from .feature1 import router as feature1_router
from .feature2 import router as feature2_router

router = APIRouter(prefix="/{domain}", tags=["{domain}"])
router.include_router(feature1_router)
router.include_router(feature2_router)
```
