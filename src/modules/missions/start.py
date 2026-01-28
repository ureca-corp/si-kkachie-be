"""POST /missions/{mission_id}/start - 미션 시작"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import CurrentProfile
from src.core.enums import MissionStatus
from src.core.exceptions import ConflictError, NotFoundError
from src.core.response import ApiResponse, Status

from . import _repository as repository
from ._models import MissionProgress

router = APIRouter()


# ─────────────────────────────────────────────────
# Response DTOs
# ─────────────────────────────────────────────────


class MissionStartResponse(BaseModel):
    """미션 시작 응답"""

    progress_id: str
    mission_id: str
    status: str
    current_step: int
    started_at: datetime


# ─────────────────────────────────────────────────
# Service
# ─────────────────────────────────────────────────


def _utcnow() -> datetime:
    return datetime.now(UTC)


def start_mission(
    session: Session,
    template_id: UUID,
    profile_id: UUID,
) -> MissionProgress:
    """미션 시작"""
    template = repository.get_template_by_id(session, template_id)
    if not template:
        raise NotFoundError("미션을 찾을 수 없어요")

    # 이미 진행 중인 미션 확인
    existing = repository.get_progress_by_profile_and_template(
        session, profile_id, template_id
    )
    if existing and existing.status == MissionStatus.IN_PROGRESS.value:
        raise ConflictError("이미 진행 중인 미션이에요")

    # 새 진행 상태 생성
    progress = MissionProgress(
        id=uuid4(),
        profile_id=profile_id,
        mission_template_id=template_id,
        status=MissionStatus.IN_PROGRESS.value,
        current_step=1,
        started_at=_utcnow(),
        created_at=_utcnow(),
        updated_at=_utcnow(),
    )

    return repository.create_progress(session, progress)


# ─────────────────────────────────────────────────
# Endpoint
# ─────────────────────────────────────────────────


@router.post("/{mission_id}/start", response_model=ApiResponse[MissionStartResponse])
def start_mission_endpoint(
    mission_id: UUID,
    profile: CurrentProfile,
    session: Session = Depends(get_session),
) -> ApiResponse[MissionStartResponse] | JSONResponse:
    """미션 시작"""
    try:
        progress = start_mission(session, mission_id, profile.id)

        return JSONResponse(
            status_code=201,
            content={
                "status": Status.SUCCESS,
                "message": "미션을 시작했어요",
                "data": {
                    "progress_id": str(progress.id),
                    "mission_id": str(progress.mission_template_id),
                    "status": progress.status,
                    "current_step": progress.current_step,
                    "started_at": (
                        progress.started_at.isoformat() if progress.started_at else None
                    ),
                },
            },
        )
    except NotFoundError:
        return JSONResponse(
            status_code=404,
            content={
                "status": Status.MISSION_NOT_FOUND,
                "message": "미션을 찾을 수 없어요",
                "data": None,
            },
        )
    except ConflictError:
        return JSONResponse(
            status_code=409,
            content={
                "status": Status.ERROR_MISSION_ALREADY_STARTED,
                "message": "이미 진행 중인 미션이에요",
                "data": None,
            },
        )
