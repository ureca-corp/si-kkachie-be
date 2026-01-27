---
name: finalize-implementation
description: Phase 3 완료 후 최종 검증 및 서버 시작
user-invocable: false
---

# Skill: Finalize Implementation

**상세 예제**: [examples.md](./examples.md) 참조

---

## 목적

Phase 4 코드 생성 완료 후:
1. 테스트 커버리지 100% 보장
2. 린트 + 서버 실행 오류 없음 확인
3. Swagger 문서 생성
4. 백그라운드 서버 시작
5. 엔드포인트 안내

---

## 실행 시점

**Phase 4 완료 직후, session-wrapper 실행 전**

```
Phase 4: 코드 생성 (병렬)
  ↓
모든 모듈 생성 완료
  ↓
finalize-implementation ← 여기!
  ↓
session-wrapper (/wrap)
```

---

## 실행 단계

### Step 1: 테스트 커버리지 100% 보장

```bash
pytest --cov=src --cov-report=term-missing --cov-report=html
```

**목표:** 100% 달성
- 커버리지 < 100% 발견 시 → 자동으로 테스트 생성
- 예제: [examples.md](./examples.md#테스트-커버리지-명령어) 참조

---

### Step 2: 린트 + 타입 체크

```bash
# Ruff
ruff check src/ tests/
ruff format src/ tests/

# 타입 체크
ty check src/
```

에러 발견 시 자동 수정

---

### Step 3: 서버 실행 테스트

```bash
timeout 5 uvicorn src.app.main:app --host 0.0.0.0 --port 8000 || true
```

에러 체크: ImportError, ValidationError, DatabaseError

---

### Step 4: Swagger 문서 확인

서버 시작 후 자동 제공:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

### Step 5: 백그라운드 서버 시작

```bash
# 기존 서버 종료
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# 백그라운드 실행
nohup uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload > server.log 2>&1 &
echo $! > .server.pid
```

---

### Step 6: 엔드포인트 안내

최종 출력 메시지: [examples.md](./examples.md#최종-출력-메시지) 참조

---

## 주의사항

1. **포트 충돌**: 8000 포트가 이미 사용 중이면 종료 후 시작
2. **커버리지 고집**: 100% 미만이면 절대 넘어가지 않음
3. **린트 무관용**: 단 하나의 에러도 허용 안 함
4. **서버 안정성**: 최소 2초 대기 후 상태 확인

---

## 에러 처리

| 상황 | 대응 |
|------|------|
| 커버리지 < 100% | 자동 테스트 생성 |
| 린트 에러 | `ruff check --fix` |
| 서버 시작 실패 | 로그 분석 후 코드 수정 |

예제: [examples.md](./examples.md#에러-처리-예시) 참조

---

## 통합

```
Phase 4: 코드 생성 (병렬)
  ↓
모든 Task 완료
  ↓
finalize-implementation 자동 실행
  - 테스트 커버리지 100%
  - 린트 + 타입 체크
  - 서버 시작
  - Swagger 생성
  - 엔드포인트 안내
  ↓
session-wrapper (/wrap)
  ↓
완료!
```
