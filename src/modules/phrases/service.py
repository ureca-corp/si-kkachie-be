"""phrases 도메인 Service"""

from datetime import UTC, datetime
from uuid import UUID

from sqlmodel import Session

from src.core.exceptions import NotFoundError

from . import repository
from .models import Phrase


def _utcnow() -> datetime:
    return datetime.now(UTC)


def get_phrases(
    session: Session,
    category: str | None = None,
    mission_step_id: UUID | None = None,
) -> list[Phrase]:
    """추천 문장 조회"""
    if mission_step_id:
        return repository.get_by_mission_step_id(session, mission_step_id)
    if category:
        return repository.get_by_category(session, category)
    return repository.get_all_active(session)


def use_phrase(session: Session, phrase_id: UUID) -> Phrase:
    """문장 사용 기록"""
    phrase = repository.get_by_id(session, phrase_id)
    if not phrase or not phrase.is_active:
        raise NotFoundError("문장을 찾을 수 없어요")

    phrase.usage_count += 1
    phrase.updated_at = _utcnow()

    return repository.update(session, phrase)
