from src.core.config import settings
from src.external.storage.base import IStorageProvider

_storage_instance: IStorageProvider | None = None


def get_storage_provider() -> IStorageProvider | None:
    """Supabase Storage 공급자 반환 (설정 없으면 None)"""
    global _storage_instance

    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        return None

    if _storage_instance is not None:
        return _storage_instance

    from src.external.storage.supabase_provider import SupabaseStorageProvider

    _storage_instance = SupabaseStorageProvider(
        url=settings.SUPABASE_URL,
        key=settings.SUPABASE_SERVICE_KEY or settings.SUPABASE_KEY,
        bucket=settings.SUPABASE_STORAGE_BUCKET,
    )

    return _storage_instance


__all__ = [
    "IStorageProvider",
    "get_storage_provider",
]
