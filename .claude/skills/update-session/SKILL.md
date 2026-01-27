---
name: update-session
description: Compact Conversation 대비를 위해 중요한 결정 사항을 SESSION.md에 즉시 기록
model: sonnet
user-invocable: false
---
# Skill: update-session

## 목적

Compact Conversation 대비를 위해
중요한 결정 사항을 SESSION.md에 즉시 기록

---

## 업데이트 시점 (필수)

### 자동 업데이트
1. **Phase 전환 시**
   - Phase 0 → 1, 1 → 2, 2 → 3
   
2. **중요 결정 직후**
   - 라이브러리 선택
   - 도메인 관계 확정
   - 비즈니스 룰 확정

3. **사용자 질문 답변 직후**
   - 각 인터뷰 질문마다

---

## 업데이트 방식

### 원칙
- **항상 `str_replace` 사용** (전체 재작성 금지)
- **APPEND 패턴** (기존 내용 뒤에 추가)
- **즉시 업데이트** (답변받자마자)

### APPEND 패턴

```python
# 기존 섹션 찾기
old_str = "### 다음 질문 (진행 예정)"

# 새 내용 + 기존 구분자
new_str = f"""#### Q{n}: {question_title}
- **질문**: "{question}"
- **답변**: "{user_answer}"
- **해석**: {interpretation}
- **시각**: {timestamp()}

### 다음 질문 (진행 예정)"""

# 교체
str_replace(
    path=".claude/SESSION.md",
    old_str=old_str,
    new_str=new_str
)
```

### REPLACE 패턴 (Phase 전환)

```python
str_replace(
    path=".claude/SESSION.md",
    old_str="> Current Phase: Phase 1 - Domain Interview",
    new_str="> Current Phase: Phase 2 - SPEC Writing"
)

str_replace(
    old_str="- Phase 1: 🔄 50%",
    new_str="- Phase 1: ✅ 100%"
)
```

---

## 예시

### 예시 1: 라이브러리 선택 후

```python
# 사용자: "Firebase로 할게"

# SESSION.md 업데이트
str_replace(
    path=".claude/SESSION.md",
    old_str="## ✅ Phase 0: 외부 라이브러리 리서치 (진행 중)",
    new_str="""## ✅ Phase 0: 외부 라이브러리 리서치 (진행 중)

### 인증
- **선택**: Firebase Authentication
- **선택 이유**: 소셜 로그인 즉시 연동
- **대안 검토**: JWT (직접 구현), Supabase (커뮤니티 작음)
- **결정 시각**: 2025-01-17 14:15:00

## ✅ Phase 0: 외부 라이브러리 리서치 (진행 중)"""
)

# 사용자 피드백
print("✅ 인증: Firebase Authentication 선택됨")
```

### 예시 2: 인터뷰 질문 답변 후

```python
# 질문: "회원-주문 관계가 1:N인가요?"
# 답변: "1:N이요"

str_replace(
    path=".claude/SESSION.md",
    old_str="### 다음 질문 (진행 예정)",
    new_str="""#### Q1: 회원-주문 관계
- **질문**: "관계가 1:N인가요, M:N인가요?"
- **답변**: "1:N이요"
- **해석**: users.id ← orders.user_id (FK)
- **시각**: 2025-01-17 14:25:00

### 다음 질문 (진행 예정)"""
)

# 진행률 업데이트
str_replace(
    old_str="- Phase 1: 🔄 0%",
    new_str="- Phase 1: 🔄 10% (1/10 질문)"
)
```

---

## 금지 사항

❌ **전체 재작성**:
```python
# 절대 이렇게 하지 말 것
session = read_file(".claude/SESSION.md")
session += new_content
write_file(".claude/SESSION.md", session)
```

❌ **업데이트 지연**:
```python
# 여러 답변 모아서 한 번에 (X)
# 각 답변마다 즉시 (O)
```

❌ **모호한 old_str**:
```python
# old_str이 파일에 여러 번 나오면 에러
# 반드시 unique한 문자열 사용
```

---

## 템플릿

### 초기 SESSION.md

```markdown
# Session Memory
> Last Updated: {timestamp}
> Status: IN_PROGRESS
> Current Phase: Phase 0 - Library Research

---

## 📋 프로젝트 개요
**사용자 요청**:
```
{user_request}
```

**탐지된 도메인**: {domains}
**탐지된 외부 연동**: {categories}

---

## ✅ Phase 0: 외부 라이브러리 리서치 (진행 중)

(각 결정마다 추가됨)

---

## 🔄 Phase 1: 도메인 인터뷰 (대기 중)

### 완료된 질문

### 다음 질문 (진행 예정)

---

## 📊 진행률
- Phase 0: 🔄 0%
- Phase 1: ⏳ 대기 중
- Phase 2: ⏳ 대기 중
- Phase 3: ⏳ 대기 중

---

## 🎯 다음 액션
1. Phase 0 라이브러리 선택 시작
```

---

## 종료 조건

### SESSION.md → DECISIONS.md 이동

Phase 3 완료 시:

```python
# SESSION.md 읽기
session = read_file(".claude/SESSION.md")

# DECISIONS.md에 추가
decisions = read_file("docs/DECISIONS.md")
decisions += f"\n\n## 프로젝트 생성 ({date})\n\n{session}"
write_file("docs/DECISIONS.md", decisions)

# SESSION.md 삭제
delete_file(".claude/SESSION.md")

print("✅ 모든 결정 사항이 DECISIONS.md에 보관됨")
```
