# FastAPI AI-Native Template

## 시작하기

### 범용 코딩 규칙 (항상 적용)

새 대화 시작 시 자동으로 로드되는 **Skill**:
- `guard` - 모든 코딩 규칙 (Vertical Slice, Provider 패턴, 네이밍, 스타일, TDD, 검증, 보안)

### 새 프로젝트 생성 (project-bootstrap 플러그인)

새 프로젝트/도메인을 생성할 때만 사용:

```
새 도메인 생성: [간단한 설명]
```

Claude가 자동으로 **project-bootstrap 플러그인**의 Phase 0-6을 순차 실행합니다.

> **Note**: project-bootstrap은 플러그인으로 분리되어 있어, 필요할 때만 로드됩니다.

### 프로젝트 문서 (참고용)

1. `docs/PRD.md` - 프로젝트 목표
2. `docs/SPEC.md` - API 스펙 (Phase 3 완료 후 생성)

---

## 세션 상태 확인

| 파일 | 있으면 | 없으면 |
|------|--------|--------|
| `.claude/SESSION.md` | 이어서 진행 (현재 Phase 확인) | Phase 0부터 시작 |
| `docs/SPEC.md` | Phase 4 가능 | Phase 0-3 필요 |

---

## project-bootstrap 플러그인

새 프로젝트 초기화 전용 플러그인 (Phase 0-6).

### Phase 순서

| Phase | Agent | 역할 | 완료 조건 |
|-------|-------|------|----------|
| 0 | `project-bootstrap:phase-0-clarifier` | 요구사항 명확화 | SESSION.md 생성 |
| 1 | `project-bootstrap:phase-1-researcher` | 외부 라이브러리 리서치 | 기술 스택 선택 완료 |
| 2 | `project-bootstrap:phase-2-interviewer` | 도메인 상세 인터뷰 | 모든 도메인 5가지 확정 |
| 3 | `project-bootstrap:phase-3-spec-writer` | SPEC.md 작성 | SPEC.md + DDD Diagram + 승인 |
| 4 | `project-bootstrap:phase-4-generator` | TDD 코드 생성 + 마이그레이션 | 테스트 통과 + DB 적용 |
| 5 | `project-bootstrap:phase-5-reviewer` | 코드 검토 | CRITICAL 이슈 0 |
| 6 | `project-bootstrap:phase-6-documenter` | API 문서화 | OpenAPI 스펙 검증 완료 |

### 흐름

```
사용자 요청
    ↓
Phase 0: 명확화 → SESSION.md 생성
    ↓
Phase 1: 리서치 (외부 연동 있으면) → 기술 스택 선택
    ↓
Phase 2: 인터뷰 → 도메인별 5가지 확정
    ↓
Phase 3: SPEC 작성 (DDD Diagram 필수) → 사용자 승인
    ↓
Phase 4: TDD 코드 생성
    ├─ test-code-generator → 테스트 먼저 (FAILED 확인)
    ├─ logic-code-generator → 구현 나중 (PASSED 확인)
    ├─ run-migration → DB 스키마 적용
    └─ verification-loop 6단계 통과
    ↓
Phase 5: 코드 검토 → CRITICAL 이슈 0
    ↓
Phase 6: API 문서화 → OpenAPI 스펙 검증 완료
    ↓
완료: Git commit
```

### 핵심 원칙

1. **Phase 순서 준수** - 건너뛰기 금지
2. **SESSION.md 즉시 업데이트** - 결정 직후마다
3. **SPEC.md 없이 코드 생성 금지**
4. **DDD Class Diagram 필수** - Phase 3 완료 조건:
   - PK/FK, NOT NULL, UNIQUE, DEFAULT
   - Enum 정의 (모든 값)
   - Entity 관계 (1:1, 1:N, N:M)
   - Cascade 규칙 (ON DELETE/UPDATE)
   - Fetch 전략 (EAGER/LAZY)
   - Orphan Removal
   - Index 전략
5. **Phase 4는 도메인별 병렬 실행** (Task tool)
6. **TDD 구조적 강제** - test-code-generator → logic-code-generator 순차 실행
   - Gate 1: 테스트 FAILED 확인 후 구현 시작
   - Gate 2: 테스트 PASSED 확인 후 마이그레이션 시작
   - Gate 3: 마이그레이션 적용 확인 후 검증 시작
