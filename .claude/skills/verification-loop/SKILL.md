---
name: verification-loop
description: 코드 변경 후 6단계 자동 검증 (Syntax→Style→Type→Guidelines→Test→Security)
user-invocable: true
argument-hint: [file-path]
---

# Verification Loop Skill

> 코드 변경 후 자동 검증 루프

---

## 트리거 조건

- Phase 4 코드 생성 완료 후
- PR 생성 전
- 리팩토링 후
- `/verify` 명령 시

---

## 검증 단계 (8-Level)

```
Level 0: Syntax       → Python 문법 오류
Level 1: Style        → ruff 코드 스타일
Level 2: Type         → ty 타입 체크
Level 3: Guidelines   → GUIDELINES.md 준수
Level 4: Test         → pytest 테스트
Level 5: Security     → 보안 검토
Level 6: Architecture → 순환참조 + 다이어그램
Level 7: External API → 목업 없음 확인 (TODO, return [], return {})
Level 8: Dependencies → external/ 의존 방향 검증
```

---

## 검증 실행

### Level 0: Syntax Check

```bash
# Python 문법 검증
python -m py_compile src/modules/**/*.py

# 결과: SyntaxError 없으면 PASS
```

### Level 1: Style Check (ruff)

```bash
# 스타일 검사
ruff check src/

# 자동 수정
ruff check src/ --fix

# 포맷팅
ruff format src/
```

### Level 2: Type Check (ty)

```bash
# 타입 검사
ty check src/

# 결과 예시:
# Found 0 errors
```

### Level 3: Guidelines Check

GUIDELINES.md 준수 여부 수동 검토:

| 항목 | 검증 |
|------|------|
| 개행 규칙 | 한 줄 80자 이하 |
| 변수명 | 의도 파악 가능 |
| 함수 인자 | 3개 이상이면 개행 |
| Import 순서 | 표준 → 서드파티 → 로컬 |
| 메시지 | 한글 사용자 친화적 |

### Level 4: Test

```bash
# 전체 테스트
pytest tests/ -v

# 커버리지 포함 (100% 필수)
pytest --cov=src --cov-report=term-missing --cov-fail-under=100

# 특정 도메인만
pytest tests/modules/{domain}/ -v
```

### Level 5: Security

security-review 스킬 실행:

```bash
# 하드코딩 비밀정보 검색
grep -rn "password\s*=\s*['\"]" src/ --include="*.py"

# Raw SQL 검색
grep -rn "text(" src/ --include="*.py"
```

### Level 6: Architecture

아키텍처 건전성 및 다이어그램 자동 생성:

```bash
# 전체 실행 (순환참조 체크 + 다이어그램 생성)
./scripts/verify-architecture.sh

# 개별 명령어 (uv run 필수)
uv run pydeps src/ --show-cycles --no-show                                 # 순환참조 체크 (출력 있으면 순환 존재)
uv run pydeps src/ --rankdir TB -o docs/diagrams/module-dependencies.svg   # 모듈 의존성 그래프 (트리 레이아웃)
uv run pyreverse src/ -o mmd -d docs/diagrams/                             # 클래스 다이어그램 (Mermaid)
```

**출력 파일:**
- `docs/diagrams/module-dependencies.svg` - 모듈 의존성 (사람용)
- `docs/diagrams/classes_project.mmd` - 클래스 다이어그램 (AI 에이전트용)
- `docs/diagrams/*_erd.png` - Pydantic 모델 ER (사람용)

---

## 자동 검증 스크립트

```bash
#!/bin/bash
# .claude/hooks/verify-all.sh

echo "=== Level 0: Syntax ==="
python -m py_compile src/**/*.py && echo "✅ PASS" || echo "❌ FAIL"

echo "=== Level 1: Style (ruff) ==="
ruff check src/ && echo "✅ PASS" || echo "❌ FAIL"

echo "=== Level 2: Type (ty) ==="
ty check src/ && echo "✅ PASS" || echo "❌ FAIL"

echo "=== Level 4: Test ==="
pytest tests/ -v && echo "✅ PASS" || echo "❌ FAIL"

echo "=== Level 5: Security ==="
if grep -rn "password\s*=\s*['\"]" src/ --include="*.py" | grep -v "password:" | grep -v "password_hash"; then
    echo "❌ FAIL: 하드코딩된 비밀번호 발견"
else
    echo "✅ PASS"
fi

echo "=== Level 6: Architecture ==="
./scripts/verify-architecture.sh && echo "✅ PASS" || echo "❌ FAIL"
```

