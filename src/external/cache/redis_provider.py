import json
from typing import Any

from src.external.cache.base import ICacheProvider


class RedisProvider(ICacheProvider):
    """표준 Redis 캐시 공급자

    실제 사용 시 redis 패키지 설치 필요:
    uv add redis
    """

    def __init__(self, url: str):
        import redis

        self.client = redis.from_url(url)

    def get(self, key: str) -> Any | None:
        value = self.client.get(key)
        if value is None:
            return None
        return json.loads(value)

    def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> bool:
        serialized = json.dumps(value)
        if ttl:
            return bool(self.client.setex(key, ttl, serialized))
        return bool(self.client.set(key, serialized))

    def delete(self, key: str) -> bool:
        return bool(self.client.delete(key))

    def exists(self, key: str) -> bool:
        return bool(self.client.exists(key))

    def incr(self, key: str, amount: int = 1) -> int:
        return self.client.incrby(key, amount)

    def expire(self, key: str, ttl: int) -> bool:
        return bool(self.client.expire(key, ttl))

    def ttl(self, key: str) -> int:
        return self.client.ttl(key)
