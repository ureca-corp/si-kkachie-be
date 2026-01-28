"""translations 도메인 Repository (공유)"""

from uuid import UUID

from sqlmodel import Session, func, select

from ._models import Translation


def create(session: Session, translation: Translation) -> Translation:
    """번역 기록 생성"""
    session.add(translation)
    session.commit()
    session.refresh(translation)
    return translation


def get_by_id(session: Session, translation_id: UUID) -> Translation | None:
    """번역 기록 조회"""
    return session.get(Translation, translation_id)


def get_by_profile_id(
    session: Session,
    profile_id: UUID,
    page: int = 1,
    limit: int = 20,
    translation_type: str | None = None,
    mission_progress_id: UUID | None = None,
) -> tuple[list[Translation], int]:
    """사용자별 번역 히스토리 조회 (페이지네이션)"""
    # 기본 쿼리
    query = select(Translation).where(Translation.profile_id == profile_id)

    # 필터 적용
    if translation_type:
        query = query.where(Translation.translation_type == translation_type)
    if mission_progress_id:
        query = query.where(Translation.mission_progress_id == mission_progress_id)

    # 전체 개수 조회
    count_query = select(func.count()).select_from(query.subquery())
    total = session.exec(count_query).one()

    # 정렬 및 페이지네이션
    query = query.order_by(Translation.created_at.desc())  # type: ignore[union-attr]
    query = query.offset((page - 1) * limit).limit(limit)

    translations = list(session.exec(query).all())
    return translations, total


def delete(session: Session, translation: Translation) -> None:
    """번역 기록 삭제"""
    session.delete(translation)
    session.commit()
