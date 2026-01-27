from fastapi.testclient import TestClient

from src.core.config import settings
from src.core.response import Status


def test_health_check(client: TestClient) -> None:
    """헬스체크 엔드포인트 테스트"""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == Status.SUCCESS
    assert data["data"]["version"] == settings.VERSION


def test_readiness_check(client: TestClient) -> None:
    """레디니스 체크 엔드포인트 테스트"""
    response = client.get("/health/ready")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == Status.SUCCESS
    assert data["data"]["database"] == "connected"
    assert "timestamp" in data["data"]
