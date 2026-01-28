"""phrases 도메인

Vertical Slice 구조:
- list.py: GET /phrases
- use.py: POST /phrases/{id}/use
- _models.py: 공유 모델
- _repository.py: 공유 DB 접근
"""

from fastapi import APIRouter

from .list import router as list_router
from .use import router as use_router

router = APIRouter(prefix="/phrases", tags=["phrases"])
router.include_router(list_router)
router.include_router(use_router)
