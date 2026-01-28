"""Health 모듈 - Liveness & Readiness 체크"""

from fastapi import APIRouter

from src.modules.health.health import router as health_router
from src.modules.health.ready import router as ready_router

router = APIRouter(prefix="/health", tags=["Health"])
router.include_router(health_router)
router.include_router(ready_router)

__all__ = ["router"]
