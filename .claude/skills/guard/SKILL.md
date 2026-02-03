---
name: guard
description: Vertical Slice 패턴 강제 적용 및 Layer-based 코드 자동 리팩토링. 코드 작성 시 항상 적용되는 아키텍처 규칙. 1 파일 = 1 기능 (DTO + Service + Controller), 공유 로직은 언더스코어 prefix. 기존 layer-based 구조 발견 시 `/guard {domain}` 명령으로 변환.
user-invocable: true
argument-hint: "[domain]"
---

# Guard: Vertical Slice 아키텍처 지킴이

> 처음부터 엄격하게 - Vertical Slice 패턴 강제 적용 및 자동 리팩토링

---

## Part 1: Vertical Slice 패턴 규칙

**항상 적용되는 코드 작성 규칙**

### 핵심 원칙

**1 파일 = 1 기능 = 1 엔드포인트**

모든 기능은 완전히 독립된 단일 파일에 구현:
- DTO (Request/Response)
- Service (비즈니스 로직)
- Controller (엔드포인트)

### 모듈 구조

```
src/modules/{domain}/
├── __init__.py           # router 조합
├── {feature1}.py         # 기능 1 (완전한 Vertical Slice)
├── {feature2}.py         # 기능 2 (완전한 Vertical Slice)
├── _models.py            # 공유: SQLModel 정의
├── _repository.py        # 공유: DB 접근
└── _utils.py             # 공유: 유틸리티 (선택)
```

### 기능 파일 템플릿

각 기능 파일은 이 구조를 엄격히 따름:

```python
"""기능 설명 (한 줄)

METHOD /endpoint
"""

from fastapi import APIRouter
from pydantic import BaseModel

# ─────────────────────────────────────────────────
# Request/Response DTO
# ─────────────────────────────────────────────────

class SomeRequest(BaseModel):
    """요청 데이터"""
    ...

class SomeResponse(BaseModel):
    """응답 데이터"""
    ...

# ─────────────────────────────────────────────────
# Service (비즈니스 로직)
# ─────────────────────────────────────────────────

def do_something(...) -> SomeResponse:
    """비즈니스 로직 구현"""
    ...

# ─────────────────────────────────────────────────
# Controller (엔드포인트)
# ─────────────────────────────────────────────────

router = APIRouter()

@router.get("/endpoint")
def endpoint(...):
    """엔드포인트 핸들러"""
    ...
```

### __init__.py 템플릿

```python
"""{domain} 도메인"""

from fastapi import APIRouter

from .feature1 import router as feature1_router
from .feature2 import router as feature2_router

router = APIRouter(prefix="/{domain}", tags=["{domain}"])
router.include_router(feature1_router)
router.include_router(feature2_router)
```

### 공유 모듈 규칙

언더스코어 prefix로 공유 성격 표시:

| 파일 | 역할 | 예시 |
|------|------|------|
| `_models.py` | SQLModel 테이블 정의 | `class User(SQLModel, table=True): ...` |
| `_repository.py` | DB 접근 함수 | `async def get_user_by_id(...)` |
| `_utils.py` | 유틸리티 함수 | `def format_phone_number(...)` |

### 금지 사항

❌ **Controller/Service 분리 금지**
```python
# ❌ 잘못된 예
modules/users/
├── controllers/
│   └── user_controller.py
└── services/
    └── user_service.py
```

❌ **기능 간 직접 호출 금지**
```python
# ❌ users/create.py에서
from ..orders.create import create_order  # 순환 참조 위험
```

❌ **하나의 파일에 여러 엔드포인트 금지**
```python
# ❌ users/crud.py
@router.post("/users")      # create
@router.get("/users/{id}")  # read
@router.put("/users/{id}")  # update
@router.delete("/users/{id}")  # delete
```

### 올바른 예시

✅ **완전히 독립된 기능 파일들**
```
modules/missions/
├── __init__.py
├── start.py      # POST /missions/start
├── end.py        # POST /missions/end
├── cancel.py     # POST /missions/cancel
├── list.py       # GET /missions
├── _models.py    # Mission 테이블
└── _repository.py  # DB 접근
```

### 테스트 구조

기능 파일과 1:1 매칭:

```
tests/modules/{domain}/
├── conftest.py          # 도메인 전용 픽스처
├── test_{feature1}.py   # feature1.py 테스트
└── test_{feature2}.py   # feature2.py 테스트
```

### 섹션 구분자

가독성을 위해 반드시 사용:

```python
# ─────────────────────────────────────────────────
# Section Name
# ─────────────────────────────────────────────────
```

3개 섹션 필수:
1. Request/Response DTO
2. Service (비즈니스 로직)
3. Controller (엔드포인트)

---

## Part 2: Layer-based 코드 자동 리팩토링

**기존 layer-based 구조를 Vertical Slice로 변환**

### 사용법

```bash
/guard {domain}
```

예시:
- `/guard locations`
- `/guard routes`
- `/guard translations`

### 언제 사용하는가?

기존 코드가 다음과 같은 구조일 때:

```
src/modules/{domain}/
├── controller.py      # N개 엔드포인트
├── service.py         # N개 함수
├── entities.py        # N개 DTO
├── models.py          # SQLModel
└── repository.py      # DB 접근
```

→ Vertical Slice 구조로 자동 변환

### 워크플로우 (6단계)

#### 1단계: 분석 (Analyze)

기존 모듈 구조를 파악하고 분해 계획을 수립.

