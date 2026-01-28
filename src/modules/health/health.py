"""GET /health - Liveness 체크"""

from fastapi import APIRouter

from src.core.config import settings
from src.core.response import ApiResponse, Status

router = APIRouter()


@router.get("/", include_in_schema=True)
def health_check() -> ApiResponse[dict]:
    """Liveness 체크 - 앱 실행 여부 확인"""
    return ApiResponse(
        status=Status.SUCCESS,
        message="서비스가 정상 동작 중이에요",
        data={"version": settings.VERSION},
    )
