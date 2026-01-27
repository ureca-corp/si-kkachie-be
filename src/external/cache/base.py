from abc import ABC, abstractmethod
from typing import Any


class ICacheProvider(ABC):
    """캐시 공급자 인터페이스"""

    @abstractmethod
    def get(self, key: str) -> Any | None:
        """캐시 값 조회"""
        ...

    @abstractmethod
    def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> bool:
        """캐시 값 저장 (ttl: 초 단위)"""
        ...

    @abstractmethod
    def delete(self, key: str) -> bool:
        """캐시 삭제"""
        ...

    @abstractmethod
    def exists(self, key: str) -> bool:
        """키 존재 여부"""
        ...

    @abstractmethod
    def incr(self, key: str, amount: int = 1) -> int:
        """값 증가 (Rate Limiting용)"""
        ...

    @abstractmethod
    def expire(self, key: str, ttl: int) -> bool:
        """TTL 설정"""
        ...

    @abstractmethod
    def ttl(self, key: str) -> int:
        """남은 TTL 조회"""
        ...
