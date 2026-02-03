"""Storage external module

파일 스토리지 API 연동을 위한 외부 모듈
- Supabase Storage (동기/비동기)
"""

from src.core.config import settings

from .base import IAsyncStorageProvider, IStorageProvider, StorageError

_storage_instance: IStorageProvider | None = None
_async_storage_instance: IAsyncStorageProvider | None = None


def get_storage_provider() -> IStorageProvider | None:
    """Supabase Storage 공급자 반환 - 동기 (설정 없으면 None)"""
    global _storage_instance

    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        return None

    if _storage_instance is not None:
        return _storage_instance

    from .supabase_provider import SupabaseStorageProvider

    _storage_instance = SupabaseStorageProvider(
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

    from .supabase_provider import AsyncSupabaseStorageProvider

    _async_storage_instance = AsyncSupabaseStorageProvider(
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
