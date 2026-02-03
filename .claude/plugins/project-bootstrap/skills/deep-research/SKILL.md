---
name: deep-research
description: 심층 기술 리서치 - 병렬 웹 검색 및 종합 분석
model: sonnet
user-invocable: true
context: fork
agent: Explore
argument-hint: [technology-name]
---

# Skill: Deep Research

**템플릿 파일**: [templates/report.md](./templates/report.md) - 종합 리포트 템플릿

---

## 목적

특정 기술/라이브러리에 대한 **심층 학습** 및 **완전한 이해**

---

## 언제 사용하는가?

### ✅ 사용해야 할 때
- 새로운 기술 스택 도입 전 **완전한 이해** 필요
- Phase 0에서 비교표만으론 부족할 때
- 팀원들에게 설명해야 할 때 (문서화 필요)
- 아키텍처 결정에 영향을 미치는 중요한 기술

### ❌ 사용하지 말아야 할 때
- 이미 잘 아는 기술
- 빠른 프로토타이핑 (phase-1-researcher로 충분)
- 단순 비교만 필요할 때

---

## phase-1-researcher vs deep-research

| 항목          | phase-1-researcher | deep-research         |
| ------------- | ------------------ | --------------------- |
| **목적**      | 빠른 결정          | 깊은 학습             |
| **시간**      | 3-5분              | 10-15분               |
| **검색 범위** | 커뮤니티 의견      | 공식 문서 + 튜토리얼  |
| **출력**      | 비교표 + 추천      | 종합 리포트 (10-20pg) |
| **저장 위치** | SESSION.md         | `research/tech/*.md`  |

---

## 검색 전략 (병렬 6-Way)

### 1. Official Documentation
```
"[기술명] official documentation 2026"
"[기술명] getting started guide"
```

### 2. GitHub Ecosystem
```
"[기술명] GitHub repository"
"[기술명] awesome list"
```

### 3. Tutorial & Guides
```
"[기술명] tutorial 2025 2026"
"[기술명] best practices 2026"
```

### 4. Stack Overflow & Forums
```
"site:stackoverflow.com [기술명] 2025"
"[기술명] common issues"
```

### 5. Recent Articles & Blogs
```
"[기술명] blog 2025 2026"
"[기술명] production experience"
```

### 6. Comparison & Reviews
```
"[기술명] pros and cons 2026"
"[기술명] vs [대안] comparison"
```

---

## 실행 단계

### Step 1: 검색 쿼리 생성
사용자 요청에서 기술명 추출 → 6개 카테고리 쿼리 생성

### Step 2: 병렬 검색 실행
6개 쿼리 동시 실행 (web_search)

### Step 3: 중요 페이지 Deep Dive
각 카테고리 상위 2-3개 페이지 web_fetch

### Step 4: 종합 리포트 생성
**템플릿:** [templates/report.md](./templates/report.md) 참조

### Step 5: 파일 저장
```
research/tech/YYYY-MM-DD-[기술명].md
```

---

## 출력

1. **종합 리포트** (10-20페이지 Markdown)
2. **SESSION.md 요약 추가** (결정 사항만)
3. **다음 단계 안내**

---

## 트리거 문구

- "심층 조사해줘"
- "자세히 알려줘"
- "deep research"
- "[기술명]에 대해 완전히 이해하고 싶어"

---

## 주의사항

- **시간 소요**: 10-15분 (빠른 결정엔 phase-1-researcher 사용)
- **최신 정보**: 2025-2026년 정보 우선
- **저장 필수**: 영구 보관 (research/tech/)
- **SESSION.md**: 결정 사항만 간략히 추가

---

## Integration

```
Phase 0: 외부 라이브러리 선택
  ↓
phase-1-researcher (빠른 비교)
  ↓
"더 자세히 알고 싶어" → deep-research
  ↓
종합 리포트 읽고 최종 결정
  ↓
SESSION.md에 기록
```