**실행:**
1. `src/modules/{domain}/` 디렉토리 구조 확인
2. `controller.py` 읽기 → 엔드포인트 목록 추출
3. `service.py` 읽기 → 서비스 함수 목록 추출
4. `entities.py` 읽기 → DTO 클래스 목록 추출
5. `models.py` 읽기 (있으면) → SQLModel 클래스 목록
6. `repository.py` 읽기 (있으면) → DB 접근 함수 목록
7. 기타 파일 (`utils.py`, `parsers.py` 등) 읽기 → 공유 로직 파악

**출력 예시:**
```python
{
    "endpoints": [
        {
            "method": "GET",
            "path": "/locations/reverse-geocode",
            "handler": "reverse_geocode",
            "service_func": "get_reverse_geocode",
            "dtos": ["ReverseGeocodeResponse"],
            "dependencies": ["_parsers.parse_reverse_geocode"]
        }
    ],
    "shared": {
        "models": ["RouteHistory"],
        "repository": ["create", "get_by_profile_id"],
        "utils": ["calculate_distance"]
    }
}
```

상세 가이드: [references/analysis-guide.md](references/analysis-guide.md)

#### 2단계: 계획 (Plan)

분석 결과를 바탕으로 생성할 파일 목록을 작성.

**출력 예시:**
```
생성할 파일:
- reverse_geocode.py (GET /locations/reverse-geocode)
- search.py (GET /locations/search)
- _parsers.py (공유: parse_reverse_geocode, parse_place_item)
- _utils.py (공유: calculate_distance)
- __init__.py (router 조합)

테스트 파일:
- test_reverse_geocode.py
- test_search.py
```

사용자에게 계획을 보여주고 승인 받는다.

#### 3단계: 생성 (Generate)

계획된 파일들을 생성.

**각 기능 파일 생성:**
`assets/feature_template.py` 참조하여:
1. 해당 엔드포인트의 DTO 이동
2. 해당 서비스 함수 이동
3. 해당 컨트롤러 함수 이동
4. Import 정리

**공유 파일 생성:**
- `_models.py`: `assets/shared_models_template.py` 참조
- `_repository.py`: `assets/shared_repository_template.py` 참조
- 기타 공유 로직: 기존 파일 내용 복사

**__init__.py 생성:**
`assets/init_template.py` 참조하여 모든 기능 router 조합

#### 4단계: 테스트 분리 (Split Tests)

기존 `test_controller.py`를 기능별로 분리.

**실행:**
1. `tests/modules/{domain}/test_controller.py` 읽기
2. 각 테스트 클래스/함수가 테스트하는 엔드포인트 식별
3. 기능별 테스트 파일 생성
4. Mock 경로 수정 (예: `src.modules.locations.service.xxx` → `src.modules.locations.search.xxx`)

**템플릿:** `assets/test_template.py`

#### 5단계: 검증 (Validate)

생성된 코드가 올바르게 동작하는지 확인.

**실행 명령:**
```bash
# 1. 테스트
export $(cat .env.test | xargs) && uv run pytest tests/modules/{domain}/ -v

# 2. 타입 체크
uv run ty check src/modules/{domain}/

# 3. 스타일 체크
uv run ruff check src/modules/{domain}/
```

**확인 사항:**
- 모든 테스트 PASS
- 타입 체크 오류 없음
- 스타일 체크 오류 없음
- API 응답 구조 동일 (Breaking change 없음)

문제 발견 시 수정 후 재검증.

#### 6단계: 정리 (Cleanup)

검증 완료 후 기존 파일 삭제.

**실행:**
```bash
# 기존 layer-based 파일 삭제
rm src/modules/{domain}/controller.py
rm src/modules/{domain}/service.py
rm src/modules/{domain}/entities.py
rm tests/modules/{domain}/test_controller.py

# 비어있는 디렉토리 확인
```

---

## 파일 구조 상세

상세 규칙: [references/file-structure.md](references/file-structure.md)

**Before (Layer-based):**
```
src/modules/{domain}/
├── __init__.py
├── controller.py      # N개 엔드포인트
├── service.py         # N개 함수
├── entities.py        # N개 DTO
├── models.py          # SQLModel
└── repository.py      # DB 접근
```

**After (Vertical Slice):**
```
src/modules/{domain}/
├── __init__.py           # router 조합
├── {feature1}.py         # 1 엔드포인트 (DTO + Service + Controller)
├── {feature2}.py         # 1 엔드포인트 (DTO + Service + Controller)
├── _models.py            # 공유: SQLModel
├── _repository.py        # 공유: DB 접근
└── _utils.py             # 공유: 유틸리티
```

---

## 템플릿 파일

모든 템플릿은 `assets/` 디렉토리 참조:

- `feature_template.py` - 기능 파일 (DTO + Service + Controller)
- `init_template.py` - __init__.py (router 조합)
- `shared_models_template.py` - _models.py
- `shared_repository_template.py` - _repository.py
- `test_template.py` - 테스트 파일

---

## 주의사항

1. **기존 코드 백업 불필요** - Git으로 관리되므로 롤백 가능
2. **단계별 검증** - 각 단계 완료 후 확인
3. **Breaking change 금지** - API 응답 구조 변경 금지
4. **Mock 경로 수정 필수** - 테스트에서 import 경로 변경 필수
5. **처음부터 올바르게** - 새 코드는 항상 Vertical Slice로 작성
