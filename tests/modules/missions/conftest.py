"""missions 도메인 테스트 픽스처"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlmodel import Session

from src.core.enums import MissionStatus, MissionType
from src.modules.missions._models import (
    MissionProgress,
    MissionStep,
    MissionStepProgress,
    MissionTemplate,
)
from src.modules.profiles._models import Profile


def _utcnow() -> datetime:
    return datetime.now(UTC)


@pytest.fixture
def taxi_mission_template(session: Session) -> MissionTemplate:
    """택시 미션 템플릿"""
    template = MissionTemplate(
        id=uuid4(),
        title_ko="택시 이용하기",
        title_en="Taking a Taxi",
        description_ko="한국에서 택시 이용하는 방법을 배워보세요",
        description_en="Learn how to take a taxi in Korea",
        mission_type=MissionType.TAXI,
        estimated_duration_min=15,
        icon_url=None,
        is_active=True,
        created_at=_utcnow(),
        updated_at=_utcnow(),
    )
    session.add(template)
    session.commit()
    session.refresh(template)
    return template


@pytest.fixture
def taxi_mission_steps(
    session: Session, taxi_mission_template: MissionTemplate
) -> list[MissionStep]:
    """택시 미션 단계들"""
    steps_data = [
        ("택시 잡기", "Hailing a Taxi", "택시를 잡는 방법", "How to hail a taxi"),
        ("목적지 전달", "Telling Destination", "목적지를 전달하세요", "Tell your destination"),
        ("요금 확인", "Checking Fare", "요금을 확인하세요", "Check the fare"),
        ("결제하기", "Making Payment", "결제를 진행하세요", "Make the payment"),
        ("하차하기", "Getting Off", "안전하게 하차하세요", "Get off safely"),
    ]

    steps = []
    for i, (title_ko, title_en, desc_ko, desc_en) in enumerate(steps_data, 1):
        step = MissionStep(
            id=uuid4(),
            mission_template_id=taxi_mission_template.id,
            step_order=i,
            title_ko=title_ko,
            title_en=title_en,
            description_ko=desc_ko,
            description_en=desc_en,
            created_at=_utcnow(),
        )
        session.add(step)
        steps.append(step)

    session.commit()
    for step in steps:
        session.refresh(step)

    return steps


@pytest.fixture
def mission_progress_not_started(
    session: Session,
    test_profile: Profile,
    taxi_mission_template: MissionTemplate,
) -> MissionProgress:
    """시작 전 미션 진행 상태"""
    progress = MissionProgress(
        id=uuid4(),
        profile_id=test_profile.id,
        mission_template_id=taxi_mission_template.id,
        status=MissionStatus.NOT_STARTED,
        result=None,
        current_step=0,
        started_at=None,
        ended_at=None,
        created_at=_utcnow(),
        updated_at=_utcnow(),
    )
    session.add(progress)
    session.commit()
    session.refresh(progress)
    return progress


@pytest.fixture
def mission_progress_in_progress(
    session: Session,
    test_profile: Profile,
    taxi_mission_template: MissionTemplate,
    taxi_mission_steps: list[MissionStep],
) -> MissionProgress:
    """진행 중인 미션"""
    progress = MissionProgress(
        id=uuid4(),
        profile_id=test_profile.id,
        mission_template_id=taxi_mission_template.id,
        status=MissionStatus.IN_PROGRESS,
        result=None,
        current_step=2,
        started_at=_utcnow(),
        ended_at=None,
        created_at=_utcnow(),
        updated_at=_utcnow(),
    )
    session.add(progress)
    session.commit()
    session.refresh(progress)

    # 첫 번째 단계 완료 기록 추가
    step_progress = MissionStepProgress(
        id=uuid4(),
        mission_progress_id=progress.id,
        mission_step_id=taxi_mission_steps[0].id,
        is_completed=True,
        completed_at=_utcnow(),
        created_at=_utcnow(),
    )
    session.add(step_progress)
    session.commit()

    return progress


@pytest.fixture
def end_mission_request_resolved() -> dict:
    """미션 종료 요청 (해결됨)"""
    return {"result": "resolved"}


@pytest.fixture
def end_mission_request_partially_resolved() -> dict:
    """미션 종료 요청 (부분 해결)"""
    return {"result": "partially_resolved"}


@pytest.fixture
def end_mission_request_unresolved() -> dict:
    """미션 종료 요청 (미해결)"""
    return {"result": "unresolved"}
