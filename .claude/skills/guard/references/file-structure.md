# Vertical Slice 파일 구조 규칙

## 핵심 원칙

1. **1 엔드포인트 = 1 파일** - 각 기능은 독립된 파일
2. **공유 로직 = `_` prefix** - 여러 기능이 사용하는 코드는 분리
3. **DTO + Service + Controller 통합** - 응집도 높은 구조

## 도메인 디렉토리 구조

```
src/modules/{domain}/
├── __init__.py           # router 조합 (필수)
├── {feature1}.py         # 첫 번째 엔드포인트
├── {feature2}.py         # 두 번째 엔드포인트
├── {feature3}.py         # 세 번째 엔드포인트
├── _models.py            # 공유: SQLModel (있으면)
├── _repository.py        # 공유: DB 접근 (있으면)
└── _utils.py             # 공유: 유틸리티 함수 (있으면)
```

## 기능 파일 구조

각 `{feature}.py` 파일은 다음 순서로 구성:

```python
"""기능 설명

METHOD /full/path
"""

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from src.core.deps import get_current_profile
from ._models import SomeModel  # 공유 모델 (있으면)
from ._repository import some_db_func  # 공유 repository (있으면)
from ._utils import some_util  # 공유 유틸 (있으면)

# ─────────────────────────────────────────────────
# Request/Response DTO
# ─────────────────────────────────────────────────

class SomeRequest(BaseModel):
    """요청 DTO"""
    field: str

class SomeResponse(BaseModel):
    """응답 DTO"""
    result: str

# ─────────────────────────────────────────────────
# Service (비즈니스 로직)
# ─────────────────────────────────────────────────

async def do_something(
    param: str,
    profile_id: int,
) -> SomeResponse:
    """비즈니스 로직 함수

    Args:
        param: 파라미터 설명
        profile_id: 사용자 프로필 ID

    Returns:
        처리 결과
    """
    # 비즈니스 로직 구현
    result = some_util(param)
    return SomeResponse(result=result)

# ─────────────────────────────────────────────────
# Controller (엔드포인트)
# ─────────────────────────────────────────────────

router = APIRouter()

@router.post("/path")
async def endpoint_name(
    request: SomeRequest,
    current_profile: Profile = Depends(get_current_profile),
) -> SomeResponse:
    """엔드포인트 설명

    Args:
        request: 요청 본문
        current_profile: 현재 로그인 사용자

    Returns:
        처리 결과
    """
    return await do_something(request.field, current_profile.id)
```

### 섹션 구분

3개 섹션으로 명확히 구분:

1. **DTO 섹션**: Request/Response 클래스
2. **Service 섹션**: 비즈니스 로직 함수
3. **Controller 섹션**: FastAPI 엔드포인트

각 섹션 사이는 구분선(`# ───...`)으로 분리.

## __init__.py 구조

모든 기능 router를 조합:

```python
"""{domain} 도메인"""

from fastapi import APIRouter

from .feature1 import router as feature1_router
from .feature2 import router as feature2_router
from .feature3 import router as feature3_router

router = APIRouter(prefix="/{domain}", tags=["{domain}"])
router.include_router(feature1_router)
router.include_router(feature2_router)
router.include_router(feature3_router)
```

### 다중 prefix (예외)

일부 도메인은 여러 prefix 사용 (예: profiles - /auth, /users):

```python
"""profiles 도메인"""

from fastapi import APIRouter

from .verify_token import router as verify_token_router
from .get_me import router as get_me_router
from .update_me import router as update_me_router

# prefix 없이 tags만 지정
router = APIRouter(tags=["auth", "users"])
router.include_router(verify_token_router)  # /auth/verify-token
router.include_router(get_me_router)        # /users/me
router.include_router(update_me_router)     # /users/me
```

## 공유 파일 구조

### _models.py

SQLModel 클래스만 포함:

```python
"""공유 데이터베이스 모델"""

from sqlmodel import SQLModel, Field
from datetime import datetime

class SomeModel(SQLModel, table=True):
    """테이블 설명"""
    __tablename__ = "table_name"

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    # ... 필드 정의
```

### _repository.py

DB 접근 함수만 포함:

