"""profiles 도메인

Vertical Slice Architecture:
- verify_token: POST /auth/verify-token
- get_me: GET /users/me
- update_me: PATCH /users/me
- profile_image: POST /users/me/profile-image
- delete_me: DELETE /users/me
"""

from fastapi import APIRouter

# Profile 모델을 먼저 export (다른 모듈에서 사용)
# 순환 import 방지를 위해 라우터보다 먼저 import
from ._models import Profile  # noqa: F401
from .delete_me import router as delete_me_router
from .get_me import router as get_me_router
from .profile_image import router as profile_image_router
from .update_me import router as update_me_router
from .verify_token import router as verify_token_router

# 이 모듈은 /auth와 /users 두 가지 prefix 사용
router = APIRouter(tags=["auth", "users"])
router.include_router(verify_token_router)  # /auth/verify-token
router.include_router(get_me_router)  # /users/me
router.include_router(update_me_router)  # /users/me
router.include_router(profile_image_router)  # /users/me/profile-image
router.include_router(delete_me_router)  # /users/me
