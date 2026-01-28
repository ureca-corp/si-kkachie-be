"""POST /missions/{mission_id}/end - 미션 종료"""

from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import CurrentProfile
from src.core.enums import MissionResult, MissionStatus
from src.core.exceptions import ValidationError
from src.core.response import ApiResponse, Status

from . import _repository as repository

router = APIRouter()


# ─────────────────────────────────────────────────
# Request/Response DTOs
# ─────────────────────────────────────────────────


class EndMissionRequest(BaseModel):
    """미션 종료 요청"""

    result: str

    @field_validator("result")
    @classmethod
    def validate_result(cls, v: str) -> str:
        valid_results = [r.value for r in MissionResult]
        if v not in valid_results:
            msg = "잘못된 결과 값이에요"
            raise ValueError(msg)
        return v


class MissionEndResponse(BaseModel):
    """미션 종료 응답"""

    progress_id: str
    status: str
    result: str
    ended_at: datetime
    duration_minutes: int


# ─────────────────────────────────────────────────
# Service
# ─────────────────────────────────────────────────


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _ensure_utc_aware(dt: datetime | None) -> datetime | None:
    """datetime을 UTC timezone-aware로 변환"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # naive datetime -> UTC aware
        return dt.replace(tzinfo=UTC)
    return dt


def end_mission(
    session: Session,
    template_id: UUID,
    profile_id: UUID,
    request: EndMissionRequest,
) -> dict:
    """미션 종료"""
    progress = repository.get_progress_by_profile_and_template(
        session, profile_id, template_id
    )

    if not progress or progress.status != MissionStatus.IN_PROGRESS.value:
        raise ValidationError("시작된 미션이 없어요")

    ended_at = _utcnow()

    # 진행 상태 업데이트
    progress.status = MissionStatus.ENDED.value
    progress.result = request.result
    progress.ended_at = ended_at
    progress.updated_at = ended_at

    repository.update_progress(session, progress)

    # 소요 시간 계산 (SQLite에서 naive datetime으로 반환될 수 있음)
    duration_minutes = 0
    if progress.started_at:
        started_at = _ensure_utc_aware(progress.started_at)
        assert started_at is not None  # type narrowing
        duration = ended_at - started_at
        duration_minutes = int(duration.total_seconds() / 60)

    return {
        "progress_id": str(progress.id),
        "status": progress.status,
        "result": progress.result,
        "ended_at": ended_at,
        "duration_minutes": duration_minutes,
    }


# ─────────────────────────────────────────────────
# Endpoint
# ─────────────────────────────────────────────────


@router.post("/{mission_id}/end", response_model=ApiResponse[MissionEndResponse])
def end_mission_endpoint(
    mission_id: UUID,
    request: EndMissionRequest,
    profile: CurrentProfile,
    session: Session = Depends(get_session),
) -> ApiResponse[MissionEndResponse] | JSONResponse:
    """미션 종료"""
    try:
        result = end_mission(session, mission_id, profile.id, request)

        return ApiResponse(
            status=Status.SUCCESS,
            message="미션을 종료했어요",
            data=MissionEndResponse(**result),
        )
    except ValidationError:
        return JSONResponse(
            status_code=400,
            content={
                "status": Status.ERROR_MISSION_NOT_STARTED,
                "message": "시작된 미션이 없어요",
                "data": None,
            },
        )