```python
"""공유 Repository (DB 접근)"""

from sqlmodel import Session, select

from ._models import SomeModel

def get_by_id(session: Session, id: int) -> SomeModel | None:
    """ID로 조회"""
    return session.get(SomeModel, id)

def create(session: Session, data: SomeModel) -> SomeModel:
    """생성"""
    session.add(data)
    session.commit()
    session.refresh(data)
    return data
```

### _utils.py

순수 유틸리티 함수만 포함:

```python
"""공유 유틸리티 함수"""

def format_distance(meters: int) -> str:
    """거리를 사람이 읽기 쉬운 형식으로 변환

    Args:
        meters: 미터 단위 거리

    Returns:
        포맷된 문자열 (예: "1.2km", "500m")
    """
    if meters >= 1000:
        return f"{meters / 1000:.1f}km"
    return f"{meters}m"
```

### 기타 공유 파일

도메인 특화 공유 로직:

- `_parsers.py`: 외부 API 응답 파싱
- `_validators.py`: 커스텀 검증 로직
- `_{custom}.py`: 도메인별 필요한 공유 파일

## 테스트 구조

```
tests/modules/{domain}/
├── __init__.py
├── conftest.py           # 공유 fixture
├── test_{feature1}.py    # 기능별 테스트
├── test_{feature2}.py
└── test_{feature3}.py
```

### 테스트 파일 구조

```python
"""feature1 엔드포인트 테스트"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

class TestFeature1:
    """Feature1 테스트"""

    def test_success(self, client: TestClient, auth_headers: dict):
        """정상 케이스"""
        response = client.post(
            "/domain/feature1",
            json={"field": "value"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["result"] == "expected"

    @patch("src.modules.domain.feature1.external_api_call")
    def test_external_api_error(
        self,
        mock_api: AsyncMock,
        client: TestClient,
        auth_headers: dict,
    ):
        """외부 API 오류 케이스"""
        mock_api.side_effect = Exception("API Error")
        response = client.post(
            "/domain/feature1",
            json={"field": "value"},
            headers=auth_headers,
        )
        assert response.status_code == 500
```

## 파일명 규칙

### 기능 파일명

엔드포인트 경로를 snake_case로 변환:

| 엔드포인트 | 파일명 |
|-----------|--------|
| GET /health | `health.py` |
| GET /health/ready | `ready.py` |
| POST /translate/text | `translate_text.py` |
| POST /translate/voice | `translate_voice.py` |
| GET /users/me | `get_me.py` |
| PATCH /users/me | `update_me.py` |
| DELETE /users/me | `delete_me.py` |

**동일 경로에 여러 메서드:**
- HTTP 메서드를 prefix로 추가
- 예: `get_me.py`, `update_me.py`, `delete_me.py`

**중첩 경로:**
- 마지막 세그먼트만 사용
- 예: `/missions/{id}/start` → `start.py`

### 테스트 파일명

기능 파일명에 `test_` prefix:

| 기능 파일 | 테스트 파일 |
|----------|-----------|
| `health.py` | `test_health.py` |
| `translate_text.py` | `test_translate_text.py` |
| `get_me.py` | `test_get_me.py` |

## Import 규칙

### 절대 import 사용

```python
# ✅ 좋은 예
from src.core.deps import get_current_profile
from src.core.database import get_session

# ❌ 나쁜 예
from core.deps import get_current_profile
from ...core.database import get_session
```

### 공유 파일 상대 import

같은 도메인 내 공유 파일은 상대 import:

```python
# ✅ 좋은 예
from ._models import SomeModel
from ._repository import get_by_id
from ._utils import format_distance

# ❌ 나쁜 예
from src.modules.domain._models import SomeModel
```

### Import 순서

1. 표준 라이브러리
2. 서드파티 라이브러리 (FastAPI, Pydantic 등)
3. 프로젝트 내부 (src.core, src.external 등)
4. 도메인 내부 공유 파일 (._models 등)

```python
# 표준 라이브러리
from datetime import datetime
from typing import List

# 서드파티
from fastapi import APIRouter, Depends
from pydantic import BaseModel

# 프로젝트
from src.core.deps import get_current_profile
from src.external.maps import search_places

# 도메인 공유
from ._models import Location
from ._repository import create
```
