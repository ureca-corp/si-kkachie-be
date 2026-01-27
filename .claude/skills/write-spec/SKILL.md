---
name: write-spec
description: SESSION.md → 도메인별 SPEC 파일 생성 (병렬 작업 최적화)
user-invocable: false
---

# Skill: Write Spec

**템플릿 파일**:
- [templates/overview.md](./templates/overview.md) - _overview.md 템플릿
- [templates/domain.md](./templates/domain.md) - 도메인별 SPEC 템플릿

---

## 목적

SESSION.md를 기반으로 **도메인별로 분리된 SPEC 파일** 생성

---

## 파일 구조 (병렬 작업 최적화)

### Before (단일 파일)
```
docs/SPEC.md  # 모든 도메인 (비효율)
```

### After (도메인별 분리)
```
docs/specs/
├── _overview.md       # 전체 개요 (공통)
├── users.md          # users 도메인 전용
├── orders.md         # orders 도메인 전용
└── products.md       # products 도메인 전용
```

**장점:**
- Task tool이 자신의 spec 파일만 읽음 (효율 ↑)
- 병렬 작업 시 파일 충돌 없음
- 도메인별 독립적 수정 가능

---

## 실행 단계

### Step 1: SESSION.md 읽기

```
.claude/SESSION.md 전체 읽기
  ↓
도메인 목록 추출
예: users, orders, products
```

---

### Step 2: _overview.md 생성

**위치:** `docs/specs/_overview.md`

**템플릿:** [templates/overview.md](./templates/overview.md) 참조

**내용:**
- 외부 라이브러리 선택 이유
- 공통 규칙 (API 응답, Status 코드, 에러 메시지)
- 도메인 목록 링크
- 디렉토리 구조

---

### Step 3: 도메인별 SPEC 파일 생성

**위치:** `docs/specs/{domain}.md`

**템플릿:** [templates/domain.md](./templates/domain.md) 참조

**내용:**
- 테이블 스키마 (SQL)
- Validation 규칙
- API 명세 (Request/Response)
- 비즈니스 룰
- 테스트 케이스 (필수!)
- 파일 생성 체크리스트

---

### Step 4: 사용자 확인

```
생성된 SPEC 파일:
- docs/specs/_overview.md
- docs/specs/users.md
- docs/specs/orders.md
- docs/specs/products.md

확인 부탁드립니다. 수정이 필요하면 말씀해주세요.
```

---

## 출력

1. **docs/specs/_overview.md** - 전체 개요
2. **docs/specs/{domain}.md** - 도메인별 상세 스펙 (N개)

---

## 주의사항

### 1. 파일 분리 필수
- 단일 SPEC.md 생성 금지
- 반드시 도메인별로 분리

### 2. _overview.md 필수
- 공통 규칙 명시
- 외부 라이브러리 선택 이유
- 도메인 목록 링크

### 3. 테스트 케이스 포함 필수
- 각 SPEC 파일에 테스트 케이스 섹션 필수
- 성공 3개 + 실패 3개 이상
- Phase 4에서 이를 기반으로 테스트 코드 작성

### 4. 독립성 보장
- 각 도메인 SPEC은 독립적
- 다른 도메인 참조 최소화
- 필요 시 _overview.md 참조

---

## 통합

Phase 3에서 자동 실행:

```
Phase 3: SPEC 작성
  ↓
write-spec.md 실행
  ↓
SESSION.md 읽기
  ↓
도메인 3개 발견: users, orders, products
  ↓
생성:
- docs/specs/_overview.md
- docs/specs/users.md (테스트 케이스 포함)
- docs/specs/orders.md (테스트 케이스 포함)
- docs/specs/products.md (테스트 케이스 포함)
  ↓
사용자 확인
```
