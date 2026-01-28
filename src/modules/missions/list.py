"""GET /missions - 미션 목록 조회"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

from src.core.database import get_session
from src.core.deps import CurrentProfile
from src.core.response import ApiResponse, Status

from . import _repository as repository

router = APIRouter()


# ─────────────────────────────────────────────────
# Response DTOs
# ─────────────────────────────────────────────────


class UserProgressResponse(BaseModel):
    """사용자 진행 상태"""

    id: str | None = None
    status: str
    current_step: int
    started_at: datetime | None = None


class MissionListItemResponse(BaseModel):
    """미션 목록 아이템"""

    id: str
    title: str
    description: str
    mission_type: str
    estimated_duration_min: int
    icon_url: str | None = None
    steps_count: int
    user_progress: UserProgressResponse | None = None


# ─────────────────────────────────────────────────
# Service
# ─────────────────────────────────────────────────


def get_missions_with_progress(
    session: Session,
    profile_id: UUID,
    lang: str = "en",
) -> list[dict]:
    """미션 목록 조회 (사용자 진행 상태 포함)"""
    templates = repository.get_all_templates(session)
    progress_list = repository.get_progress_by_profile(session, profile_id)

    # 진행 상태를 템플릿 ID로 매핑
    progress_map = {p.mission_template_id: p for p in progress_list}

    result = []
    for template in templates:
        steps = repository.get_steps_by_template_id(session, template.id)

        title = template.title_en if lang == "en" else template.title_ko
        description = (
            template.description_en if lang == "en" else template.description_ko
        )

        mission_data = {
            "id": str(template.id),
            "title": title,
            "description": description,
            "mission_type": template.mission_type,
            "estimated_duration_min": template.estimated_duration_min,
            "icon_url": template.icon_url,
            "steps_count": len(steps),
            "user_progress": None,
        }

        # 진행 상태 추가
        progress = progress_map.get(template.id)
        if progress:
            mission_data["user_progress"] = {
                "id": str(progress.id),
                "status": progress.status,
                "current_step": progress.current_step,
                "started_at": progress.started_at,
            }

        result.append(mission_data)

    return result


# ─────────────────────────────────────────────────
# Endpoint
# ─────────────────────────────────────────────────


@router.get("/", response_model=ApiResponse[list[MissionListItemResponse]])
def list_missions(
    profile: CurrentProfile,
    session: Session = Depends(get_session),
) -> ApiResponse[list[MissionListItemResponse]]:
    """미션 목록 조회"""
    missions = get_missions_with_progress(
        session, profile.id, lang=profile.preferred_language
    )

    items = []
    for m in missions:
        user_progress = None
        if m["user_progress"]:
            user_progress = UserProgressResponse(**m["user_progress"])

        items.append(
            MissionListItemResponse(
                id=m["id"],
                title=m["title"],
                description=m["description"],
                mission_type=m["mission_type"],
                estimated_duration_min=m["estimated_duration_min"],
                icon_url=m["icon_url"],
                steps_count=m["steps_count"],
                user_progress=user_progress,
            )
        )

    return ApiResponse(
        status=Status.SUCCESS,
        message="조회에 성공했어요",
        data=items,
    )
