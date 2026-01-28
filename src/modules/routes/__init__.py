"""routes 도메인

Vertical Slice 구조:
- search.py: POST /routes/search
- recent.py: GET /routes/recent
- detail.py: GET /routes/{route_id}
- _models.py: RouteHistory 모델
- _repository.py: DB 접근
- _utils.py: 포맷팅 유틸리티
"""

from fastapi import APIRouter

from .detail import router as detail_router
from .recent import router as recent_router
from .search import router as search_router

router = APIRouter(prefix="/routes", tags=["routes"])
router.include_router(search_router)
router.include_router(recent_router)
router.include_router(detail_router)
