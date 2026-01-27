"""profiles 도메인 Repository"""

from uuid import UUID

from sqlmodel import Session, select

from .models import Profile


def get_by_user_id(session: Session, user_id: UUID) -> Profile | None:
    """Supabase user_id로 프로필 조회"""
    return session.exec(select(Profile).where(Profile.user_id == user_id)).first()


def get_by_id(session: Session, profile_id: UUID) -> Profile | None:
    """프로필 ID로 조회"""
    return session.get(Profile, profile_id)


def create(session: Session, profile: Profile) -> Profile:
    """프로필 생성"""
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


def update(session: Session, profile: Profile) -> Profile:
    """프로필 수정"""
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return profile


def delete(session: Session, profile: Profile) -> None:
    """프로필 삭제"""
    session.delete(profile)
    session.commit()
