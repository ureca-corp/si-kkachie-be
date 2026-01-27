---
name: session-wrapper
description: 세션 종료 시 자동 정리 및 문서화
---

# Agent: Session Wrapper

## 역할

Phase 3 완료 후 세션 마무리 및 영구 기록 생성

## 사용 도구

- `Read` - SESSION.md 읽기
- `Write` - DECISIONS.md 생성
- `Bash` - Git commit, 파일 삭제

---

## 실행 조건

Phase 3 완료 감지:
- `src/modules/` 아래 모든 도메인 파일 생성 완료
- 모든 테스트 통과
- on-phase-complete.sh 통과

---

## 작업 흐름

### Step 1: Phase 3 완료 확인

```bash
# 모듈 생성 확인
ls src/modules/

# 테스트 통과 확인
pytest tests/ --tb=short
```

---

### Step 2: 세션 분석

SESSION.md를 읽고 다음 항목 추출:

1. **문서 업데이트 필요 여부**
   - README 수정 필요?
   - API 문서 추가 필요?

2. **자동화 가능한 작업**
   - 반복적인 패턴 발견?
   - 템플릿화 가능?

3. **학습 내용**
   - 기술적 발견
   - 피해야 할 실수

4. **후속 작업**
   - 개선 사항
   - 확장 가능성

---

### Step 3: DECISIONS.md 생성

SESSION.md를 영구 기록으로 변환:

```markdown
# Decision Log

## 프로젝트: [도메인들]
**완료일**: [날짜]

---

## Phase 0: 외부 라이브러리 선택

### 인증: JWT
- 이유: 커스터마이징 자유, 종속성 최소
- 대안 고려: Firebase Auth

---

## Phase 1-2: 도메인 정의

### users 도메인
- 테이블: id, email, password_hash, name, created_at
- API: POST /users, GET /users/{id}
- 비즈니스 룰: 이메일 중복 불가

---

## Phase 3: 구현 결과

### 생성된 파일
- src/modules/users/
- tests/modules/users/

### 검증 통과
- Level 0-4 모두 통과

---

## 학습 및 개선사항

### 배운 점
1. [기술적 발견]

### 후속 작업
1. [개선 사항]
```

---

### Step 4: Git Commit

```bash
git add .
git commit -m "feat: [도메인들] 구현

Phase 0-3 완료:
- 외부 라이브러리 선택
- 도메인 정의
- 코드 생성 및 테스트

Details in docs/DECISIONS.md"
```

---

### Step 5: 세션 정리

```bash
# SESSION.md 삭제 (DECISIONS.md로 이동 완료)
rm .claude/SESSION.md
```

---

## 출력

1. **docs/DECISIONS.md** (영구 기록)
2. **Git commit** (변경사항 저장)
3. **SESSION.md 삭제** (다음 세션 준비)

---

## 주의사항

- **완료 확인**: 모든 Phase 완료 후에만 실행
- **영구 보관**: DECISIONS.md는 삭제 금지
- **세션 초기화**: SESSION.md 삭제로 다음 세션 준비
