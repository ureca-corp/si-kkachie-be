"""missions 도메인 Repository (공유)"""

from uuid import UUID

from sqlmodel import Session, select

from ._models import MissionProgress, MissionStep, MissionStepProgress, MissionTemplate


def get_all_templates(
    session: Session, active_only: bool = True
) -> list[MissionTemplate]:
    """모든 미션 템플릿 조회"""
    query = select(MissionTemplate)
    if active_only:
        query = query.where(MissionTemplate.is_active == True)  # noqa: E712
    return list(session.exec(query).all())


def get_template_by_id(session: Session, template_id: UUID) -> MissionTemplate | None:
    """미션 템플릿 조회"""
    return session.get(MissionTemplate, template_id)


def get_steps_by_template_id(session: Session, template_id: UUID) -> list[MissionStep]:
    """미션 단계 목록 조회"""
    query = (
        select(MissionStep)
        .where(MissionStep.mission_template_id == template_id)
        .order_by(MissionStep.step_order)  # type: ignore[arg-type]
    )
    return list(session.exec(query).all())


def get_step_by_id(session: Session, step_id: UUID) -> MissionStep | None:
    """미션 단계 조회"""
    return session.get(MissionStep, step_id)


def get_progress_by_profile_and_template(
    session: Session,
    profile_id: UUID,
    template_id: UUID,
    active_only: bool = True,
) -> MissionProgress | None:
    """사용자의 미션 진행 상태 조회"""
    query = select(MissionProgress).where(
        MissionProgress.profile_id == profile_id,
        MissionProgress.mission_template_id == template_id,
    )
    if active_only:
        query = query.where(MissionProgress.status != "ended")
    return session.exec(query).first()


def get_progress_by_profile(
    session: Session,
    profile_id: UUID,
) -> list[MissionProgress]:
    """사용자의 모든 미션 진행 상태 조회"""
    query = select(MissionProgress).where(MissionProgress.profile_id == profile_id)
    return list(session.exec(query).all())


def create_progress(session: Session, progress: MissionProgress) -> MissionProgress:
    """미션 진행 상태 생성"""
    session.add(progress)
    session.commit()
    session.refresh(progress)
    return progress


def update_progress(session: Session, progress: MissionProgress) -> MissionProgress:
    """미션 진행 상태 수정"""
    session.add(progress)
    session.commit()
    session.refresh(progress)
    return progress


def get_step_progress(
    session: Session,
    progress_id: UUID,
    step_id: UUID,
) -> MissionStepProgress | None:
    """단계별 진행 상태 조회"""
    query = select(MissionStepProgress).where(
        MissionStepProgress.mission_progress_id == progress_id,
        MissionStepProgress.mission_step_id == step_id,
    )
    return session.exec(query).first()


def get_completed_steps_count(session: Session, progress_id: UUID) -> int:
    """완료된 단계 수 조회"""
    query = select(MissionStepProgress).where(
        MissionStepProgress.mission_progress_id == progress_id,
        MissionStepProgress.is_completed == True,  # noqa: E712
    )
    return len(list(session.exec(query).all()))


def create_step_progress(
    session: Session,
    step_progress: MissionStepProgress,
) -> MissionStepProgress:
    """단계 진행 상태 생성"""
    session.add(step_progress)
    session.commit()
    session.refresh(step_progress)
    return step_progress


def update_step_progress(
    session: Session,
    step_progress: MissionStepProgress,
) -> MissionStepProgress:
    """단계 진행 상태 수정"""
    session.add(step_progress)
    session.commit()
    session.refresh(step_progress)
    return step_progress
