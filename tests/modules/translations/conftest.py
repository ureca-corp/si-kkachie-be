"""translations 도메인 테스트 픽스처"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlmodel import Session

from src.modules.profiles import Profile
from src.modules.translations._models import Translation


def _utcnow() -> datetime:
    return datetime.now(UTC)


@pytest.fixture
def text_translation_request() -> dict:
    """텍스트 번역 요청 데이터"""
    return {
        "source_text": "안녕하세요",
        "source_lang": "ko",
        "target_lang": "en",
    }


@pytest.fixture
def text_translation_with_mission_request() -> dict:
    """미션 연결된 텍스트 번역 요청"""
    return {
        "source_text": "택시 기사님, 여기로 가주세요",
        "source_lang": "ko",
        "target_lang": "en",
        "mission_progress_id": str(uuid4()),
    }


@pytest.fixture
def created_translation(session: Session, test_profile: Profile) -> Translation:
    """DB에 저장된 번역 기록"""
    translation = Translation(
        id=uuid4(),
        profile_id=test_profile.id,
        source_text="안녕하세요",
        translated_text="Hello",
        source_lang="ko",
        target_lang="en",
        translation_type="text",
        mission_progress_id=None,
        audio_url=None,
        duration_ms=None,
        confidence_score=None,
        created_at=_utcnow(),
    )
    session.add(translation)
    session.commit()
    session.refresh(translation)
    return translation


@pytest.fixture
def voice_translation(session: Session, test_profile: Profile) -> Translation:
    """음성 번역 기록"""
    translation = Translation(
        id=uuid4(),
        profile_id=test_profile.id,
        source_text="감사합니다",
        translated_text="Thank you",
        source_lang="ko",
        target_lang="en",
        translation_type="voice",
        mission_progress_id=None,
        audio_url="https://storage.supabase.co/tts/abc123.mp3",
        duration_ms=1500,
        confidence_score=0.95,
        created_at=_utcnow(),
    )
    session.add(translation)
    session.commit()
    session.refresh(translation)
    return translation
