"""phrases 도메인 Repository"""

from uuid import UUID

from sqlmodel import Session, select

from .models import Phrase, PhraseStepMapping


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


def get_by_id(session: Session, phrase_id: UUID) -> Phrase | None:
    """문장 조회"""
    return session.get(Phrase, phrase_id)


def update(session: Session, phrase: Phrase) -> Phrase:
    """문장 업데이트"""
    session.add(phrase)
    session.commit()
    session.refresh(phrase)
    return phrase
