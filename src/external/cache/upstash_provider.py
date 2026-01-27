import json
from typing import Any

from src.external.cache.base import ICacheProvider


class UpstashProvider(ICacheProvider):
    """Upstash Redis 캐시 공급자 (REST API)

    실제 사용 시 upstash-redis 패키지 설치 필요:
    uv add upstash-redis
    """

    def __init__(self, url: str, token: str):
        from upstash_redis import Redis

        self.client = Redis(url=url, token=token)

    def get(self, key: str) -> Any | None:
        value = self.client.get(key)
        if value is None:
            return None
        return json.loads(value) if isinstance(value, str) else value

    def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> bool:
        serialized = json.dumps(value)
        if ttl:
            return self.client.setex(key, ttl, serialized) == "OK"
        return self.client.set(key, serialized) == "OK"

    def delete(self, key: str) -> bool:
        return self.client.delete(key) > 0

    def exists(self, key: str) -> bool:
        return self.client.exists(key) > 0

    def incr(self, key: str, amount: int = 1) -> int:
        return self.client.incrby(key, amount)

    def expire(self, key: str, ttl: int) -> bool:
        return self.client.expire(key, ttl) == 1

    def ttl(self, key: str) -> int:
        return self.client.ttl(key)
