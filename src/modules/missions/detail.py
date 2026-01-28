"""GET /missions/{mission_id} - 미션 상세 조회"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import CurrentProfile
from src.core.exceptions import NotFoundError
from src.core.response import ApiResponse, Status

from . import _repository as repository

router = APIRouter()


# ─────────────────────────────────────────────────
# Response DTOs
# ─────────────────────────────────────────────────


class MissionStepResponse(BaseModel):
    """미션 단계 응답"""

    id: str
    step_order: int
    title: str
    description: str
    is_completed: bool = False
    phrases: list[dict] = []


class UserProgressResponse(BaseModel):
    """사용자 진행 상태"""

    id: str | None = None
    status: str
    current_step: int
    started_at: datetime | None = None


class MissionDetailResponse(BaseModel):
    """미션 상세 응답"""

    id: str
    title: str
    description: str
    mission_type: str
    estimated_duration_min: int
    icon_url: str | None = None
    steps: list[MissionStepResponse]
    user_progress: UserProgressResponse | None = None


# ─────────────────────────────────────────────────
# Service
# ─────────────────────────────────────────────────


def get_mission_detail(
    session: Session,
    template_id: UUID,
    profile_id: UUID,
    lang: str = "en",
) -> dict:
    """미션 상세 조회"""
    template = repository.get_template_by_id(session, template_id)
    if not template:
        raise NotFoundError("미션을 찾을 수 없어요")

    steps = repository.get_steps_by_template_id(session, template_id)
    progress = repository.get_progress_by_profile_and_template(
        session, profile_id, template_id
    )

    title = template.title_en if lang == "en" else template.title_ko
    description = template.description_en if lang == "en" else template.description_ko

    steps_data = []
    for step in steps:
        step_title = step.title_en if lang == "en" else step.title_ko
        step_desc = step.description_en if lang == "en" else step.description_ko

        # 단계 완료 여부 확인
        is_completed = False
        if progress:
            step_progress = repository.get_step_progress(session, progress.id, step.id)
            is_completed = step_progress.is_completed if step_progress else False

        steps_data.append(
            {
                "id": str(step.id),
                "step_order": step.step_order,
                "title": step_title,
                "description": step_desc,
                "is_completed": is_completed,
                "phrases": [],  # TODO: phrases 연동
            }
        )

    result = {
        "id": str(template.id),
        "title": title,
        "description": description,
        "mission_type": template.mission_type,
        "estimated_duration_min": template.estimated_duration_min,
        "icon_url": template.icon_url,
        "steps": steps_data,
        "user_progress": None,
    }

    if progress:
        result["user_progress"] = {
            "id": str(progress.id),
            "status": progress.status,
            "current_step": progress.current_step,
            "started_at": progress.started_at,
        }

    return result


# ─────────────────────────────────────────────────
# Endpoint
# ─────────────────────────────────────────────────


@router.get("/{mission_id}", response_model=ApiResponse[MissionDetailResponse])
def get_mission(
    mission_id: UUID,
    profile: CurrentProfile,
    session: Session = Depends(get_session),
) -> ApiResponse[MissionDetailResponse] | JSONResponse:
    """미션 상세 조회"""
    try:
        mission = get_mission_detail(
            session, mission_id, profile.id, lang=profile.preferred_language
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

    user_progress = None
    if mission["user_progress"]:
        user_progress = UserProgressResponse(**mission["user_progress"])

    steps = [
        MissionStepResponse(
            id=s["id"],
            step_order=s["step_order"],
            title=s["title"],
            description=s["description"],
            is_completed=s["is_completed"],
            phrases=s["phrases"],
        )
        for s in mission["steps"]
    ]

    return ApiResponse(
        status=Status.SUCCESS,
        message="조회에 성공했어요",
        data=MissionDetailResponse(
            id=mission["id"],
            title=mission["title"],
            description=mission["description"],
            mission_type=mission["mission_type"],
            estimated_duration_min=mission["estimated_duration_min"],
            icon_url=mission["icon_url"],
            steps=steps,
            user_progress=user_progress,
        ),
    )
