"""phrases 도메인 Repository (공유)"""

from datetime import UTC, datetime
from uuid import UUID

from sqlmodel import Session, select

from ._models import Phrase, PhraseStepMapping


def _utcnow() -> datetime:
    return datetime.now(UTC)


# === List 관련 ===
def get_all_active(session: Session) -> list[Phrase]:
    """모든 활성 문장 조회 (사용량 내림차순)"""
    query = (
        select(Phrase)
        .where(Phrase.is_active == True)  # noqa: E712
        .order_by(Phrase.usage_count.desc())
    )
    return list(session.exec(query).all())


def get_by_category(session: Session, category: str) -> list[Phrase]:
    """카테고리별 문장 조회"""
    query = (
        select(Phrase)
        .where(Phrase.is_active == True, Phrase.category == category)  # noqa: E712
        .order_by(Phrase.usage_count.desc())
    )
    return list(session.exec(query).all())


def get_by_mission_step_id(session: Session, mission_step_id: UUID) -> list[Phrase]:
    """미션 단계별 문장 조회"""
    query = (
        select(Phrase)
        .join(PhraseStepMapping, Phrase.id == PhraseStepMapping.phrase_id)
        .where(
            PhraseStepMapping.mission_step_id == mission_step_id,
            Phrase.is_active == True,  # noqa: E712
        )
        .order_by(PhraseStepMapping.display_order)
    )
    return list(session.exec(query).all())


# === Use 관련 ===
def get_by_id(session: Session, phrase_id: UUID) -> Phrase | None:
    """문장 조회"""
    return session.get(Phrase, phrase_id)


def increment_usage_count(session: Session, phrase: Phrase) -> Phrase:
    """문장 사용량 증가"""
    phrase.usage_count += 1
    phrase.updated_at = _utcnow()
    session.add(phrase)
    session.commit()
    session.refresh(phrase)
    return phrase
