# Translations 모듈 Vertical Slice 리팩토링

## 목표
Layer-based 구조를 Vertical Slice 구조로 변환하여 기능별 응집도를 높인다.

## 현재 구조
```
src/modules/translations/
├── __init__.py
├── controller.py      # 4개 엔드포인트
├── service.py         # 비즈니스 로직 (번역, STT, TTS)
├── entities.py        # DTO들
├── models.py          # Translation (SQLModel)
└── repository.py      # DB 접근

tests/modules/translations/
├── __init__.py
├── conftest.py
└── test_controller.py
```

## 목표 구조
```
src/modules/translations/
├── __init__.py               # router 조합
├── translate_text.py         # POST /translate/text
├── translate_voice.py        # POST /translate/voice
├── list.py                   # GET /translations
├── delete.py                 # DELETE /translations/{id}
├── _models.py                # Translation - 공유
├── _repository.py            # DB 접근 - 공유
└── _translation_service.py   # Google Cloud 번역 호출 - 공유

tests/modules/translations/
├── __init__.py
├── conftest.py
├── test_translate_text.py
├── test_translate_voice.py
├── test_list.py
└── test_delete.py
```

## 엔드포인트별 작업

### translate_text.py
- **Endpoint**: POST /translate/text
- **Request DTO**: TextTranslationRequest
- **Response DTO**: TranslationResponse
- **Service**: translate_text()
- **Dependencies**:
  - _translation_service.translate
  - _repository.create

### translate_voice.py
- **Endpoint**: POST /translate/voice
- **Request**: multipart/form-data (audio_file)
- **Response DTO**: TranslationResponse
- **Service**: translate_voice()
- **Dependencies**:
  - _translation_service.speech_to_text
  - _translation_service.translate
  - _translation_service.text_to_speech
  - _repository.create

### list.py
- **Endpoint**: GET /translations
- **Query Params**: page, limit, type, mission_progress_id
- **Response DTO**: TranslationListResponse, PaginationResponse
- **Service**: get_translations()
- **Dependencies**: _repository.get_by_profile_paginated

### delete.py
- **Endpoint**: DELETE /translations/{translation_id}
- **Service**: delete_translation()
- **Dependencies**:
  - _repository.get_by_id
  - _repository.delete

## 공유 파일

### _models.py
```python
class Translation(SQLModel, table=True): ...
```

### _repository.py
```python
def create(session, translation): ...
def get_by_id(session, translation_id): ...
def get_by_profile_paginated(session, profile_id, page, limit, type_filter): ...
def delete(session, translation): ...
```

### _translation_service.py
```python
async def translate(text: str, source_lang: str, target_lang: str) -> str: ...
async def speech_to_text(audio_data: bytes, language: str) -> str: ...
async def text_to_speech(text: str, language: str) -> bytes: ...
```

## 테스트 수정
- `TestTextTranslation` → `test_translate_text.py`
- `TestVoiceTranslation` → `test_translate_voice.py`
- `TestTranslationHistory` → `test_list.py`
- `TestDeleteTranslation` → `test_delete.py`

## 검증
```bash
export $(cat .env.test | xargs) && uv run pytest tests/modules/translations/ -v
uv run ty check src/modules/translations/
uv run ruff check src/modules/translations/
```

## 완료 조건
- [ ] 모든 테스트 통과
- [ ] 타입 체크 통과
- [ ] 스타일 체크 통과
- [ ] API 동작 동일
