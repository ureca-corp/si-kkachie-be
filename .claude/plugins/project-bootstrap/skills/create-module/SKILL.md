---
name: create-module
description: 단일 도메인 모듈 생성 (Task tool 병렬 실행용)
user-invocable: false
argument-hint: [domain-name]
---

# Skill: Create Module

**이 스킬은 Task tool 내에서 실행됩니다**

**템플릿 파일** (TDD 순서):
- [templates/test.md](./templates/test.md) - 테스트 코드 템플릿 (먼저!)
- [templates/source.md](./templates/source.md) - 소스 코드 템플릿 (나중)

---

## 역할

- **입력**: 단일 도메인 이름 (예: "routes")
- **읽기**: `docs/specs/{domain}.md` + `docs/specs/_overview.md`
- **출력**: 해당 도메인의 모든 파일 생성 (소스 + 테스트)

---

## 출력 구조 (Vertical Slice)

### 소스 코드

```
src/modules/{domain}/
├── __init__.py           # router 조합
├── {feature1}.py         # 첫 번째 엔드포인트 (DTO + Service + Controller)
├── {feature2}.py         # 두 번째 엔드포인트 (DTO + Service + Controller)
├── _models.py            # 공유: SQLModel 정의
├── _repository.py        # 공유: DB 접근
└── _utils.py             # 공유: 유틸리티 함수 (선택)
```

### 테스트 코드

```
tests/modules/{domain}/
├── __init__.py
├── conftest.py           # 공유 fixture
├── test_{feature1}.py    # 기능별 테스트
└── test_{feature2}.py    # 기능별 테스트
```

---

## 실행 단계 (TDD: Red → Green → Refactor)

### Step 0: SPEC 파일 읽기

```
docs/specs/_overview.md    # 공통 규칙
docs/specs/{domain}.md     # 도메인 전용 스펙
```

---

### Step 1: 테스트 코드 먼저 생성 (RED)

**TDD 원칙: 테스트 먼저, 소스 나중!**

| 파일 | 설명 |
|------|------|
| `conftest.py` | 도메인 픽스처 |
| `test_{feature}.py` | 기능별 테스트 |

```bash
# 테스트 실행 → FAILED 확인 (아직 소스 없음)
pytest tests/modules/{domain}/ -v
```

---

### Step 2: 소스 코드 생성 (GREEN) - Vertical Slice 패턴

**생성 순서 (의존성 순서):**

1. `_models.py` - SQLModel 테이블 정의
2. `_repository.py` - DB 접근 함수
3. `_utils.py` - 유틸리티 함수 (선택)
4. `{feature}.py` - 기능별 파일 (DTO + Service + Controller)
5. `__init__.py` - router 조합

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

## Vertical Slice 패턴

### 각 기능 파일 구조 ({feature}.py)

```python
"""기능 설명

METHOD /endpoint
"""

from fastapi import APIRouter
from pydantic import BaseModel

# ─────────────────────────────────────────────────
# Request/Response DTO
# ─────────────────────────────────────────────────

class SomeRequest(BaseModel): ...
class SomeResponse(BaseModel): ...

# ─────────────────────────────────────────────────
# Service (비즈니스 로직)
# ─────────────────────────────────────────────────

def do_something(...) -> SomeResponse: ...

# ─────────────────────────────────────────────────
# Controller (엔드포인트)
# ─────────────────────────────────────────────────

router = APIRouter()

@router.get("/endpoint")
def endpoint(...): ...
```

### __init__.py 템플릿

```python
"""{domain} 도메인

Vertical Slice 구조:
- {feature1}.py: METHOD /endpoint1
- {feature2}.py: METHOD /endpoint2
"""

from fastapi import APIRouter

from .feature1 import router as feature1_router
from .feature2 import router as feature2_router

router = APIRouter(prefix="/{domain}", tags=["{domain}"])
router.include_router(feature1_router)
router.include_router(feature2_router)
```

---

## 체크리스트

1. 테스트 코드 (먼저!):
- [ ] conftest.py
- [ ] test_{feature}.py (기능별)
- [ ] pytest → FAILED 확인

2. 소스 코드 - Vertical Slice (나중):
- [ ] _models.py (공유)
- [ ] _repository.py (공유)
- [ ] {feature}.py (기능별)
- [ ] __init__.py (router 조합)
- [ ] pytest → PASSED 확인

3. 리팩토링:
- [ ] 코드 품질 개선
- [ ] pytest → 여전히 PASSED

---

## 출력

```
✅ {domain} 모듈 생성 완료 (TDD + Vertical Slice)

[RED] 테스트 먼저 생성:
- tests/modules/{domain}/conftest.py
- tests/modules/{domain}/test_search.py
- tests/modules/{domain}/test_recent.py
→ pytest FAILED ✅ (예상대로)

[GREEN] 소스 코드 생성 (Vertical Slice):
- src/modules/{domain}/__init__.py     (router 조합)
- src/modules/{domain}/_models.py      (공유)
- src/modules/{domain}/_repository.py  (공유)
- src/modules/{domain}/search.py       (POST /search)
- src/modules/{domain}/recent.py       (GET /recent)
→ pytest PASSED ✅

[REFACTOR] 코드 품질 개선:
→ pytest 여전히 PASSED ✅
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
