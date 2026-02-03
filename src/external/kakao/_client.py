"""Kakao API 공유 HTTP 클라이언트"""

import httpx

# API 타임아웃 (초)
TIMEOUT = 10.0

_client: httpx.AsyncClient | None = None


async def get_client() -> httpx.AsyncClient:
    """공유 HTTP 클라이언트 반환 (lazy initialization)"""
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=TIMEOUT)
    return _client


async def close_client() -> None:
    """HTTP 클라이언트 종료"""
    global _client
    if _client is not None and not _client.is_closed:
        await _client.aclose()
        _client = None
