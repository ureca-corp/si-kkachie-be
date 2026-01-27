from datetime import UTC, datetime
from uuid import UUID

from sqlmodel import Session, select

from .models import User


def create(session: Session, user: User) -> User:
    """사용자 생성"""
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_by_id(session: Session, user_id: UUID) -> User | None:
    """ID로 사용자 조회 (삭제된 사용자 제외)"""
    stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None))
    return session.exec(stmt).first()


def get_by_email(session: Session, email: str) -> User | None:
    """이메일로 사용자 조회 (삭제된 사용자 제외)"""
    stmt = select(User).where(User.email == email, User.deleted_at.is_(None))
    return session.exec(stmt).first()


def get_by_email_include_deleted(session: Session, email: str) -> User | None:
    """이메일로 사용자 조회 (삭제된 사용자 포함)"""
    stmt = select(User).where(User.email == email)
    return session.exec(stmt).first()


def update(session: Session, user: User) -> User:
    """사용자 정보 업데이트"""
    user.updated_at = datetime.now(UTC)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def update_login(session: Session, user: User) -> User:
    """로그인 정보 업데이트"""
    user.last_login_at = datetime.now(UTC)
    user.login_count += 1
    user.updated_at = datetime.now(UTC)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def soft_delete(session: Session, user: User) -> User:
    """소프트 삭제"""
    user.soft_delete()
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_all(session: Session) -> list[User]:
    """모든 활성 사용자 조회"""
    stmt = select(User).where(User.deleted_at.is_(None))
    return list(session.exec(stmt).all())
