"""phrases 도메인 테스트 픽스처"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlmodel import Session

from src.core.enums import MissionType, PhraseCategory
from src.modules.missions.models import MissionStep, MissionTemplate
from src.modules.phrases._models import Phrase, PhraseStepMapping


def _utcnow() -> datetime:
    return datetime.now(UTC)


@pytest.fixture
def taxi_mission_template_for_phrases(session: Session) -> MissionTemplate:
    """택시 미션 템플릿 (phrases 테스트용)"""
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
    session: Session, taxi_mission_template_for_phrases: MissionTemplate
) -> list[MissionStep]:
    """택시 미션 단계들 (phrases 테스트용)"""
    steps_data = [
        ("택시 잡기", "Hailing a Taxi", "택시를 잡는 방법", "How to hail a taxi"),
        ("목적지 전달", "Telling Destination", "목적지를 전달하세요", "Tell your destination"),
    ]

    steps = []
    for i, (title_ko, title_en, desc_ko, desc_en) in enumerate(steps_data, 1):
        step = MissionStep(
            id=uuid4(),
            mission_template_id=taxi_mission_template_for_phrases.id,
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
def greeting_phrase(session: Session) -> Phrase:
    """인사 문장"""
    phrase = Phrase(
        id=uuid4(),
        text_ko="안녕하세요",
        text_en="Hello",
        category=PhraseCategory.GREETING,
        usage_count=100,
        is_active=True,
        created_at=_utcnow(),
        updated_at=_utcnow(),
    )
    session.add(phrase)
    session.commit()
    session.refresh(phrase)
    return phrase


@pytest.fixture
def request_phrase(session: Session) -> Phrase:
    """요청 문장"""
    phrase = Phrase(
        id=uuid4(),
        text_ko="택시!",
        text_en="Taxi!",
        category=PhraseCategory.REQUEST,
        usage_count=50,
        is_active=True,
        created_at=_utcnow(),
        updated_at=_utcnow(),
    )
    session.add(phrase)
    session.commit()
    session.refresh(phrase)
    return phrase


@pytest.fixture
def thanks_phrase(session: Session) -> Phrase:
    """감사 문장"""
    phrase = Phrase(
        id=uuid4(),
        text_ko="감사합니다",
        text_en="Thank you",
        category=PhraseCategory.THANKS,
        usage_count=200,
        is_active=True,
        created_at=_utcnow(),
        updated_at=_utcnow(),
    )
    session.add(phrase)
    session.commit()
    session.refresh(phrase)
    return phrase


@pytest.fixture
def inactive_phrase(session: Session) -> Phrase:
    """비활성 문장"""
    phrase = Phrase(
        id=uuid4(),
        text_ko="비활성 문장",
        text_en="Inactive phrase",
        category=PhraseCategory.GREETING,
        usage_count=0,
        is_active=False,
        created_at=_utcnow(),
        updated_at=_utcnow(),
    )
    session.add(phrase)
    session.commit()
    session.refresh(phrase)
    return phrase


@pytest.fixture
def phrase_step_mapping(
    session: Session,
    request_phrase: Phrase,
    taxi_mission_steps: list[MissionStep],
) -> PhraseStepMapping:
    """문장-단계 매핑"""
    mapping = PhraseStepMapping(
        id=uuid4(),
        phrase_id=request_phrase.id,
        mission_step_id=taxi_mission_steps[0].id,  # 택시 잡기 단계
        display_order=1,
        created_at=_utcnow(),
    )
    session.add(mapping)
    session.commit()
    session.refresh(mapping)
    return mapping
