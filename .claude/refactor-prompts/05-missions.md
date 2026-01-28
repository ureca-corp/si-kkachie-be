# Missions 모듈 Vertical Slice 리팩토링

## 목표
Layer-based 구조를 Vertical Slice 구조로 변환하여 기능별 응집도를 높인다.

## 현재 구조
```
src/modules/missions/
├── __init__.py
├── controller.py      # 5개 엔드포인트
├── service.py         # 비즈니스 로직
├── entities.py        # DTO들
├── models.py          # Mission, MissionStep, MissionProgress (SQLModel)
└── repository.py      # DB 접근

tests/modules/missions/
├── __init__.py
├── conftest.py
└── test_controller.py
```

## 목표 구조
```
src/modules/missions/
├── __init__.py           # router 조합
├── list.py               # GET /missions
├── detail.py             # GET /missions/{id}
├── start.py              # POST /missions/{id}/start
├── progress.py           # PATCH /missions/{id}/progress
├── end.py                # POST /missions/{id}/end
├── _models.py            # Mission, MissionStep, MissionProgress - 공유
└── _repository.py        # DB 접근 - 공유

tests/modules/missions/
├── __init__.py
├── conftest.py
├── test_list.py
├── test_detail.py
├── test_start.py
├── test_progress.py
└── test_end.py
```

## 엔드포인트별 작업

### list.py
- **Endpoint**: GET /missions
- **Response DTO**: MissionListItemResponse, UserProgressResponse
- **Service**: get_missions_with_progress()
- **Dependencies**: _repository.get_all_with_progress

### detail.py
- **Endpoint**: GET /missions/{mission_id}
- **Response DTO**: MissionDetailResponse, MissionStepResponse
- **Service**: get_mission_detail()
- **Dependencies**:
  - _repository.get_by_id_with_steps
  - _repository.get_progress_by_mission

### start.py
- **Endpoint**: POST /missions/{mission_id}/start
- **Response DTO**: MissionStartResponse
- **Service**: start_mission()
- **Dependencies**:
  - _repository.get_by_id
  - _repository.get_active_progress
  - _repository.create_progress

### progress.py
- **Endpoint**: PATCH /missions/{mission_id}/progress
- **Request DTO**: MissionProgressUpdateRequest
- **Response DTO**: MissionProgressResponse
- **Service**: update_progress()
- **Dependencies**:
  - _repository.get_progress_by_id
  - _repository.update_step_completion

### end.py
- **Endpoint**: POST /missions/{mission_id}/end
- **Request DTO**: MissionEndRequest
- **Response DTO**: MissionEndResponse
- **Service**: end_mission()
- **Dependencies**:
  - _repository.get_progress_by_id
  - _repository.update_progress_status

## 공유 파일

### _models.py
```python
class Mission(SQLModel, table=True): ...
class MissionStep(SQLModel, table=True): ...
class MissionProgress(SQLModel, table=True): ...
```

### _repository.py
```python
def get_all_with_progress(session, profile_id): ...
def get_by_id(session, mission_id): ...
def get_by_id_with_steps(session, mission_id): ...
def get_progress_by_mission(session, mission_id, profile_id): ...
def get_active_progress(session, profile_id): ...
def create_progress(session, mission_id, profile_id): ...
def update_step_completion(session, progress_id, step_id): ...
def update_progress_status(session, progress_id, status, result): ...
```

## 테스트 수정
- `TestListMissions` → `test_list.py`
- `TestMissionDetail` → `test_detail.py`
- `TestStartMission` → `test_start.py`
- `TestUpdateProgress` → `test_progress.py`
- `TestEndMission` → `test_end.py`

## 검증
```bash
export $(cat .env.test | xargs) && uv run pytest tests/modules/missions/ -v
uv run ty check src/modules/missions/
uv run ruff check src/modules/missions/
```

## 완료 조건
- [ ] 모든 테스트 통과
- [ ] 타입 체크 통과
- [ ] 스타일 체크 통과
- [ ] API 동작 동일
