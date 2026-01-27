# Finalize Implementation 예제

> SKILL.md에서 참조하는 상세 명령어 및 출력 예제

---

## 테스트 커버리지 명령어

### 현재 커버리지 확인

```bash
pytest --cov=src --cov-report=term-missing --cov-report=html
```

**출력 예시:**
```
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
src/modules/users/models.py          25      0   100%
src/modules/users/repository.py      45      3    93%   89-91
src/modules/orders/api/create.py     32      5    84%   45-49
---------------------------------------------------------------
TOTAL                               450     15    97%
```

### 미커버 부분 테스트 생성 예시

```python
# 예시: users/repository.py의 89-91 라인이 미커버

# Missing code:
def delete_user(user_id: UUID) -> bool:
    """사용자 삭제"""
    # 이 부분이 테스트 안 됨

# → 자동으로 테스트 생성:

async def test_사용자_삭제_성공(session):
    """사용자 삭제 테스트"""
    user = await create_test_user(session)
    result = await delete_user(session, user.id)
    assert result is True

async def test_존재하지않는_사용자_삭제(session):
    """없는 사용자 삭제 시 False 반환"""
    result = await delete_user(session, uuid4())
    assert result is False
```

---

## 린트 & 타입 체크 명령어

### Ruff 검사

```bash
# Check
ruff check src/ tests/

# Format
ruff format src/ tests/

# 에러 자동 수정
ruff check --fix src/ tests/
```

### 타입 체크 (ty/mypy)

```bash
ty check src/
```

**에러 예시:**
```
src/modules/users/api/create.py:25: error:
  Argument 1 has incompatible type "str"; expected "UUID"
```

**수정:**
```python
# Before
user_id = "some-string"

# After
user_id = UUID("some-string")
```

---

## 서버 실행 명령어

### 짧은 서버 실행 테스트 (5초)

```bash
timeout 5 uvicorn src.app.main:app --host 0.0.0.0 --port 8000 || true
```

### 기존 서버 종료

```bash
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
```

### 백그라운드 실행

```bash
nohup uvicorn src.app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --reload \
  > server.log 2>&1 &

echo $! > .server.pid
```

### 서버 상태 확인

```bash
sleep 2

if curl -s http://localhost:8000/docs > /dev/null; then
    echo "✅ 서버가 백그라운드에서 실행 중입니다"
else
    echo "❌ 서버 시작 실패"
    cat server.log
    exit 1
fi
```

---

## OpenAPI 설정 예시

```python
# src/app/main.py에 추가
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="FastAPI AI-Native Template",
        version="1.0.0",
        description="AI 에이전트 친화적 FastAPI 템플릿",
        routes=app.routes,
    )

    app.openapi_schema = openapi_schema
    return openapi_schema

app.openapi = custom_openapi
```

---

## 최종 출력 메시지

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎉 모든 작업이 완료되었습니다!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ✅ 최종 검증 결과

### 테스트 커버리지
- **커버리지**: 100% ✅
- **테스트 파일**: tests/modules/*/
- **HTML 리포트**: htmlcov/index.html

### 린트 & 타입 체크
- **Ruff**: 0 errors ✅
- **Ty**: 0 type errors ✅

### 서버 상태
- **상태**: 실행 중 🟢
- **PID**: 12345
- **로그**: server.log

---

## 📚 API 문서

### Swagger UI (인터랙티브)
🔗 http://localhost:8000/docs

### ReDoc (읽기 전용)
🔗 http://localhost:8000/redoc

### OpenAPI Spec (JSON)
🔗 http://localhost:8000/openapi.json

---

## 🚀 생성된 API 엔드포인트

### 인증
- `POST /auth/login` - 로그인
- `POST /auth/refresh` - 토큰 갱신

### 회원 (users)
- `POST /users` - 회원가입
- `GET /users/{id}` - 회원 조회
- `GET /users` - 회원 목록
- `PUT /users/{id}` - 회원 수정
- `DELETE /users/{id}` - 회원 삭제

### 주문 (orders)
- `POST /orders` - 주문 생성
- `GET /orders/{id}` - 주문 조회
- `GET /orders` - 주문 목록
- `GET /users/{user_id}/orders` - 특정 사용자 주문

---

## 🛠️ 유용한 명령어

### 서버 제어
```bash
# 서버 종료
kill $(cat .server.pid)

# 서버 재시작
kill $(cat .server.pid) && uvicorn src.app.main:app --reload

# 로그 확인
tail -f server.log
```

### 테스트
```bash
# 전체 테스트
pytest

# 커버리지 확인
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### 린트
```bash
# 체크
ruff check src/ tests/

# 자동 수정
ruff check --fix src/ tests/

# 포맷
ruff format src/ tests/
```

---

## 📁 생성된 파일 구조

```
src/
├── core/                        # 앱 내부 프레임워크
│   ├── config.py
│   ├── database/
│   ├── response.py
│   └── exceptions.py
│
├── external/                    # 외부 서비스 연동
│   ├── storage/
│   ├── email/
│   └── payment/
│
├── common/                      # 도메인 간 공유 로직
│   ├── auth/
│   └── pagination/
│
└── modules/                     # 비즈니스 도메인 (CSR 패턴)
    ├── users/
    │   ├── models.py            # Model
    │   ├── entities.py          # DTO
    │   ├── repository.py        # Repository
    │   ├── service.py           # Service
    │   └── controller.py        # Controller
    └── orders/
        └── ...

tests/
├── conftest.py
└── modules/
    ├── users/
    │   ├── test_controller.py   # 엔드포인트 테스트
    │   └── test_service.py      # 비즈니스 로직 테스트
    └── orders/
        └── ...

htmlcov/                         # 커버리지 리포트
server.log                       # 서버 로그
.server.pid                      # 서버 PID
```

---

## 🎯 다음 단계

1. **Swagger 문서 확인**
2. **API 테스트**
3. **프론트엔드 연동**
4. **배포 준비**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 에러 처리 예시

### 커버리지 < 100%

```
⚠️ 테스트 커버리지가 97%입니다.

누락된 부분:
- src/modules/users/service.py: 45-49
- src/modules/orders/controller.py: 32-35

자동으로 테스트를 생성하겠습니다...
[테스트 생성]
✅ 커버리지 100% 달성
```

### 린트 에러

```
❌ Ruff 검사 실패: 3개 에러 발견

자동 수정을 시도하겠습니다...
[ruff check --fix]
✅ 모든 에러 수정 완료
```

### 서버 시작 실패

```
❌ 서버 시작 실패

Error log:
[에러 내용]

문제를 해결하겠습니다...
[str_replace로 수정]
✅ 서버 시작 성공
```
