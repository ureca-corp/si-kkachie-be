"""routes 모델

DDD_CLASS_DIAGRAM.md 기반:
- route_history: 경로 검색 기록
- PostGIS GEOGRAPHY(Point, 4326) 타입 사용

Note: SQLite 테스트에서는 PostGIS를 사용할 수 없으므로
좌표를 별도 컬럼으로 저장합니다.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON
from sqlmodel import Column, Field, SQLModel

from src.core.enums import RouteOption


def _utcnow() -> datetime:
    return datetime.now(UTC)


class RouteHistory(SQLModel, table=True):
    """경로 검색 기록"""

    __tablename__ = "route_history"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    profile_id: UUID = Field(foreign_key="profiles.id", index=True)
    start_name: str = Field()
    # SQLite 호환을 위해 좌표를 별도 필드로 저장
    start_lat: float = Field()
    start_lng: float = Field()
    end_name: str = Field()
    end_lat: float = Field()
    end_lng: float = Field()
    # 경유지 (JSON)
    waypoints: list[dict] | None = Field(default=None, sa_column=Column(JSON))
    route_option: str = Field(default=RouteOption.TRAOPTIMAL.value)
    total_distance_m: int = Field()
    total_duration_s: int = Field()
    # 경로 데이터 (JSON)
    path_data: list[dict] = Field(sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=_utcnow, index=True)
