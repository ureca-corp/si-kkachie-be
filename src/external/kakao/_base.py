"""Kakao API 인터페이스 및 에러 클래스"""

from abc import ABC, abstractmethod


class KakaoError(Exception):
    """Kakao API 기본 에러"""

    def __init__(self, message: str, code: int | None = None):
        self.message = message
        self.code = code
        super().__init__(message)


class IKakaoProvider(ABC):
    """Kakao API Provider 인터페이스"""

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
    async def search_by_category(
        self,
        category: str,
        lng: float,
        lat: float,
        radius: int = 1000,
        page: int = 1,
        size: int = 15,
        sort: str = "distance",
    ) -> dict:
        """카테고리별 장소 검색

        Args:
            category: 카테고리 코드 (MT1, CS2, FD6, CE7 등)
            lng: 경도 (x)
            lat: 위도 (y)
            radius: 검색 반경 미터 (기본 1000, 최대 20000)
            page: 페이지 번호 (기본 1, 최대 45)
            size: 결과 개수 (기본 15, 최대 15)
            sort: 정렬 기준 (distance 또는 accuracy)

        Returns:
            dict: {
                "total_count": int,
                "is_end": bool,
                "places": [...]
            }
        """
        ...

    @abstractmethod
    async def close(self) -> None:
        """HTTP 클라이언트 종료"""
        ...
