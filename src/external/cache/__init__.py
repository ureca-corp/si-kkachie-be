from src.core.config import settings
from src.external.cache.base import ICacheProvider

_cache_instance: ICacheProvider | None = None


def get_cache_provider() -> ICacheProvider | None:
    """설정에 따라 적절한 캐시 공급자 반환 (설정 없으면 None)"""
    global _cache_instance

    if settings.CACHE_BACKEND is None:
        return None

    if _cache_instance is not None:
        return _cache_instance

    match settings.CACHE_BACKEND:
        case "redis":
            from src.external.cache.redis_provider import RedisProvider

            _cache_instance = RedisProvider(
                url=settings.REDIS_URL or "",
            )

        case "upstash":
            from src.external.cache.upstash_provider import UpstashProvider

            _cache_instance = UpstashProvider(
                url=settings.UPSTASH_REDIS_URL or "",
                token=settings.UPSTASH_REDIS_TOKEN or "",
            )

        case _:
            return None

    return _cache_instance


__all__ = [
    "ICacheProvider",
    "get_cache_provider",
]
