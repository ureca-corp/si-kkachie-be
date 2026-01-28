"""GET /health/ready - Readiness 체크"""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlmodel import Session, text

from src.core.database import get_session
from src.core.response import ApiResponse, Status

router = APIRouter()


@router.get("/ready")
def readiness_check(session: Session = Depends(get_session)) -> ApiResponse[dict]:
    """Readiness 체크 - DB 연결 확인"""
    session.exec(text("SELECT 1"))

    return ApiResponse(
        status=Status.SUCCESS,
        message="모든 서비스가 준비됐어요",
        data={
            "database": "connected",
            "timestamp": datetime.now(UTC).isoformat(),
        },
    )