---

## 검증 리포트 형식

```
╔══════════════════════════════════════════════════════════════╗
║                    VERIFICATION REPORT                        ║
╠══════════════════════════════════════════════════════════════╣
║ Level 0: Syntax       │ ✅ PASS                              ║
║ Level 1: Style        │ ✅ PASS (0 errors)                   ║
║ Level 2: Type         │ ✅ PASS (0 errors)                   ║
║ Level 3: Guidelines   │ ⚠️  WARN (2 suggestions)             ║
║ Level 4: Test         │ ✅ PASS (42/42, 100% coverage)       ║
║ Level 5: Security     │ ✅ PASS                              ║
║ Level 6: Architecture │ ✅ PASS (순환참조 0, 다이어그램 갱신) ║
╠══════════════════════════════════════════════════════════════╣
║ OVERALL: ✅ READY FOR COMMIT                                  ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 검증 실패 시 조치

### Level 0 실패 (Syntax)

```
원인: Python 문법 오류
조치: 에러 메시지 확인 후 수정
예시: SyntaxError: unexpected EOF while parsing
```

### Level 1 실패 (Style)

```
원인: ruff 규칙 위반
조치: ruff check --fix 자동 수정 또는 수동 수정
예시: E501 line too long (120 > 88 characters)
```

### Level 2 실패 (Type)

```
원인: 타입 불일치
조치: 타입 힌트 수정 또는 타입 캐스팅
예시: Argument of type "str" cannot be assigned to parameter of type "int"
```

### Level 4 실패 (Test)

```
원인: 테스트 실패
조치:
  1. 테스트 코드 확인 (기대값 잘못됨?)
  2. 구현 코드 확인 (버그?)
  3. 픽스처 확인 (설정 오류?)
```

### Level 5 실패 (Security)

```
원인: 보안 취약점 발견
조치: security-review 스킬 참조하여 수정
```

### Level 6 실패 (Architecture)

```
원인: 순환참조 발견
조치:
  1. pydeps src/ --show-cycles 로 순환 경로 확인
  2. 공통 로직 → common/ 으로 추출
  3. 의존 방향 역전 (Dependency Inversion)
예시: users → orders → users
  → orders가 users에 의존하는 부분을 common/으로 분리
```

---

## Level 7: External API 목업 검사 (필수)

**외부 API가 실제로 구현되었는지 검증. 목업/TODO 상태면 FAIL.**

```bash
# 목업/TODO 검사
grep -rn "# TODO" src/external/ --include="*.py"
grep -rn "return \[\]" src/external/ --include="*.py"
grep -rn "return {}" src/external/ --include="*.py"
grep -rn "pass$" src/external/ --include="*.py"
```

### 검사 항목

| 패턴 | 의미 | 조치 |
|------|------|------|
| `# TODO` | 미구현 표시 | 실제 구현 |
| `return []` | 빈 배열 반환 | API 호출 구현 |
| `return {}` | 빈 객체 반환 | API 호출 구현 |
| `pass` 단독 | 빈 함수 | 실제 로직 구현 |

### 자동 검증 스크립트

```bash
#!/bin/bash
# Level 7: External API Mock Check

echo "=== Level 7: External API 목업 검사 ==="

MOCK_COUNT=0

# TODO 검사
TODO_COUNT=$(grep -rn "# TODO" src/external/ --include="*.py" 2>/dev/null | wc -l)
if [ "$TODO_COUNT" -gt 0 ]; then
    echo "⚠️  TODO 발견: $TODO_COUNT개"
    grep -rn "# TODO" src/external/ --include="*.py"
    MOCK_COUNT=$((MOCK_COUNT + TODO_COUNT))
fi

# 빈 반환 검사 (메서드 내부에서)
EMPTY_RETURN=$(grep -rn "return \[\]$\|return {}$" src/external/ --include="*.py" 2>/dev/null | wc -l)
if [ "$EMPTY_RETURN" -gt 0 ]; then
    echo "⚠️  빈 반환 발견: $EMPTY_RETURN개"
    grep -rn "return \[\]$\|return {}$" src/external/ --include="*.py"
    MOCK_COUNT=$((MOCK_COUNT + EMPTY_RETURN))
fi

if [ "$MOCK_COUNT" -gt 0 ]; then
    echo "❌ FAIL: 목업 코드 $MOCK_COUNT개 발견"
    exit 1
else
    echo "✅ PASS: 목업 없음"
fi
```

