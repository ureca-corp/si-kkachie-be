from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from src.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)


def init_db() -> None:
    """데이터베이스 테이블 초기화"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """데이터베이스 세션 의존성"""
    with Session(engine) as session:
        yield session
