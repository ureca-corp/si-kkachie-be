# Profiles 모듈 Vertical Slice 리팩토링

## 목표
Layer-based 구조를 Vertical Slice 구조로 변환하여 기능별 응집도를 높인다.

## 특이사항
이 모듈은 `/auth`와 `/users` 두 가지 prefix를 사용한다.

## 현재 구조
```
src/modules/profiles/
├── __init__.py
├── controller.py      # 5개 엔드포인트 (auth + users)
├── service.py         # 비즈니스 로직
├── entities.py        # DTO들
├── models.py          # Profile (SQLModel)
└── repository.py      # DB 접근

tests/modules/profiles/
├── __init__.py
├── conftest.py
└── test_controller.py
```

## 목표 구조
```
src/modules/profiles/
├── __init__.py               # router 조합
├── verify_token.py           # POST /auth/verify-token
├── get_me.py                 # GET /users/me
├── update_me.py              # PATCH /users/me
├── profile_image.py          # POST /users/me/profile-image
├── delete_me.py              # DELETE /users/me
├── _models.py                # Profile - 공유
├── _repository.py            # DB 접근 - 공유
└── _storage.py               # Supabase Storage 연동 - 공유

tests/modules/profiles/
├── __init__.py
├── conftest.py
├── test_verify_token.py
├── test_get_me.py
├── test_update_me.py
├── test_profile_image.py
└── test_delete_me.py
```

## __init__.py 구조 (다중 prefix)
```python
"""profiles 도메인"""

from fastapi import APIRouter

from .verify_token import router as verify_token_router
from .get_me import router as get_me_router
from .update_me import router as update_me_router
from .profile_image import router as profile_image_router
from .delete_me import router as delete_me_router

# 이 모듈은 /auth와 /users 두 가지 prefix 사용
router = APIRouter(tags=["auth", "users"])
router.include_router(verify_token_router)  # /auth/verify-token
router.include_router(get_me_router)        # /users/me
router.include_router(update_me_router)     # /users/me
router.include_router(profile_image_router) # /users/me/profile-image
router.include_router(delete_me_router)     # /users/me
```

## 엔드포인트별 작업

### verify_token.py
- **Endpoint**: POST /auth/verify-token
- **Response DTO**: ProfileResponse
- **Service**: verify_token_and_get_or_create_profile()
- **특이사항**: 인증 없이 접근, 토큰 직접 검증
- **Dependencies**:
  - src.core.deps.verify_supabase_token
  - _repository.get_by_user_id
  - _repository.create

### get_me.py
- **Endpoint**: GET /users/me
- **Response DTO**: ProfileResponse
- **Service**: 없음 (단순 조회)
- **Dependencies**: CurrentProfile dependency

### update_me.py
- **Endpoint**: PATCH /users/me
- **Request DTO**: UpdateProfileRequest
- **Response DTO**: ProfileResponse
- **Service**: update_profile()
- **Dependencies**: _repository.update

### profile_image.py
- **Endpoint**: POST /users/me/profile-image
- **Request DTO**: ProfileImageUploadRequest
- **Response DTO**: ProfileImageUploadResponse
- **Service**: create_profile_image_upload_url()
- **Dependencies**: _storage.create_presigned_url

### delete_me.py
- **Endpoint**: DELETE /users/me
- **Service**: delete_profile()
- **Dependencies**: _repository.delete

## 공유 파일

### _models.py
```python
class Profile(SQLModel, table=True): ...
```

### _repository.py
```python
def get_by_user_id(session, user_id): ...
def get_by_id(session, profile_id): ...
def create(session, profile): ...
def update(session, profile, data): ...
def delete(session, profile): ...
```

### _storage.py
```python
def create_presigned_url(profile_id, file_name, content_type): ...
def get_public_url(profile_id, file_name): ...
```

## 테스트 수정
- `TestVerifyToken` → `test_verify_token.py`
- `TestGetMe` → `test_get_me.py`
- `TestUpdateMe` → `test_update_me.py`
- `TestProfileImage` → `test_profile_image.py`
- `TestDeleteMe` → `test_delete_me.py`

## 검증
```bash
export $(cat .env.test | xargs) && uv run pytest tests/modules/profiles/ -v
uv run ty check src/modules/profiles/
uv run ruff check src/modules/profiles/
```

## 완료 조건
- [ ] 모든 테스트 통과
- [ ] 타입 체크 통과
- [ ] 스타일 체크 통과
- [ ] API 동작 동일
