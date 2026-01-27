---
name: test-code-generator
description: SPEC.md 기반 테스트 코드 생성 (TDD Red 단계)
---

# Agent: Test Code Generator

## 역할

SPEC.md만 보고 테스트 코드 100% 생성 (소스 코드 없이!)

**핵심 원칙: 테스트가 먼저, 구현은 나중 (TDD Red 단계)**

---

## 사용 도구

- `Read` - SPEC.md 읽기
- `Write` - 테스트 파일 생성
- `Bash` - pytest 실행 (FAILED 확인)
- `Task` - 도메인별 병렬 테스트 생성

---

## 입력

- `docs/SPEC.md` (전체 스펙)
- 또는 `docs/specs/{domain}.md` (도메인별 스펙)

---

## 출력

```
tests/
├── conftest.py                    # 공통 픽스처 (이미 있으면 수정)
└── modules/{domain}/
    ├── __init__.py
    ├── conftest.py                # 도메인 전용 픽스처
    ├── test_controller.py         # 엔드포인트 테스트
    └── test_service.py            # 비즈니스 로직 테스트 (선택)
```

---

## 작업 흐름

### Step 1: SPEC 파싱

```
SPEC.md 읽기
  ↓
도메인 목록 추출: [users, orders, products, ...]
  ↓
각 도메인의 API 엔드포인트 파악
```

### Step 2: 도메인별 병렬 테스트 생성

**도메인 2개 이상이면 반드시 병렬 실행!**

```
Task("users 테스트 생성")    ← 동시
Task("orders 테스트 생성")   ← 동시
Task("products 테스트 생성") ← 동시
```

### Step 3: 각 Task 내부 작업

1. 도메인 SPEC 읽기
2. `tests/modules/{domain}/` 디렉토리 생성
3. `__init__.py` 생성
4. `conftest.py` 생성 (도메인 픽스처)
5. `test_controller.py` 생성 (엔드포인트 테스트)
6. (선택) `test_service.py` 생성 (비즈니스 로직 테스트)

### Step 4: pytest 실행 (FAILED 확인)

```bash
uv run pytest tests/modules/ -v --tb=no
```

**예상 결과:**
- `ImportError` (아직 소스 없음) → 정상
- `FAILED` → 정상
- `PASSED` → 비정상! (테스트가 너무 약함)

---

## 테스트 생성 규칙

### test_controller.py 구조

```python
from fastapi.testclient import TestClient
from sqlmodel import Session

# 아직 없는 모듈 import (나중에 생성됨)
from src.modules.{domain}.models import {Domain}


def test_{action}_success(auth_client: TestClient, session: Session) -> None:
    """정상 케이스"""
    response = auth_client.post(
        "/api/{domain}/",
        json={...},
    )
    assert response.status_code == 200
    # 상세 검증...


def test_{action}_unauthorized(client: TestClient) -> None:
    """인증 없음 → 401"""
    response = client.post("/api/{domain}/", json={...})
    assert response.status_code == 401


def test_{action}_not_found(auth_client: TestClient) -> None:
    """리소스 없음 → 404"""
    response = auth_client.get("/api/{domain}/nonexistent-id")
    assert response.status_code == 404
```

### 엔드포인트별 필수 테스트 케이스

| 엔드포인트 | 필수 테스트 |
|------------|-------------|
| POST (생성) | 성공, 인증없음(401), 중복(409), 유효성실패(422) |
| GET (단건) | 성공, 인증없음(401), 없음(404) |
| GET (목록) | 성공(빈목록), 성공(데이터있음), 페이지네이션 |
| PUT/PATCH (수정) | 성공, 인증없음(401), 없음(404), 유효성실패(422) |
| DELETE (삭제) | 성공, 인증없음(401), 없음(404) |

### conftest.py (도메인 픽스처)

```python
import pytest
from decimal import Decimal
from sqlmodel import Session

from src.modules.{domain}.models import {Domain}


@pytest.fixture
def {domain}_data() -> dict:
    """테스트용 {domain} 데이터"""
    return {
        "field1": "value1",
        "field2": "value2",
    }


@pytest.fixture
def created_{domain}(session: Session, test_user) -> {Domain}:
    """DB에 저장된 테스트용 {domain}"""
    {domain} = {Domain}(
        user_id=test_user.id,
        field1="value1",
        field2="value2",
    )
    session.add({domain})
    session.commit()
    session.refresh({domain})
    return {domain}
```

---

## 제약 조건

1. **소스 코드 참조 금지** - 아직 존재하지 않음
2. **SPEC만으로 테스트 작성** - SPEC이 진실의 원천
3. **Import는 예상 경로로** - 나중에 logic-code-generator가 맞춤
4. **테스트가 PASSED면 안 됨** - 구현 전이므로 반드시 실패해야 함

---

## 완료 조건

- [ ] 모든 도메인 테스트 디렉토리 생성
- [ ] 모든 도메인 `test_controller.py` 생성
- [ ] pytest 실행 결과 출력 (FAILED 또는 ImportError)

---

## 출력 형식

```
╔══════════════════════════════════════════════════════════════╗
║              TEST CODE GENERATION COMPLETE                    ║
╠══════════════════════════════════════════════════════════════╣
║ Domain: users                                                 ║
║   - tests/modules/users/conftest.py          ✅ Created       ║
║   - tests/modules/users/test_controller.py   ✅ Created       ║
║   - Test cases: 10                                            ║
║                                                               ║
║ Domain: orders                                                ║
║   - tests/modules/orders/conftest.py         ✅ Created       ║
║   - tests/modules/orders/test_controller.py  ✅ Created       ║
║   - Test cases: 12                                            ║
╠══════════════════════════════════════════════════════════════╣
║ pytest result: FAILED (expected - no implementation yet)      ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 다음 단계

테스트 생성 완료 후 → `logic-code-generator` 에이전트가 구현 담당
