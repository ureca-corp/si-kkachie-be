from src.core.config import settings
from src.external.storage.base import IStorageProvider

_storage_instance: IStorageProvider | None = None


def get_storage_provider() -> IStorageProvider | None:
    """설정에 따라 적절한 스토리지 공급자 반환 (설정 없으면 None)"""
    global _storage_instance

    if settings.STORAGE_BACKEND is None:
        return None

    if _storage_instance is not None:
        return _storage_instance

    match settings.STORAGE_BACKEND:
        case "s3":
            from src.external.storage.s3_provider import S3StorageProvider

            _storage_instance = S3StorageProvider(
                bucket=settings.S3_BUCKET or "",
                region=settings.S3_REGION or "",
                access_key=settings.S3_ACCESS_KEY or "",
                secret_key=settings.S3_SECRET_KEY or "",
            )

        case "r2":
            from src.external.storage.r2_provider import R2StorageProvider

            _storage_instance = R2StorageProvider(
                bucket=settings.R2_BUCKET or "",
                account_id=settings.R2_ACCOUNT_ID or "",
                access_key=settings.R2_ACCESS_KEY or "",
                secret_key=settings.R2_SECRET_KEY or "",
            )

        case "supabase":
            from src.external.storage.supabase_provider import SupabaseStorageProvider

            _storage_instance = SupabaseStorageProvider(
                url=settings.SUPABASE_URL or "",
                key=settings.SUPABASE_KEY or "",
                bucket=settings.SUPABASE_STORAGE_BUCKET or "",
            )

        case _:
            return None

    return _storage_instance


__all__ = [
    "IStorageProvider",
    "get_storage_provider",
]
