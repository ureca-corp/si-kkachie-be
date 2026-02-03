"""Naver API 인터페이스 및 에러 클래스"""

from abc import ABC, abstractmethod


class NaverError(Exception):
    """Naver API 기본 에러"""

    def __init__(self, message: str, code: int | None = None):
        self.message = message
        self.code = code
        super().__init__(message)


class INaverProvider(ABC):
    """Naver API Provider 인터페이스"""

    @abstractmethod
    async def reverse_geocode(self, lng: float, lat: float) -> dict:
        """좌표 -> 주소 변환 (Reverse Geocoding)

        Args:
            lng: 경도
            lat: 위도

        Returns:
            Naver API 응답 (JSON)
        """
        ...

    @abstractmethod
    async def search_places(self, query: str, display: int = 5) -> dict:
        """장소 검색

        Args:
            query: 검색어
            display: 결과 개수 (최대 5개)

        Returns:
            Naver API 응답 (JSON)
        """
        ...

    @abstractmethod
    async def directions(
        self,
        start_lng: float,
        start_lat: float,
        goal_lng: float,
        goal_lat: float,
        waypoints: list[tuple[float, float]] | None = None,
        option: str = "traoptimal",
    ) -> dict:
        """경로 검색

        Args:
            start_lng: 출발지 경도
            start_lat: 출발지 위도
            goal_lng: 도착지 경도
            goal_lat: 도착지 위도
            waypoints: 경유지 리스트 [(lng, lat), ...]
            option: 경로 옵션

        Returns:
            dict: {
                "total_distance_m": int,
                "total_duration_s": int,
                "path": [[lng, lat], ...] 좌표 배열
            }
        """
        ...

    @abstractmethod
    async def close(self) -> None:
        """HTTP 클라이언트 종료"""
        ...
