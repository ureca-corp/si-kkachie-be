---
name: clarify
description: 모호한 요구사항을 구조화된 질문으로 명확화
user-invocable: true
---

# Clarify

Transform vague or ambiguous requirements into precise, actionable specifications through iterative questioning.

## Purpose

When requirements are unclear, incomplete, or open to multiple interpretations, use structured questioning to extract the user's true intent before any implementation begins.

## Protocol

### Phase 1: Capture Original Requirement

Record the original requirement exactly as stated:

```markdown
## Original Requirement
"{user's original request verbatim}"
```

Identify ambiguities:
- What is unclear or underspecified?
- What assumptions would need to be made?
- What decisions are left to interpretation?

### Phase 2: Iterative Clarification

Use AskUserQuestion tool to resolve each ambiguity. Continue until ALL aspects are clear.

**Question Design Principles:**
- **Specific over general**: Ask about concrete details, not abstract preferences
- **Options over open-ended**: Provide 2-4 choices (recognition > recall)
- **One concern at a time**: Avoid bundling multiple questions
- **Neutral framing**: Present options without bias

**Loop Structure:**
```
while ambiguities_remain:
    identify_most_critical_ambiguity()
    ask_clarifying_question()  # Use AskUserQuestion tool
    update_requirement_understanding()
    check_for_new_ambiguities()
```

**AskUserQuestion Format:**
```
question: "What authentication method should be used?"
options:
  - label: "Username/Password"
    description: "Traditional email/password login"
  - label: "OAuth"
    description: "Google, GitHub, etc. social login"
  - label: "Magic Link"
    description: "Passwordless email link"
```

### Phase 3: Before/After Comparison

After clarification is complete, present the transformation:

```markdown
## Requirement Clarification Summary

### Before (Original)
"{original request verbatim}"

### After (Clarified)
**Goal**: [precise description of what user wants]
**Scope**: [what's included and excluded]
**Constraints**: [limitations, requirements, preferences]
**Success Criteria**: [how to know when done]

**Decisions Made**:
| Question | Decision |
|----------|----------|
| [ambiguity 1] | [chosen option] |
| [ambiguity 2] | [chosen option] |
```

### Phase 4: Save Option

Ask if the user wants to save the clarified requirement:

```
AskUserQuestion:
question: "Save this requirement specification to a file?"
options:
  - label: "Yes, save to file"
    description: "Save to requirements/ directory"
  - label: "No, proceed"
    description: "Continue without saving"
```

If saving:
- Default location: `requirements/` or project-appropriate directory
- Filename: descriptive, based on requirement topic (e.g., `auth-feature-requirements.md`)
- Format: Markdown with Before/After structure

## Ambiguity Categories

Common types to probe:

| Category | Example Questions |
|----------|------------------|
| **Scope** | What's included? What's explicitly out? |
| **Behavior** | Edge cases? Error scenarios? |
| **Interface** | Who/what interacts? How? |
| **Data** | Inputs? Outputs? Format? |
| **Constraints** | Performance? Compatibility? |
| **Priority** | Must-have vs nice-to-have? |

## Examples

### Example 1: Vague Feature Request

**Original**: "Add a login feature"

**Clarifying questions (via AskUserQuestion)**:
1. Authentication method? → Username/Password
2. Registration included? → Yes, self-signup
3. Session duration? → 24 hours
4. Password requirements? → Min 8 chars, mixed case

**Clarified**:
- Goal: Add username/password login with self-registration
- Scope: Login, logout, registration, password reset
- Constraints: 24h session, bcrypt, rate limit 5 attempts
- Success: User can register, login, logout, reset password

### Example 2: Bug Report

**Original**: "The export is broken"

**Clarifying questions**:
1. Which export? → CSV
2. What happens? → Empty file
3. When did it start? → After v2.1 update
4. Steps to reproduce? → Export any report

**Clarified**:
- Goal: Fix CSV export producing empty files
- Scope: CSV only, other formats work
- Constraint: Regression from v2.1
- Success: CSV contains correct data matching UI

## Rules

1. **No assumptions**: Ask, don't assume
2. **Preserve intent**: Refine, don't redirect
3. **Minimal questions**: Only what's needed
4. **Respect answers**: Accept user decisions
5. **Track changes**: Always show before/after

---

## Phase 0 워크플로우 통합

이 스킬은 Phase 0 (요구사항 명확화)에서 자동으로 사용됩니다.

### 자동 감지 조건

다음 중 하나라도 해당하면 **즉시 실행**:

- [ ] "기능 만들어줘" 같은 모호한 표현
- [ ] 기술 스택 미언급 (JWT? Firebase? Supabase?)
- [ ] 테이블 스키마 불명확 (필드? 타입? 제약?)
- [ ] API 동작 불명확 (Request? Response? Status?)
- [ ] 비즈니스 룰 불명확 (상태 전이? 권한? 제약?)

### Phase 0 예시

**Before (모호함):**
```
"회원 기능 만들어줘"
```

**After (명확함):**
```
목표: 이메일/비밀번호 기반 회원가입 + 로그인
인증: JWT (Bearer Token, 24시간 유효)
필드: 이메일, 비밀번호(bcrypt), 이름, 프로필 이미지(선택)
제약: 이메일 중복 불가, 비밀번호 최소 8자
소셜: Google OAuth 추가 (선택)
```

### SESSION.md 연동

명확화 완료 후:
1. 명확해진 스펙을 `.claude/SESSION.md`에 기록
2. Phase 1 (interview-requirements)로 자동 진행

```
clarify (완료)
  ↓
interview-requirements (5가지 질문)
  ↓
SESSION.md (완전 정의)
```