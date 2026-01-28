# Locations 모듈 Vertical Slice 리팩토링

## 목표
Layer-based 구조를 Vertical Slice 구조로 변환하여 기능별 응집도를 높인다.

## 현재 구조
```
src/modules/locations/
├── __init__.py
├── controller.py      # 2개 엔드포인트
├── service.py         # 2개 함수
├── entities.py        # 2개 DTO
├── parsers.py         # 파싱 로직
└── utils.py           # 거리 계산

tests/modules/locations/
├── __init__.py
├── conftest.py
└── test_controller.py
```

## 목표 구조
```
src/modules/locations/
├── __init__.py           # router 조합
├── reverse_geocode.py    # GET /reverse-geocode (DTO + Service + Endpoint)
├── search.py             # GET /search (DTO + Service + Endpoint)
├── _parsers.py           # 공유: Naver API 응답 파싱
└── _utils.py             # 공유: PostGIS 거리 계산

tests/modules/locations/
├── __init__.py
├── conftest.py
├── test_reverse_geocode.py
└── test_search.py
```

## 변환 규칙

### 1. 파일 분리 기준
- 각 엔드포인트 = 1개 파일
- 공유 로직 = `_` prefix 파일

### 2. 각 기능 파일 구조
```python
"""기능 설명

METHOD /endpoint
"""

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

### 3. __init__.py 구조
```python
"""locations 도메인"""

from fastapi import APIRouter

from .reverse_geocode import router as reverse_geocode_router
from .search import router as search_router

router = APIRouter(prefix="/locations", tags=["locations"])
router.include_router(reverse_geocode_router)
router.include_router(search_router)
```

## 엔드포인트별 작업

### reverse_geocode.py
- **Endpoint**: GET /locations/reverse-geocode
- **DTO**: ReverseGeocodeResponse
- **Service**: get_reverse_geocode()
- **Dependencies**: _parsers.parse_reverse_geocode

### search.py
- **Endpoint**: GET /locations/search
- **DTO**: PlaceSearchItem
- **Service**: search_places()
- **Dependencies**: _parsers.parse_place_item, _utils.calculate_distance

## 테스트 수정
- `test_controller.py` → `test_reverse_geocode.py` + `test_search.py`
- Mock 경로 변경: `src.modules.locations.service.xxx` → `src.modules.locations.reverse_geocode.xxx`

## 검증
```bash
# 테스트 실행
export $(cat .env.test | xargs) && uv run pytest tests/modules/locations/ -v

# 타입 체크
uv run ty check src/modules/locations/

# 스타일 체크
uv run ruff check src/modules/locations/
```

## 완료 조건
- [ ] 모든 테스트 통과
- [ ] 타입 체크 통과
- [ ] 스타일 체크 통과
- [ ] API 동작 동일 (응답 구조 변경 없음)
