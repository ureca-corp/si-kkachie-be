# Vertical Slice 리팩토링 프롬프트

## 개요

Layer-based 구조에서 Vertical Slice 구조로 전환하는 리팩토링 가이드입니다.

## 권장 순서

복잡도 순서로 진행합니다 (단순 → 복잡):

| 순서 | 파일 | 도메인 | 엔드포인트 수 | 난이도 |
|------|------|--------|---------------|--------|
| 1 | [00-health.md](./00-health.md) | health | 2 | ⭐ |
| 2 | [01-locations.md](./01-locations.md) | locations | 2 | ⭐ |
| 3 | [02-routes.md](./02-routes.md) | routes | 2 | ⭐⭐ |
| 4 | [03-phrases.md](./03-phrases.md) | phrases | 2 | ⭐⭐ |
| 5 | [04-translations.md](./04-translations.md) | translations | 4 | ⭐⭐⭐ |
| 6 | [05-missions.md](./05-missions.md) | missions | 5 | ⭐⭐⭐ |
| 7 | [06-profiles.md](./06-profiles.md) | profiles | 5 | ⭐⭐⭐ |

## 세션 실행 방법

각 도메인에 대해 새 Claude 세션을 열고:

```
{프롬프트 파일 내용 복사 붙여넣기}

위 계획대로 리팩토링을 진행해줘.
```

## 공통 규칙

### 파일 구조
```
src/modules/{domain}/
├── __init__.py           # router 조합
├── {feature1}.py         # 첫 번째 엔드포인트
├── {feature2}.py         # 두 번째 엔드포인트
├── _models.py            # 공유: SQLModel 정의
├── _repository.py        # 공유: DB 접근
└── _utils.py             # 공유: 유틸리티 함수
```

### 각 기능 파일 구조
```python
"""기능 설명

METHOD /endpoint
"""

from fastapi import APIRouter
from pydantic import BaseModel

# ─────────────────────────────────────────────────
# Request/Response DTO
# ─────────────────────────────────────────────────

class SomeRequest(BaseModel): ...
class SomeResponse(BaseModel): ...

# ─────────────────────────────────────────────────
# Service (비즈니스 로직)
# ─────────────────────────────────────────────────

async def do_something(...) -> SomeResponse: ...

# ─────────────────────────────────────────────────
# Controller (엔드포인트)
# ─────────────────────────────────────────────────

router = APIRouter()

@router.get("/endpoint")
async def endpoint(...): ...
```

### __init__.py 템플릿
```python
"""{domain} 도메인"""

from fastapi import APIRouter

from .feature1 import router as feature1_router
from .feature2 import router as feature2_router

router = APIRouter(prefix="/{domain}", tags=["{domain}"])
router.include_router(feature1_router)
router.include_router(feature2_router)
```

### 테스트 구조
```
tests/modules/{domain}/
├── __init__.py
├── conftest.py           # 공유 fixture
├── test_{feature1}.py    # 기능별 테스트
└── test_{feature2}.py
```

## 검증 명령어

```bash
# 1. 테스트 실행 (PostgreSQL 필요)
export $(cat .env.test | xargs) && uv run pytest tests/modules/{domain}/ -v

# 2. 타입 체크
uv run ty check src/modules/{domain}/

# 3. 스타일 체크
uv run ruff check src/modules/{domain}/

# 4. 전체 테스트
export $(cat .env.test | xargs) && uv run pytest tests/ -v
```

## 완료 체크리스트

각 도메인 완료 시:

- [ ] 모든 테스트 통과
- [ ] 타입 체크 통과
- [ ] 스타일 체크 통과
- [ ] API 응답 구조 동일 (Breaking change 없음)
- [ ] main.py 수정 불필요 (router import 경로 동일)

## 롤백

문제 발생 시 git으로 롤백:

```bash
git checkout -- src/modules/{domain}/
git checkout -- tests/modules/{domain}/
```
