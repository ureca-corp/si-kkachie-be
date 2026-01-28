"""missions 도메인

Vertical Slice Architecture:
- list.py: GET /missions
- detail.py: GET /missions/{id}
- start.py: POST /missions/{id}/start
- progress.py: PATCH /missions/{id}/progress
- end.py: POST /missions/{id}/end
"""

from fastapi import APIRouter

from .detail import router as detail_router
from .end import router as end_router
from .list import router as list_router
from .progress import router as progress_router
from .start import router as start_router

router = APIRouter(prefix="/missions", tags=["missions"])

# 각 엔드포인트 라우터 조합
router.include_router(list_router)
router.include_router(detail_router)
router.include_router(start_router)
router.include_router(progress_router)
router.include_router(end_router)
