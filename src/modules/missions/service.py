"""missions 도메인 Service"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlmodel import Session

from src.core.enums import MissionStatus
from src.core.exceptions import ConflictError, NotFoundError, ValidationError

from . import repository
from .entities import EndMissionRequest, UpdateProgressRequest
from .models import MissionProgress, MissionStepProgress


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
        duration = ended_at - started_at
        duration_minutes = int(duration.total_seconds() / 60)

    return {
        "progress_id": str(progress.id),
        "status": progress.status,
        "result": progress.result,
        "ended_at": ended_at,
        "duration_minutes": duration_minutes,
    }
