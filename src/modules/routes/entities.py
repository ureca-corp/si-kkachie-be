"""routes 도메인 Request/Response DTO"""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class PointRequest(BaseModel):
    """좌표 요청"""

    name: str
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)


class RouteSearchRequest(BaseModel):
    """경로 검색 요청"""

    start: PointRequest
    end: PointRequest
    waypoints: list[PointRequest] | None = Field(default=None, max_length=5)
    option: str = "traoptimal"

    @field_validator("waypoints")
    @classmethod
    def validate_waypoints(cls, v: list | None) -> list | None:
        if v and len(v) > 5:
            msg = "경유지는 최대 5개까지 가능해요"
            raise ValueError(msg)
        return v


class PointResponse(BaseModel):
    """좌표 응답"""

    name: str
    lat: float
    lng: float


class RouteSearchResponse(BaseModel):
    """경로 검색 응답"""

    id: str
    start: PointResponse
    end: PointResponse
    total_distance_m: int
    total_duration_s: int
    distance_text: str
    duration_text: str
    path: list[dict]


class RouteHistoryResponse(BaseModel):
    """경로 히스토리 응답"""

    id: str
    start_name: str
    end_name: str
    total_distance_m: int
    total_duration_s: int
    created_at: datetime
