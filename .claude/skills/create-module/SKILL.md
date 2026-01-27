---
name: create-module
description: 단일 도메인 모듈 생성 (Task tool 병렬 실행용)
user-invocable: false
argument-hint: [domain-name]
---

# Skill: Create Module

**⚠️ 중요: 이 스킬은 Task tool 내에서 실행됩니다**

**템플릿 파일** (TDD 순서):
- [templates/test.md](./templates/test.md) - 테스트 코드 템플릿 (먼저!)
- [templates/source.md](./templates/source.md) - 소스 코드 템플릿 (나중)

---

## 역할

- **입력**: 단일 도메인 이름 (예: "users")
- **읽기**: `docs/specs/{domain}.md` + `docs/specs/_overview.md`
- **출력**: 해당 도메인의 모든 파일 생성 (소스 + 테스트)

---

## 입력 파라미터

```
domain: string (필수)
  예: "users", "orders", "products"
```

---

## 실행 단계 (TDD: Red → Green → Refactor)

### Step 0: SPEC 파일 읽기

```
docs/specs/_overview.md    # 공통 규칙
docs/specs/{domain}.md     # 도메인 전용 스펙
```

**중요:**
- 다른 도메인 SPEC 읽지 않기 (독립성)
- _overview.md는 공통 규칙만

---

### Step 1: 테스트 코드 먼저 생성 (RED)

**⚠️ TDD 원칙: 테스트 먼저, 소스 나중!**

**디렉토리:** `tests/modules/{domain}/`

