from abc import ABC, abstractmethod


class IAuthProvider(ABC):
    """인증 공급자 인터페이스"""

    @abstractmethod
    def create_token(self, user_id: str, expires_minutes: int | None = None) -> str:
        """액세스 토큰 생성

        Args:
            user_id: 사용자 ID
            expires_minutes: 만료 시간 (분). None이면 기본값 사용

        Returns:
            JWT 토큰 문자열
        """
        ...

    @abstractmethod
    def verify_token(self, token: str) -> dict | None:
        """토큰 검증 및 페이로드 반환"""
        ...

    @abstractmethod
    def hash_password(self, password: str) -> str:
        """비밀번호 해싱"""
        ...

    @abstractmethod
    def verify_password(self, plain: str, hashed: str) -> bool:
        """비밀번호 검증"""
        ...
