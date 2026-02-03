"""translations 도메인 테스트 픽스처"""

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlmodel import Session

from src.modules.profiles import Profile
from src.modules.translations._models import (
    Translation,
    TranslationCategoryMapping,
    TranslationContextPrompt,
    TranslationPrimaryCategory,
    TranslationSubCategory,
    TranslationThread,
)


def _utcnow() -> datetime:
    return datetime.now(UTC)


# ─────────────────────────────────────────────────
# Category Fixtures
# ─────────────────────────────────────────────────


@pytest.fixture
def seeded_categories(
    session: Session,
) -> tuple[
    list[TranslationPrimaryCategory],
    list[TranslationSubCategory],
    list[TranslationCategoryMapping],
]:
    """테스트용 카테고리 seed 데이터 (마이그레이션에서 이미 생성된 데이터 사용)"""
    from sqlmodel import select

    # 이미 존재하는 데이터 조회 (마이그레이션에서 seed됨)
    primaries = list(
        session.exec(
            select(TranslationPrimaryCategory).order_by(
                TranslationPrimaryCategory.display_order
            )
        ).all()
    )
    subs = list(
        session.exec(
            select(TranslationSubCategory).order_by(TranslationSubCategory.display_order)
        ).all()
    )
    mappings = list(session.exec(select(TranslationCategoryMapping)).all())

    # 데이터가 없으면 테스트용 데이터 생성 (SQLite 등 다른 DB 환경)
    if not primaries:
        primaries = [
            TranslationPrimaryCategory(
                code="FD6", name_ko="음식점", name_en="Restaurant", display_order=1
            ),
            TranslationPrimaryCategory(
                code="CE7", name_ko="카페", name_en="Cafe", display_order=2
            ),
            TranslationPrimaryCategory(
                code="GEN", name_ko="일반", name_en="General", display_order=99
            ),
        ]
        for p in primaries:
            session.add(p)

        subs = [
            TranslationSubCategory(
                code="ordering", name_ko="주문", name_en="Ordering", display_order=1
            ),
            TranslationSubCategory(
                code="payment", name_ko="결제", name_en="Payment", display_order=2
            ),
            TranslationSubCategory(
                code="inquiry", name_ko="문의", name_en="Inquiry", display_order=10
            ),
            TranslationSubCategory(
                code="other", name_ko="기타", name_en="Other", display_order=99
            ),
        ]
        for s in subs:
            session.add(s)

        session.commit()

        # Category Mappings
        mappings_data = [
            ("FD6", "ordering"),
            ("FD6", "payment"),
            ("FD6", "inquiry"),
            ("FD6", "other"),
            ("CE7", "ordering"),
            ("CE7", "payment"),
            ("CE7", "other"),
            ("GEN", "inquiry"),
            ("GEN", "other"),
        ]
        mappings = [
            TranslationCategoryMapping(id=uuid4(), primary_code=p, sub_code=s)
            for p, s in mappings_data
        ]
        for m in mappings:
            session.add(m)

        session.commit()

    return primaries, subs, mappings


@pytest.fixture
def seeded_context_prompts(
    session: Session,
    seeded_categories: tuple[
        list[TranslationPrimaryCategory],
        list[TranslationSubCategory],
        list[TranslationCategoryMapping],
    ],
) -> list[TranslationContextPrompt]:
    """테스트용 컨텍스트 프롬프트 seed 데이터"""
    prompts = [
        TranslationContextPrompt(
            id=uuid4(),
            primary_code="FD6",
            sub_code="ordering",
            prompt_ko="음식점에서 음식을 주문하는 상황입니다.",
            prompt_en="This is a situation of ordering food at a restaurant.",
            keywords="메뉴,주문,추천",
        ),
        TranslationContextPrompt(
            id=uuid4(),
            primary_code="FD6",
            sub_code="payment",
            prompt_ko="음식점에서 결제하는 상황입니다.",
            prompt_en="This is a payment situation at a restaurant.",
            keywords="카드,현금,계산",
        ),
    ]
    for p in prompts:
        session.add(p)
    session.commit()
    return prompts


# ─────────────────────────────────────────────────
# Thread Fixtures
# ─────────────────────────────────────────────────


@pytest.fixture
def created_thread(
    session: Session,
    test_profile: Profile,
    seeded_categories: tuple[
        list[TranslationPrimaryCategory],
        list[TranslationSubCategory],
        list[TranslationCategoryMapping],
    ],
) -> TranslationThread:
    """DB에 저장된 번역 스레드"""
    thread = TranslationThread(
        id=uuid4(),
        profile_id=test_profile.id,
        primary_category="FD6",
        sub_category="ordering",
        created_at=_utcnow(),
    )
    session.add(thread)
    session.commit()
    session.refresh(thread)
    return thread


@pytest.fixture
def thread_with_translations(
    session: Session,
    test_profile: Profile,
    created_thread: TranslationThread,
) -> tuple[TranslationThread, list[Translation]]:
    """번역 기록이 연결된 스레드"""
    translations = [
        Translation(
            id=uuid4(),
            profile_id=test_profile.id,
            thread_id=created_thread.id,
            source_text="주문할게요",
            translated_text="I'd like to order",
            source_lang="ko",
            target_lang="en",
            translation_type="text",
            context_primary="FD6",
            context_sub="ordering",
            created_at=_utcnow(),
        ),
        Translation(
            id=uuid4(),
            profile_id=test_profile.id,
            thread_id=created_thread.id,
            source_text="메뉴판 주세요",
            translated_text="May I have the menu",
            source_lang="ko",
            target_lang="en",
            translation_type="text",
            context_primary="FD6",
            context_sub="ordering",
            created_at=_utcnow(),
        ),
    ]
    for t in translations:
        session.add(t)
    session.commit()
    return created_thread, translations


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