| 파일 | 설명 | 템플릿 |
|------|------|--------|
| `conftest.py` | 픽스처 | [test.md](./templates/test.md#conftestpy-픽스처) |
| `test_controller.py` | 엔드포인트 테스트 | [test.md](./templates/test.md#test_controllerpy) |
| `test_service.py` | 비즈니스 로직 테스트 | [test.md](./templates/test.md#test_servicepy) |

```bash
# 테스트 실행 → FAILED 확인 (아직 소스 없음)
pytest tests/modules/{domain}/ -v
```

---

### Step 2: 소스 코드 생성 (GREEN) - CSR 패턴

**디렉토리:** `src/modules/{domain}/`

| 파일 | 레이어 | 역할 | 템플릿 |
|------|--------|------|--------|
| `models.py` | Model | SQLModel 테이블 | [source.md](./templates/source.md#modelspy) |
| `entities.py` | DTO | Request/Response | [source.md](./templates/source.md#entitiespy) |
| `repository.py` | Repository | 데이터 접근만 | [source.md](./templates/source.md#repositorypy) |
| `service.py` | Service | 비즈니스 로직 | [source.md](./templates/source.md#servicepy) |
| `controller.py` | Controller | 엔드포인트 | [source.md](./templates/source.md#controllerpy) |

**의존성 방향:**
```
controller.py → service.py → repository.py → models.py
```

```bash
# 테스트 실행 → PASSED 확인
pytest tests/modules/{domain}/ -v
```

---

### Step 3: 리팩토링 (REFACTOR)

테스트 통과 후 코드 품질 개선:
- 중복 제거
- 네이밍 개선
- 구조 정리

```bash
# 리팩토링 후에도 여전히 PASSED
pytest tests/modules/{domain}/ -v
```

---

### Step 4: Hook 자동 실행

각 파일 생성 시:
- `on-file-created.sh` 자동 실행
- Level 0-3 검증

---

### Step 5: 완료 확인

**체크리스트 (TDD + CSR 패턴):**

1️⃣ 테스트 코드 (먼저!):
- [x] conftest.py
- [x] test_controller.py
- [x] test_service.py
- [x] pytest → FAILED 확인

2️⃣ 소스 코드 - CSR (나중):
- [x] models.py (Model)
- [x] entities.py (DTO)
- [x] repository.py (Repository)
- [x] service.py (Service)
- [x] controller.py (Controller)
- [x] pytest → PASSED 확인

3️⃣ 리팩토링:
- [x] 코드 품질 개선
- [x] pytest → 여전히 PASSED

---

## TDD 원칙 (필수!)

1. **테스트 먼저** - 소스 코드 작성 전에 반드시 테스트 먼저
2. **FAILED 확인** - 테스트가 실패하는 것을 확인한 후 구현
3. **최소 구현** - 테스트 통과하는 최소한의 코드만 작성
4. **100% 커버리지** - finalize-implementation에서 검증

---

## 출력

```
✅ {domain} 모듈 생성 완료 (TDD + CSR)

[RED] 테스트 먼저 생성:
- tests/modules/{domain}/conftest.py
- tests/modules/{domain}/test_controller.py
- tests/modules/{domain}/test_service.py
→ pytest FAILED ✅ (예상대로)

[GREEN] 소스 코드 생성 (CSR 패턴):
- src/modules/{domain}/models.py       (Model)
- src/modules/{domain}/entities.py     (DTO)
- src/modules/{domain}/repository.py   (Repository)
- src/modules/{domain}/service.py      (Service)
- src/modules/{domain}/controller.py   (Controller)
→ pytest PASSED ✅

[REFACTOR] 코드 품질 개선:
→ pytest 여전히 PASSED ✅

Hook 검증:
- Level 0: Syntax ✅
- Level 1: Style ✅
- Level 2: Type ✅
- Level 3: Guidelines ✅

테스트 커버리지: 100% ✅
```

---

## 에러 처리

### SPEC 파일 없음

```
❌ docs/specs/{domain}.md 파일이 없습니다!

Phase 2 (write-spec)를 먼저 실행해주세요.
```

### 테스트 누락

```
⚠️ 테스트 파일이 누락되었습니다!

필수:
- tests/modules/{domain}/test_create.py
- tests/modules/{domain}/test_get.py

테스트 없는 코드는 미완성입니다.
```

---

## External Provider 생성 (Strategy Pattern)

외부 서비스 연동 시:

### 디렉토리 구조

```
src/external/{service}/
├── __init__.py          # get_{service}_provider() 팩토리
├── base.py              # I{Service}Provider 인터페이스
└── {impl}_provider.py   # 구현체
```

### 생성 순서

1. **base.py (인터페이스)**
```python
from abc import ABC, abstractmethod

class IPaymentProvider(ABC):
    @abstractmethod
    def create_payment(self, amount: int, order_id: str) -> str:
        """결제 생성 후 결제 ID 반환"""
        ...

    @abstractmethod
    def verify_payment(self, payment_id: str) -> bool:
        """결제 검증"""
        ...
```

2. **{impl}_provider.py (구현체)**
```python
from src.external.payment.base import IPaymentProvider

class TossPaymentProvider(IPaymentProvider):
    def __init__(self, client_key: str, secret_key: str):
        self.client_key = client_key
        self.secret_key = secret_key

    def create_payment(self, amount: int, order_id: str) -> str:
        # 토스페이먼츠 API 호출
        ...
```

3. **__init__.py (팩토리)**
```python
from src.core.config import settings
from src.external.payment.base import IPaymentProvider

_payment_instance: IPaymentProvider | None = None

def get_payment_provider() -> IPaymentProvider | None:
    global _payment_instance

    if settings.PAYMENT_BACKEND is None:
        return None

    if _payment_instance is not None:
        return _payment_instance

    match settings.PAYMENT_BACKEND:
        case "toss":
            from src.external.payment.toss_provider import TossPaymentProvider
            _payment_instance = TossPaymentProvider(
                client_key=settings.TOSS_CLIENT_KEY or "",
                secret_key=settings.TOSS_SECRET_KEY or "",
            )
        case _:
            return None

    return _payment_instance
```

4. **config.py 설정 추가**
5. **.env.example 업데이트**
