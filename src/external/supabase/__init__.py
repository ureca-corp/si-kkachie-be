"""Supabase Storage Provider

Supabase Storage API 연동

기능 목록:
1. 파일 업로드/다운로드
2. 파일 삭제
3. Presigned URL 생성 (다운로드용/업로드용)
"""

from src.core.config import settings

from ._base import IAsyncStorageProvider, IStorageProvider, StorageError

_storage_instance: IStorageProvider | None = None
_async_storage_instance: IAsyncStorageProvider | None = None


def get_storage_provider() -> IStorageProvider | None:
    """Supabase Storage 공급자 반환 - 동기 (설정 없으면 None)"""
    global _storage_instance

    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        return None

    if _storage_instance is not None:
        return _storage_instance

    from .storage import StorageProvider

    _storage_instance = StorageProvider(
        url=settings.SUPABASE_URL,
        key=settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_KEY,
        bucket=settings.SUPABASE_STORAGE_BUCKET,
    )

    return _storage_instance


async def get_async_storage_provider() -> IAsyncStorageProvider | None:
    """Supabase Storage 공급자 반환 - 비동기 (설정 없으면 None)"""
    global _async_storage_instance

    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        return None

    if _async_storage_instance is not None:
        return _async_storage_instance

    from .storage import AsyncStorageProvider

    _async_storage_instance = AsyncStorageProvider(
        url=settings.SUPABASE_URL,
        key=settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_KEY,
        bucket=settings.SUPABASE_STORAGE_BUCKET,
    )

    return _async_storage_instance


__all__ = [
    # 인터페이스
    "IStorageProvider",
    "IAsyncStorageProvider",
    # 팩토리 함수
    "get_storage_provider",
    "get_async_storage_provider",
    # 에러 클래스
    "StorageError",
]
