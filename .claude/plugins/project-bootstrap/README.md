# Project Bootstrap Plugin

> **Internal Plugin** - 이 플러그인은 si-kkachie-be 프로젝트 전용이며, 퍼블릭 배포용이 아닙니다.

새 프로젝트 초기화를 위한 완전한 워크플로우 (Phase 0-6).

## 개요

이 플러그인은 요구사항 수집부터 실제 구현까지 전체 프로젝트 생성 프로세스를 자동화합니다.

## Phase 순서

| Phase | Agent | 역할 | 완료 조건 |
|-------|-------|------|----------|
| 0 | phase-0-clarifier | 요구사항 명확화 | SESSION.md 생성 |
| 1 | phase-1-researcher | 외부 라이브러리 리서치 | 기술 스택 선택 완료 |
| 2 | phase-2-interviewer | 도메인 상세 인터뷰 | 모든 도메인 5가지 확정 |
| 3 | phase-3-spec-writer | SPEC.md 작성 | SPEC.md + DDD Diagram + 승인 |
| 4 | phase-4-generator | TDD 코드 생성 + 마이그레이션 | 테스트 통과 + DB 적용 |
| 5 | phase-5-reviewer | 코드 검토 | CRITICAL 이슈 0 |
| 6 | phase-6-documenter | API 문서화 | OpenAPI 스펙 검증 완료 |

## 사용 방법

### 전체 프로세스 실행

새 프로젝트를 시작할 때:

```
새 도메인 생성: [간단한 설명]
```

Claude가 자동으로 Phase 0부터 시작하여 순차적으로 진행합니다.

### 개별 Phase 실행

특정 Phase만 실행할 경우:

```
Task(project-bootstrap:phase-3-spec-writer)를 사용하여 SPEC 작성해줘
```

## 포함된 구성요소

### Agents (10개)

- **phase-0-clarifier** - 모호한 요구사항 명확화
- **phase-1-researcher** - 외부 API/라이브러리 리서치
- **phase-2-interviewer** - 도메인별 5가지 질문 인터뷰
- **phase-3-spec-writer** - DDD Class Diagram + SPEC.md 생성
- **phase-4-generator** - TDD 오케스트레이터
- **test-code-generator** - 테스트 코드 생성 (Red)
- **logic-code-generator** - 구현 코드 생성 (Green)
- **phase-5-reviewer** - 코드 품질/보안 검토
- **phase-6-documenter** - API 문서 생성
- **session-wrapper** - 세션 마무리 정리

### Skills (7개)

- **clarify** - 요구사항 구조화
- **interview-requirements** - 도메인 인터뷰
- **write-spec** - SPEC 파일 생성
- **create-module** - 단일 모듈 생성
- **deep-research** - 심층 기술 리서치
- **update-session** - SESSION.md 업데이트
- **finalize-implementation** - 최종 검증

## 핵심 원칙

1. **Phase 순서 준수** - 건너뛰기 금지
2. **SESSION.md 즉시 업데이트** - 결정 직후마다
3. **SPEC.md 없이 코드 생성 금지**
4. **DDD Class Diagram 필수**
5. **TDD 구조적 강제** - test → logic → migration
6. **6단계 검증** - verification-loop 모두 PASS

## 의존성

이 플러그인은 다음 범용 Skills에 의존합니다 (`.claude/skills/`):

- `vertical-slice-rules` - Vertical Slice 패턴
- `naming-conventions` - 네이밍 규칙
- `fastapi-standards` - 코딩 스타일
- `provider-pattern-rules` - Provider 패턴
- `tdd-workflow` - TDD 워크플로우
- `verification-loop` - 6단계 검증
- `security-review` - 보안 검토

이 Skills들은 프로젝트 레벨에 설치되어 있어야 합니다.

## 제한사항

- **프로젝트 전용**: 이 플러그인은 si-kkachie-be 아키텍처에 특화되어 있습니다
- **FastAPI 전용**: Python/FastAPI 프로젝트만 지원
- **로컬 전용**: 퍼블릭 배포 금지

## 라이센스

Internal use only - Not for public distribution
