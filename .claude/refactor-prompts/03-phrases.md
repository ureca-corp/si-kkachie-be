# Phrases 모듈 Vertical Slice 리팩토링

## 목표
Layer-based 구조를 Vertical Slice 구조로 변환하여 기능별 응집도를 높인다.

## 현재 구조
```
src/modules/phrases/
├── __init__.py
├── controller.py      # 2개 엔드포인트
├── service.py         # 비즈니스 로직
├── entities.py        # DTO들
├── models.py          # Phrase, PhraseUsage (SQLModel)
└── repository.py      # DB 접근

tests/modules/phrases/
├── __init__.py
├── conftest.py
└── test_controller.py
```

## 목표 구조
```
src/modules/phrases/
├── __init__.py           # router 조합
├── list.py               # GET /phrases
├── use.py                # POST /phrases/{id}/use
├── _models.py            # Phrase, PhraseUsage - 공유
└── _repository.py        # DB 접근 - 공유

tests/modules/phrases/
├── __init__.py
├── conftest.py
├── test_list.py
└── test_use.py
```

## 엔드포인트별 작업

### list.py
- **Endpoint**: GET /phrases
- **Query Params**: category, mission_step_id
- **Response DTO**: PhraseResponse
- **Service**: get_phrases()
- **Dependencies**: _repository.get_phrases_by_filter

### use.py
- **Endpoint**: POST /phrases/{phrase_id}/use
- **Response DTO**: PhraseUseResponse
- **Service**: record_phrase_usage()
- **Dependencies**:
  - _repository.get_by_id
  - _repository.create_usage
  - _repository.increment_usage_count

## 공유 파일

### _models.py
```python
class Phrase(SQLModel, table=True): ...
class PhraseUsage(SQLModel, table=True): ...
```

### _repository.py
```python
def get_phrases_by_filter(session, category, mission_step_id): ...
def get_by_id(session, phrase_id): ...
def create_usage(session, phrase_id, profile_id): ...
def increment_usage_count(session, phrase_id): ...
```

## 테스트 수정
- `TestListPhrases` → `test_list.py`
- `TestUsePhrase` → `test_use.py`

## 검증
```bash
export $(cat .env.test | xargs) && uv run pytest tests/modules/phrases/ -v
uv run ty check src/modules/phrases/
uv run ruff check src/modules/phrases/
```

## 완료 조건
- [ ] 모든 테스트 통과
- [ ] 타입 체크 통과
- [ ] 스타일 체크 통과
- [ ] API 동작 동일
