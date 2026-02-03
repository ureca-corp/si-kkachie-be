# 테스트 코드 템플릿 (CSR 패턴)

> create-module 스킬에서 참조하는 테스트 코드 템플릿

**테스트 구조:**
```
tests/modules/{domain}/
├── conftest.py          # 도메인 전용 픽스처
├── test_controller.py   # 엔드포인트 테스트 (통합)
└── test_service.py      # 비즈니스 로직 테스트 (단위)
```

---

## conftest.py

```python
import pytest
from uuid import uuid4
from sqlmodel import Session

from src.modules.{domain}.models import {Domain}
from src.modules.{domain}.entities import Create{Domain}Request

@pytest.fixture
def {domain}_data():
    """테스트용 {domain} 데이터"""
    return {
        "{필드1}": "{테스트값1}",
        "{필드2}": "{테스트값2}",
    }

@pytest.fixture
async def created_{domain}(session: Session, {domain}_data):
    """DB에 저장된 테스트용 {domain}"""
    {domain} = {Domain}(**{domain}_data)
    session.add({domain})
    await session.commit()
    await session.refresh({domain})
    return {domain}
```

---

## test_controller.py

> **통합 테스트: HTTP 요청 → 응답 검증**

```python
import pytest
from httpx import AsyncClient
from uuid import uuid4

class TestCreate{Domain}:
    """POST /{domain} 테스트"""

    async def test_성공(self, client: AsyncClient, {domain}_data):
        """정상 생성"""
        response = await client.post("/{domain}", json={domain}_data)

        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["message"] == "{도메인} 생성이 완료됐어요"
        assert data["data"]["{필드1}"] == {domain}_data["{필드1}"]

    async def test_실패_필수필드_누락(self, client: AsyncClient):
        """필수 필드 누락"""
        response = await client.post("/{domain}", json={})

        assert response.status_code == 422  # Pydantic validation


class TestGet{Domain}:
    """GET /{domain}/{{id}} 테스트"""

    async def test_성공(self, client: AsyncClient, created_{domain}):
        """존재하는 {domain} 조회"""
        response = await client.get(f"/{domain}/{created_{domain}.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["data"]["id"] == str(created_{domain}.id)

    async def test_실패_없음(self, client: AsyncClient):
        """존재하지 않는 ID"""
        response = await client.get(f"/{domain}/{uuid4()}")

        assert response.status_code == 404
        data = response.json()
        assert "{도메인}을 찾을 수 없어요" in data["detail"]


class TestList{Domain}:
    """GET /{domain} 테스트"""

    async def test_성공_빈목록(self, client: AsyncClient):
        """빈 목록"""
        response = await client.get("/{domain}")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SUCCESS"
        assert data["data"] == []

    async def test_성공_페이지네이션(self, client: AsyncClient, session):
        """페이지네이션"""
        # Given: 30개 생성
        for i in range(30):
            {domain} = {Domain}({필드1}=f"test_{i}")
            session.add({domain})
        await session.commit()

        # When: limit=20
        response = await client.get("/{domain}?limit=20")

        # Then: 20개 반환
        data = response.json()
        assert len(data["data"]) == 20


class TestUpdate{Domain}:
    """PUT /{domain}/{{id}} 테스트"""

    async def test_성공(self, client: AsyncClient, created_{domain}):
        """정상 수정"""
        response = await client.put(
            f"/{domain}/{created_{domain}.id}",
            json={"{필드1}": "updated_value"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["{필드1}"] == "updated_value"

    async def test_실패_없음(self, client: AsyncClient):
        """존재하지 않는 ID"""
        response = await client.put(
            f"/{domain}/{uuid4()}",
            json={"{필드1}": "updated_value"},
        )

        assert response.status_code == 404


class TestDelete{Domain}:
    """DELETE /{domain}/{{id}} 테스트"""

    async def test_성공(self, client: AsyncClient, created_{domain}):
        """정상 삭제"""
        response = await client.delete(f"/{domain}/{created_{domain}.id}")

        assert response.status_code == 204

        # 삭제 확인
        response = await client.get(f"/{domain}/{created_{domain}.id}")
        assert response.status_code == 404

    async def test_실패_없음(self, client: AsyncClient):
        """존재하지 않는 ID"""
        response = await client.delete(f"/{domain}/{uuid4()}")

        assert response.status_code == 404
```

---

## test_service.py

> **단위 테스트: 비즈니스 로직 검증 (HTTP 없이)**

```python
import pytest
from uuid import uuid4
from sqlmodel import Session

from src.modules.{domain} import service
from src.modules.{domain}.entities import Create{Domain}Request, Update{Domain}Request

class TestCreate{Domain}Service:
    """create_{domain} 서비스 테스트"""

    async def test_성공(self, session: Session, {domain}_data):
        """정상 생성"""
        request = Create{Domain}Request(**{domain}_data)

        result = await service.create_{domain}(session, request)

        assert result.{필드1} == {domain}_data["{필드1}"]
        assert result.id is not None


class TestGet{Domain}Service:
    """get_{domain} 서비스 테스트"""

    async def test_성공(self, session: Session, created_{domain}):
        """존재하는 {domain} 조회"""
        result = await service.get_{domain}(session, created_{domain}.id)

        assert result.id == created_{domain}.id

    async def test_실패_없음(self, session: Session):
        """존재하지 않는 ID → HTTPException(404)"""
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            await service.get_{domain}(session, uuid4())

        assert exc_info.value.status_code == 404


class TestUpdate{Domain}Service:
    """update_{domain} 서비스 테스트"""

    async def test_성공(self, session: Session, created_{domain}):
        """정상 수정"""
        request = Update{Domain}Request({필드1}="updated_value")

        result = await service.update_{domain}(
            session, created_{domain}.id, request
        )

        assert result.{필드1} == "updated_value"


class TestDelete{Domain}Service:
    """delete_{domain} 서비스 테스트"""

    async def test_성공(self, session: Session, created_{domain}):
        """정상 삭제"""
        await service.delete_{domain}(session, created_{domain}.id)

        # 삭제 확인
        from fastapi import HTTPException
        with pytest.raises(HTTPException):
            await service.get_{domain}(session, created_{domain}.id)
```

---

## 좋은 테스트 vs 나쁜 테스트

```python
# ✅ 좋은 테스트 - Given/When/Then 명확
async def test_사용자_생성_성공(client, user_data):
    """
    Given: 유효한 사용자 정보
    When: POST /users
    Then: 201, status=SUCCESS
    """
    response = await client.post("/users", json=user_data)
    assert response.status_code == 201
    assert response.json()["status"] == "SUCCESS"

# ❌ 나쁜 테스트 - 의도 불명확
async def test_1(client):
    response = await client.post("/users")
    assert response  # 뭘 테스트하는지 불명확
```
