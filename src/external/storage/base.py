from abc import ABC, abstractmethod
from typing import BinaryIO


class IStorageProvider(ABC):
    """스토리지 공급자 인터페이스"""

    @abstractmethod
    def upload(
        self,
        file: BinaryIO,
        key: str,
        content_type: str | None = None,
    ) -> str:
        """파일 업로드 후 URL 반환"""
        ...

    @abstractmethod
    def download(self, key: str) -> bytes:
        """파일 다운로드"""
        ...

    @abstractmethod
    def delete(self, key: str) -> bool:
        """파일 삭제"""
        ...

    @abstractmethod
    def get_presigned_url(
        self,
        key: str,
        expires_in: int = 3600,
    ) -> str:
        """서명된 URL 생성 (다운로드용)"""
        ...

    @abstractmethod
    def get_upload_url(
        self,
        key: str,
        expires_in: int = 3600,
    ) -> str:
        """서명된 URL 생성 (업로드용)"""
        ...