7. **마이그레이션 필수** - 모델 생성/수정 시 Alembic 마이그레이션 실행
8. **6단계 검증** - verification-loop 모두 PASS 필수
9. **보안 검토** - security-review 체크리스트 통과

---

## 프로젝트 구조

### 범용 규칙 (`.claude/skills/`)

항상 로드되어 모든 코드에 적용:

```
.claude/skills/
└── guard/  # 모든 코딩 규칙 (항상 적용)
```

### 플러그인 (`.claude/plugins/`)

특정 목적으로만 사용:

```
.claude/plugins/
└── project-bootstrap/         # 새 프로젝트 생성 (Phase 0-6)
    ├── agents/                # Phase 전용 Agents
    │   ├── phase-0-clarifier.md
    │   ├── phase-1-researcher.md
    │   ├── phase-2-interviewer.md
    │   ├── phase-3-spec-writer.md
    │   ├── phase-4-generator.md
    │   ├── test-code-generator.md
    │   ├── logic-code-generator.md
    │   ├── phase-5-reviewer.md
    │   ├── phase-6-documenter.md
    │   └── session-wrapper.md
    └── skills/                # Phase 전용 Skills
        ├── clarify/
        ├── interview-requirements/
        ├── write-spec/
        ├── create-module/
        ├── deep-research/
        ├── update-session/
        ├── finalize-implementation/
        └── run-migration/
```

### Agents (`.claude/agents/`)

범용 agents:

```
.claude/agents/
└── render-autofix.md  # Render 배포 오류 자동 수정 (통합)
```

---

## External 모듈

```
src/external/
├── maps/           # 지도/경로 (Naver Maps 등)
├── storage/        # 스토리지 (S3, R2, Supabase)
├── speech/         # 음성 처리 (TTS, STT)
└── translation/    # 번역 (Papago, OpenAI 등)
```

### OpenAPI 스펙 파일

외부 API 연동 시 `src/external/{api_name}/docs/`에 OpenAPI JSON 스펙 저장:

- **Phase 1**에서 API 선택 후 공식 스펙 다운로드
- **Phase 4**에서 코드 생성 시 WebFetch 없이 Read로 참조
- 에이전트가 정확한 엔드포인트, 파라미터, 응답 형식 파악 가능

```bash
# 스펙 파일 위치 예시
src/external/maps/docs/naver-maps-api.json       # Naver Maps API
src/external/translation/docs/papago-api.json   # Papago 번역 API
```

---

## 마이그레이션 (Alembic)

모델 생성/수정 후 반드시 실행:

```bash
# 1. 변경 감지
uv run alembic check

# 2. 마이그레이션 파일 생성
uv run alembic revision --autogenerate -m "add user table"

# 3. DB에 적용
uv run alembic upgrade head

# 4. 현재 상태 확인
uv run alembic current
```

**새 모델 추가 시**: `migrations/env.py`에 import 추가 필수

```python
from src.modules.{domain}._models import {Model}  # noqa: F401
```

---

## 예시

```
사용자: "회원, 주문 도메인 만들어줘"

Phase 0 (clarifier):
  - "인증 방식은?" → JWT
  - "결제 포함?" → 예, 토스페이먼츠
  → SESSION.md 생성

Phase 1 (researcher):
  - JWT vs Firebase 비교
  - Toss vs Stripe 비교
  → 사용자 선택

Phase 2 (interviewer):
  - users 도메인 5가지 질문
  - orders 도메인 5가지 질문
  → SESSION.md 완성

Phase 3 (spec-writer):
  - DDD Class Diagram 생성 (PK/FK, Enum, Cascade, Fetch)
  - SPEC.md 생성
  → 사용자 승인

Phase 4 (generator - TDD + Migration):
  test-code-generator:
    - Task(users 테스트) + Task(orders 테스트) 병렬
    - pytest → FAILED 확인 (Gate 1)
  logic-code-generator:
    - Task(users 구현) + Task(orders 구현) 병렬
    - pytest → PASSED 확인 (Gate 2)
  run-migration:
    - alembic revision --autogenerate
    - alembic upgrade head (Gate 3)
  verification-loop:
    - Syntax → Style → Type → Guidelines → Test → Security

Phase 5 (reviewer):
  - 코드 품질 검토
  - 보안 취약점 검토
  → CRITICAL 0 확인

Phase 6 (documenter):
  - API 엔드포인트 수집
  - OpenAPI 스펙 검증
  - 엔드포인트 문서 확인
  → OpenAPI 스펙 검증 완료

완료: Git commit
```
