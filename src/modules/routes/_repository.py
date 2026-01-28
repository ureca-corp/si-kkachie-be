"""routes 도메인 Repository

DB 접근 함수
"""

from uuid import UUID

from sqlmodel import Session, select

from ._models import RouteHistory


def create(session: Session, route: RouteHistory) -> RouteHistory:
    """경로 기록 생성"""
    session.add(route)
    session.commit()
    session.refresh(route)
    return route


def get_by_profile_id(
    session: Session,
    profile_id: UUID,
    limit: int = 10,
) -> list[RouteHistory]:
    """사용자별 최근 경로 조회"""
    query = (
        select(RouteHistory)
        .where(RouteHistory.profile_id == profile_id)
        .order_by(RouteHistory.created_at.desc())
        .limit(limit)
    )
    return list(session.exec(query).all())
