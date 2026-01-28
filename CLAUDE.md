# FastAPI AI-Native Template

## 시작하기

새 대화 시작 시 **반드시** 순서대로 읽기:
1. `docs/GUIDELINES.md` - 코드 작성 규칙
2. `docs/TRD.md` - 기술 아키텍처
3. `docs/PRD.md` - 프로젝트 목표

## 세션 상태 확인

| 파일 | 있으면 | 없으면 |
|------|--------|--------|
| `.claude/SESSION.md` | 이어서 진행 (현재 Phase 확인) | Phase 0부터 시작 |
| `docs/SPEC.md` | Phase 4 가능 | Phase 0-3 필요 |

---

## Phase 순서

사용자가 프로젝트 생성을 요청하면 아래 순서로 Agent 호출:

| Phase | Agent | 역할 | 완료 조건 |
|-------|-------|------|----------|
| 0 | `phase-0-clarifier` | 요구사항 명확화 | 모호함 0, SESSION.md 생성 |
| 1 | `phase-1-researcher` | 외부 라이브러리 리서치 | 기술 스택 선택 완료 |
| 2 | `phase-2-interviewer` | 도메인 상세 인터뷰 | 모든 도메인 5가지 확정 |
| 3 | `phase-3-spec-writer` | SPEC.md 작성 | SPEC.md + **DDD Diagram** + 승인 |
| 4 | `phase-4-generator` | TDD 코드 생성 + 마이그레이션 | 테스트 통과 + DB 적용 |
| 5 | `phase-5-reviewer` | 코드 검토 | CRITICAL 이슈 0 |
| 6 | `phase-6-documenter` | API 문서화 | OpenAPI 스펙 검증 완료 |

**흐름:**
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
    ├─ Step 2: test-code-generator → 테스트 먼저 (FAILED 확인)
    ├─ Step 3: logic-code-generator → 구현 나중 (PASSED 확인)
    ├─ Step 4: run-migration → DB 스키마 적용
    └─ Step 5: verification-loop 6단계 통과
    ↓
Phase 5: 코드 검토 → CRITICAL 이슈 0
    ↓
Phase 6: API 문서화 → OpenAPI 스펙 검증 완료
    ↓
완료: Git commit
```

---

## 핵심 원칙

1. **Phase 순서 준수** - 건너뛰기 금지
2. **SESSION.md 즉시 업데이트** - 결정 직후마다
3. **SPEC.md 없이 코드 생성 금지**
4. **DDD Class Diagram 필수** - Phase 3 완료 조건 (아래 항목 모두 포함):
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

## External 모듈

```
src/external/
├── maps/           # 지도/경로 (Naver Maps 등)
├── storage/        # 스토리지 (S3, R2, Supabase)
├── speech/         # 음성 처리 (TTS, STT)
└── translation/    # 번역 (Papago, OpenAI 등)
```

### OpenAPI 스펙 파일 (docs/)

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

## Agent 위치

```
.claude/agents/
├── phase-0-clarifier.md      # 요구사항 명확화
├── phase-1-researcher.md     # 외부 라이브러리 리서치
├── phase-2-interviewer.md    # 도메인 상세 인터뷰
├── phase-3-spec-writer.md    # SPEC.md 작성
├── phase-4-generator.md      # TDD 오케스트레이터 (test → logic → migration)
│   ├── test-code-generator.md    # 테스트 코드 생성 (Red)
│   └── logic-code-generator.md   # 구현 코드 생성 (Green)
├── phase-5-reviewer.md       # 코드 품질/보안 검토
├── phase-6-documenter.md     # API 문서화
└── session-wrapper.md        # 세션 마무리
```

## Skill 위치

```
.claude/skills/                        # 디렉토리/SKILL.md 구조
├── clarify/SKILL.md                   # 요구사항 명확화 (Phase 0)
├── interview-requirements/SKILL.md    # 도메인 인터뷰 (Phase 2)
├── write-spec/SKILL.md                # SPEC 작성 (Phase 3)
├── create-module/SKILL.md             # 모듈 생성 (Phase 4)
├── tdd-workflow/SKILL.md              # TDD 워크플로우 (Red-Green-Refactor)
├── run-migration/SKILL.md             # Alembic 마이그레이션 (Phase 4)
├── verification-loop/SKILL.md         # 6단계 검증 루프
├── security-review/SKILL.md           # 보안 검토 체크리스트
├── finalize-implementation/SKILL.md   # 최종 검증
├── deep-research/SKILL.md             # 심층 기술 리서치
└── update-session/SKILL.md            # SESSION.md 업데이트
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
from src.modules.{domain}.models import {Model}  # noqa: F401
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
  Step 2: test-code-generator
    - Task(users 테스트) + Task(orders 테스트) 병렬
    - pytest → FAILED 확인 (Gate 1)
  Step 3: logic-code-generator
    - Task(users 구현) + Task(orders 구현) 병렬
    - pytest → PASSED 확인 (Gate 2)
  Step 4: run-migration
    - alembic revision --autogenerate
    - alembic upgrade head (Gate 3)
  Step 5: verification-loop

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
