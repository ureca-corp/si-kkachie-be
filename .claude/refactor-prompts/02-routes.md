# Routes 모듈 Vertical Slice 리팩토링

## 목표
Layer-based 구조를 Vertical Slice 구조로 변환하여 기능별 응집도를 높인다.

## 현재 구조
```
src/modules/routes/
├── __init__.py
├── controller.py      # 2개 엔드포인트
├── service.py         # 비즈니스 로직 + Naver API 호출
├── entities.py        # DTO들
├── models.py          # RouteHistory (SQLModel)
└── repository.py      # DB 접근

tests/modules/routes/
├── __init__.py
├── conftest.py
└── test_controller.py
```

## 목표 구조
```
src/modules/routes/
├── __init__.py           # router 조합
├── search.py             # POST /routes/search
├── recent.py             # GET /routes/recent
├── _models.py            # RouteHistory (SQLModel) - 공유
├── _repository.py        # DB 접근 - 공유
└── _utils.py             # 포맷팅 유틸 (거리/시간 텍스트)

tests/modules/routes/
├── __init__.py
├── conftest.py
├── test_search.py
└── test_recent.py
```

## 엔드포인트별 작업

### search.py
- **Endpoint**: POST /routes/search
- **Request DTO**: RouteSearchRequest, PointRequest
- **Response DTO**: RouteSearchResponse, PointResponse
- **Service**: search_route()
- **Dependencies**:
  - _models.RouteHistory, make_point
  - _repository.create
  - _utils._format_distance, _format_duration
  - Naver API 호출 (search_route_from_naver)

### recent.py
- **Endpoint**: GET /routes/recent
- **Response DTO**: RouteHistoryResponse
- **Service**: get_recent_routes()
- **Dependencies**: _repository.get_by_profile_id

## 공유 파일

### _models.py
```python
# RouteHistory SQLModel
# make_point 함수
```

### _repository.py
```python
def create(session, route_history): ...
def get_by_profile_id(session, profile_id, limit): ...
```

### _utils.py
```python
def _format_distance(meters: int) -> str: ...
def _format_duration(seconds: int) -> str: ...
```

## 테스트 수정
- Mock 경로: `src.modules.routes.service.search_route_from_naver` → `src.modules.routes.search.search_route_from_naver`

## 검증
```bash
export $(cat .env.test | xargs) && uv run pytest tests/modules/routes/ -v
uv run ty check src/modules/routes/
uv run ruff check src/modules/routes/
```

## 완료 조건
- [ ] 모든 테스트 통과
- [ ] 타입 체크 통과
- [ ] 스타일 체크 통과
- [ ] API 동작 동일
