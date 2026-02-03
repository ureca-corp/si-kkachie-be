"""Supabase Storage Provider

동기/비동기 Supabase Storage 구현

사용법:
- 동기: SupabaseStorageProvider (기존 호환)
- 비동기: AsyncSupabaseStorageProvider
"""

from typing import BinaryIO

from src.external.storage.base import (
    IAsyncStorageProvider,
    IStorageProvider,
    StorageError,
)


class SupabaseStorageProvider(IStorageProvider):
    """Supabase 스토리지 공급자 (동기)"""

    def __init__(self, url: str, key: str, bucket: str):
        from supabase import create_client

        self.client = create_client(url, key)
        self.bucket = bucket

    def upload(
        self,
        file: BinaryIO,
        key: str,
        content_type: str | None = None,
    ) -> str:
        try:
            data = file.read()
            options = {"content-type": content_type} if content_type else {}
            self.client.storage.from_(self.bucket).upload(key, data, options)
            return self.client.storage.from_(self.bucket).get_public_url(key)
        except Exception as e:
            raise StorageError(f"Upload failed: {e}") from e

    def download(self, key: str) -> bytes:
        try:
            return self.client.storage.from_(self.bucket).download(key)
        except Exception as e:
            raise StorageError(f"Download failed: {e}") from e

    def delete(self, key: str) -> bool:
        try:
            self.client.storage.from_(self.bucket).remove([key])
            return True
        except Exception as e:
            raise StorageError(f"Delete failed: {e}") from e

    def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        try:
            result = self.client.storage.from_(self.bucket).create_signed_url(
                key,
                expires_in,
            )
            return result["signedURL"]
        except Exception as e:
            raise StorageError(f"Create signed URL failed: {e}") from e

    def get_upload_url(self, key: str, expires_in: int = 3600) -> str:
        try:
            result = self.client.storage.from_(self.bucket).create_signed_upload_url(key)
            return result["signedURL"]
        except Exception as e:
            raise StorageError(f"Create upload URL failed: {e}") from e


class AsyncSupabaseStorageProvider(IAsyncStorageProvider):
    """Supabase 스토리지 공급자 (비동기)"""

    def __init__(self, url: str, key: str, bucket: str):
        self._url = url
        self._key = key
        self.bucket = bucket
        self._client = None

    async def _get_client(self):
        """Lazy initialization of async client"""
        if self._client is None:
            from supabase import acreate_client

            self._client = await acreate_client(self._url, self._key)
        return self._client

    async def upload(
        self,
        file: BinaryIO,
        key: str,
        content_type: str | None = None,
    ) -> str:
        try:
            client = await self._get_client()
            data = file.read()
            options = {"content-type": content_type} if content_type else {}
            await client.storage.from_(self.bucket).upload(key, data, options)
            return client.storage.from_(self.bucket).get_public_url(key)
        except Exception as e:
            raise StorageError(f"Upload failed: {e}") from e

    async def download(self, key: str) -> bytes:
        try:
            client = await self._get_client()
            return await client.storage.from_(self.bucket).download(key)
        except Exception as e:
            raise StorageError(f"Download failed: {e}") from e

    async def delete(self, key: str) -> bool:
        try:
            client = await self._get_client()
            await client.storage.from_(self.bucket).remove([key])
            return True
        except Exception as e:
            raise StorageError(f"Delete failed: {e}") from e

    async def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        try:
            client = await self._get_client()
            result = await client.storage.from_(self.bucket).create_signed_url(
                key,
                expires_in,
            )
            return result["signedURL"]
        except Exception as e:
            raise StorageError(f"Create signed URL failed: {e}") from e

    async def get_upload_url(self, key: str, expires_in: int = 3600) -> str:
        try:
            client = await self._get_client()
            result = await client.storage.from_(self.bucket).create_signed_upload_url(key)
            return result["signedURL"]
        except Exception as e:
            raise StorageError(f"Create upload URL failed: {e}") from e

    async def close(self) -> None:
        """클라이언트 종료"""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
