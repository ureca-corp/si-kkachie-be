"""PATCH /missions/{mission_id}/progress - 단계 완료 처리"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import CurrentProfile
from src.core.enums import MissionStatus
from src.core.exceptions import NotFoundError, ValidationError
from src.core.response import ApiResponse, Status

from . import _repository as repository
from ._models import MissionStepProgress

router = APIRouter()


# ─────────────────────────────────────────────────
# Request/Response DTOs
# ─────────────────────────────────────────────────


class UpdateProgressRequest(BaseModel):
    """단계 완료 요청"""

    step_id: str
    is_completed: bool = True


class MissionProgressUpdateResponse(BaseModel):
    """단계 진행 응답"""

    progress_id: str
    current_step: int
    completed_steps: int
    total_steps: int


# ─────────────────────────────────────────────────
# Service
# ─────────────────────────────────────────────────


def _utcnow() -> datetime:
    return datetime.now(UTC)


def update_progress(
    session: Session,
    template_id: UUID,
    profile_id: UUID,
    request: UpdateProgressRequest,
) -> dict:
    """단계 완료 처리"""
    progress = repository.get_progress_by_profile_and_template(
        session, profile_id, template_id
    )

    if not progress or progress.status != MissionStatus.IN_PROGRESS.value:
        raise ValidationError("시작된 미션이 없어요")

    step_id = UUID(request.step_id)
    step = repository.get_step_by_id(session, step_id)
    if not step:
        raise NotFoundError("단계를 찾을 수 없어요")

    # 단계 진행 상태 업데이트
    step_progress = repository.get_step_progress(session, progress.id, step_id)
    if not step_progress:
        step_progress = MissionStepProgress(
            id=uuid4(),
            mission_progress_id=progress.id,
            mission_step_id=step_id,
            is_completed=request.is_completed,
            completed_at=_utcnow() if request.is_completed else None,
            created_at=_utcnow(),
        )
        repository.create_step_progress(session, step_progress)
    else:
        step_progress.is_completed = request.is_completed
        step_progress.completed_at = _utcnow() if request.is_completed else None
        repository.update_step_progress(session, step_progress)

    # current_step 업데이트
    if request.is_completed:
        progress.current_step = step.step_order + 1
        progress.updated_at = _utcnow()
        repository.update_progress(session, progress)

    # 완료된 단계 수 조회
    completed_count = repository.get_completed_steps_count(session, progress.id)
    steps = repository.get_steps_by_template_id(session, template_id)

    return {
        "progress_id": str(progress.id),
        "current_step": progress.current_step,
        "completed_steps": completed_count,
        "total_steps": len(steps),
    }


# ─────────────────────────────────────────────────
# Endpoint
# ─────────────────────────────────────────────────


@router.patch(
    "/{mission_id}/progress",
    response_model=ApiResponse[MissionProgressUpdateResponse],
)
def update_progress_endpoint(
    mission_id: UUID,
    request: UpdateProgressRequest,
    profile: CurrentProfile,
    session: Session = Depends(get_session),
) -> ApiResponse[MissionProgressUpdateResponse] | JSONResponse:
    """단계 완료 처리"""
    try:
        result = update_progress(session, mission_id, profile.id, request)

        return ApiResponse(
            status=Status.SUCCESS,
            message="단계를 완료했어요",
            data=MissionProgressUpdateResponse(**result),
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
