"""routes 모델

DDD_CLASS_DIAGRAM.md 기반:
- route_history: 경로 검색 기록
- PostGIS GEOGRAPHY(Point, 4326) 타입 사용
"""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from geoalchemy2 import Geography, WKBElement
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Point
from sqlalchemy import JSON
from sqlmodel import Column, Field, SQLModel

from src.core.enums import RouteOption


def _utcnow() -> datetime:
    return datetime.now(UTC)


def make_point(lng: float, lat: float) -> WKBElement:
    """Create a PostGIS GEOGRAPHY point from lng/lat."""
    return from_shape(Point(lng, lat), srid=4326)


def get_coords(point: WKBElement | None) -> tuple[float, float] | None:
    """Extract (lat, lng) from a PostGIS GEOGRAPHY point."""
    if point is None:
        return None
    shape = to_shape(point)
    return (shape.y, shape.x)  # lat, lng


class RouteHistory(SQLModel, table=True):
    """경로 검색 기록"""

    __tablename__ = "route_history"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    profile_id: UUID = Field(foreign_key="profiles.id", index=True)
    start_name: str = Field()
    # PostGIS GEOGRAPHY(Point, 4326) - WGS84 좌표계
    start_point: Any = Field(
        sa_column=Column(Geography(geometry_type='POINT', srid=4326))
    )
    end_name: str = Field()
    end_point: Any = Field(
        sa_column=Column(Geography(geometry_type='POINT', srid=4326))
    )
    # 경유지 (JSON)
    waypoints: list[dict] | None = Field(default=None, sa_column=Column(JSON))
    route_option: str = Field(default=RouteOption.TRAOPTIMAL.value)
    total_distance_m: int = Field()
    total_duration_s: int = Field()
    # 경로 데이터 (JSON)
    path_data: list[dict] = Field(sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=_utcnow, index=True)

    @property
    def start_lat(self) -> float | None:
        """Start point latitude."""
        coords = get_coords(self.start_point)
        return coords[0] if coords else None

    @property
    def start_lng(self) -> float | None:
        """Start point longitude."""
        coords = get_coords(self.start_point)
        return coords[1] if coords else None

    @property
    def end_lat(self) -> float | None:
        """End point latitude."""
        coords = get_coords(self.end_point)
        return coords[0] if coords else None

    @property
    def end_lng(self) -> float | None:
        """End point longitude."""
        coords = get_coords(self.end_point)
        return coords[1] if coords else None