### 예외 처리

다음 경우는 목업이 허용됨:
- `base.py` 추상 클래스의 `pass`
- 테스트 코드 (`tests/`)
- 선택적 프로바이더 (설정 안 하면 None 반환)

```python
# 허용: 추상 메서드
@abstractmethod
async def search_places(self, ...):
    pass  # OK - 추상 메서드

# 금지: 실제 구현에서 빈 반환
async def search_places(self, ...):
    return []  # FAIL - 목업
```

---

## Level 8: External 의존성 방향 검증

external/ 모듈 사용 시 추가 검증:

```bash
# external/ → core/ 방향만 허용 (역방향 금지)
# core/ → external/ 참조 발견 시 FAIL
```

### 체크리스트

- [ ] external/ 모듈이 core/에만 의존하는지
- [ ] modules/ → external/ 방향 참조인지
- [ ] Provider 인터페이스 구현 완전성
- [ ] config.py에 *_BACKEND 설정 존재
- [ ] .env.example 환경변수 문서화

### 예시

```
✅ 허용:
  src/modules/users/service.py → src/external/auth/__init__.py
  src/external/auth/jwt_provider.py → src/core/config.py

❌ 금지:
  src/core/deps.py → src/external/auth/__init__.py (허용 - deps는 예외)
  src/core/config.py → src/external/auth/base.py (금지!)
```

---

## 지속 검증 모드

장시간 작업 시:

1. **15분마다** 자동 검증 실행
2. **함수/클래스 완성 후** 체크포인트
3. **커밋 전** 전체 검증

```python
# 체크포인트 예시
"""
[Checkpoint] UserRepository 완성
- create_user ✅
- get_by_id ✅
- get_by_email ✅
- update ✅
- delete ✅

검증 결과: Level 0-5 모두 PASS
"""
```

---

## 통합: Phase 4 완료 조건

Phase 4 generator가 완료하려면:

1. ✅ 모든 도메인 코드 생성
2. ✅ 모든 테스트 코드 생성
3. ✅ **verification-loop 7단계 모두 PASS**
4. ✅ **다이어그램 생성 확인** (docs/diagrams/)
5. ✅ 서버 시작 확인
6. ✅ Git commit

```
Phase 4 완료 체크:
[ ] Level 0: Syntax ✅
[ ] Level 1: Style ✅
[ ] Level 2: Type ✅
[ ] Level 3: Guidelines ✅
[ ] Level 4: Test ✅ (warning 0)
[ ] Level 5: Security ✅
[ ] Level 6: Architecture ✅
[ ] 다이어그램 생성 ✅
→ 모두 PASS면 session-wrapper 호출
```

---

## 다이어그램 생성 필수

**작업 완료 시 반드시 `./scripts/verify-architecture.sh` 실행!**

### 생성되는 파일

```
docs/diagrams/
├── module-dependencies.svg    # 모듈 의존성 그래프 (필수)
├── classes_project.mmd        # 클래스 다이어그램 Mermaid (필수)
├── packages_project.mmd       # 패키지 다이어그램 Mermaid (필수)
└── {domain}_erd.png           # 도메인별 ER 다이어그램 (선택)
```

### 검증 방법

```bash
# 다이어그램 생성 확인
ls docs/diagrams/*.svg docs/diagrams/*.mmd

# 파일이 없으면 실행
./scripts/verify-architecture.sh
```

### 실패 시 조치

```
❌ 다이어그램 파일 없음
조치: ./scripts/verify-architecture.sh 실행
```
