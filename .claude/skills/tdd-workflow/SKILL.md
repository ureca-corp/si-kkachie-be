---
name: tdd-workflow
description: 테스트 주도 개발 워크플로우 - 테스트 먼저, 코드 나중 (Phase 4 코드 생성 시 자동 적용)
user-invocable: false
---

# TDD Workflow Skill

> 테스트 주도 개발 워크플로우 - "테스트 먼저, 코드 나중"

**상세 코드 예제**: [examples.md](./examples.md) 참조

---

## 트리거 조건

- 새 기능 구현 요청
- 버그 수정 요청
- 리팩토링 요청
- Phase 4 코드 생성 시

---

## 테스트 환경

> 테스트는 **실제 DB(PostgreSQL)가 아닌 로컬 SQLite**에서 실행.
> 외부 트래픽 없이 빠르고 독립적인 테스트 보장.

- **인메모리 SQLite**: `sqlite://`
- **conftest.py 설정**: [examples.md](./examples.md#conftestpy-설정) 참조
- **호환성 주의**: UUID, ARRAY, JSON 처리 ([examples.md](./examples.md#sqlite--postgresql-호환성) 참조)

---

## TDD 사이클 (Red → Green → Refactor)

```
1. RED    - 실패하는 테스트 작성
2. GREEN  - 테스트 통과하는 최소 코드 작성
3. REFACTOR - 코드 개선 (테스트 유지)
```

---

## 워크플로우 단계

| Step | 단계 | 설명 |
|------|------|------|
| 1 | 테스트 케이스 설계 | SPEC.md에서 테스트 케이스 도출 |
| 2 | 테스트 실행 (RED) | `pytest` → FAILED (구현 전이므로) |
| 3 | 최소 구현 (GREEN) | 테스트 통과하는 **최소한의 코드만** 작성 |
| 4 | 테스트 실행 (GREEN) | `pytest` → PASSED |
| 5 | 리팩토링 (REFACTOR) | 코드 품질 개선 (중복 제거, 네이밍 개선) |
| 6 | 커버리지 검증 | `pytest --cov` → 100% 목표 |

---

## 테스트 체크리스트

### 생성 (POST)
- [ ] 정상 생성 → 201
- [ ] 필수 필드 누락 → 400
- [ ] 중복 데이터 → 409
- [ ] 유효성 검증 실패 → 400
- [ ] 인증 없음 → 401 (인증 필요 시)

### 조회 (GET)
- [ ] 존재하는 ID → 200 + 데이터
- [ ] 존재하지 않는 ID → 404
- [ ] 잘못된 ID 형식 → 400

### 목록 (GET)
- [ ] 빈 목록 → 200 + []
- [ ] 페이지네이션 → offset, limit 동작
- [ ] 필터링 → 조건별 필터

### 수정 (PUT/PATCH)
- [ ] 정상 수정 → 200
- [ ] 존재하지 않는 ID → 404
- [ ] 유효성 검증 실패 → 400

### 삭제 (DELETE)
- [ ] 정상 삭제 → 204
- [ ] 존재하지 않는 ID → 404
- [ ] 연관 데이터 있음 → 409 또는 CASCADE

---

## 커버리지 기준

| 항목 | 기준 |
|------|------|
| Line Coverage | **100%** |
| Branch Coverage | **100%** |
| Function Coverage | **100%** |

> TDD를 제대로 따르면 100%는 자연스럽게 달성됨.

---

## 테스트 코드 구조

```
tests/
├── conftest.py              # 공통 픽스처 (DB, Client)
├── factories/               # 테스트 데이터 팩토리
├── fixtures/                # 도메인별 픽스처
├── helpers/                 # 테스트 유틸리티 (assertions, api)
└── modules/                 # 도메인별 테스트 (기능별 파일 분리)
```

**상세 예제**: [examples.md](./examples.md#테스트-클린-아키텍처-예제) 참조

---

## 원칙

1. **한 파일 = 한 기능** - test_create.py, test_get.py 분리
2. **팩토리 패턴** - 테스트 데이터 생성 중앙화
3. **헬퍼 재사용** - API 호출, assertion 추상화
4. **픽스처 계층화** - 공통 → 도메인별 → 테스트별
5. **테스트 독립성** - 각 테스트는 다른 테스트에 의존하지 않음

---

## 금지 사항

1. **구현 먼저, 테스트 나중** - 반드시 테스트 먼저
2. **테스트 없는 PR** - 테스트 미포함 코드 금지
3. **하드코딩 테스트 데이터** - Factory 패턴 사용
4. **외부 의존성 직접 호출** - Mock 또는 로컬 DB 사용
5. **한 파일에 모든 테스트** - 기능별로 분리
6. **실제 DB 사용** - 반드시 SQLite 로컬 DB 사용

---

## 예시 흐름

```
1. test_create_user.py 작성 (RED)
2. pytest → FAILED
3. api/create.py 구현 (GREEN)
4. pytest → PASSED
5. 리팩토링 (네이밍, 개행 등)
6. pytest → PASSED
7. 커버리지 확인 → 100%
8. 다음 테스트로 이동
```
