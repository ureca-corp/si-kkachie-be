---
name: security-review
description: FastAPI/Python 보안 검토 체크리스트 (인증, SQL 인젝션, XSS 등)
user-invocable: false
---

# Security Review Skill

> FastAPI/Python 보안 검토 체크리스트

---

## 트리거 조건

- 인증/인가 코드 작성 시
- 사용자 입력 처리 시
- 외부 API 연동 시
- 결제/금융 기능 구현 시
- Phase 4 완료 후 (자동)

---

## 보안 검토 영역

### 1. 비밀정보 관리

#### 금지 패턴
```python
# ❌ 하드코딩된 비밀정보
SECRET_KEY = "my-super-secret-key"
DATABASE_URL = "postgresql://user:password@localhost/db"
API_KEY = "sk-1234567890abcdef"
```

#### 올바른 패턴
```python
# ✅ 환경변수 사용
from src.core.config import settings

SECRET_KEY = settings.SECRET_KEY
DATABASE_URL = settings.DATABASE_URL
```

#### 검증 방법
```bash
# 하드코딩된 비밀정보 탐지
grep -rn "password\|secret\|api_key\|token" src/ --include="*.py" | grep -v "settings\."
```

---

### 2. SQL 인젝션 방지

#### 금지 패턴
```python
# ❌ 문자열 포매팅으로 쿼리 생성
query = f"SELECT * FROM users WHERE email = '{email}'"
await session.execute(text(query))
```

#### 올바른 패턴
```python
# ✅ SQLModel/SQLAlchemy 파라미터 바인딩
stmt = select(User).where(User.email == email)
result = await session.exec(stmt)
```

---

### 3. 입력 검증

#### 필수 검증 항목

```python
from pydantic import BaseModel, EmailStr, Field, field_validator
import re

class UserCreateRequest(BaseModel):
    # ✅ 타입 + 제약 조건
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    name: str = Field(min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        # ✅ 특수문자 제한
        if not re.match(r"^[\w\s가-힣]+$", v):
            raise ValueError("이름에 특수문자를 사용할 수 없어요")
        return v.strip()
```

#### 파일 업로드 검증

```python
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

async def validate_upload(file: UploadFile) -> None:
    # ✅ 확장자 검증
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError("허용되지 않는 파일 형식이에요")

    # ✅ 파일 크기 검증
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise ValidationError("파일 크기가 너무 커요 (최대 5MB)")

    # ✅ MIME 타입 검증 (확장자 위조 방지)
    import magic
    mime = magic.from_buffer(content, mime=True)
    if not mime.startswith("image/"):
        raise ValidationError("이미지 파일만 업로드할 수 있어요")
```

---

### 4. 인증/인가

#### JWT 보안 설정

```python
from datetime import datetime, timedelta
from jose import jwt

# ✅ 안전한 JWT 설정
JWT_SETTINGS = {
    "algorithm": "HS256",
    "access_token_expire": timedelta(hours=1),   # 짧은 만료
    "refresh_token_expire": timedelta(days=7),
}

def create_access_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + JWT_SETTINGS["access_token_expire"],
        "iat": datetime.utcnow(),
        "type": "access",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
```

#### 권한 검사

```python
from fastapi import Depends, HTTPException, status

async def require_owner(
    resource_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    """리소스 소유자 검증"""
    resource = await session.get(Resource, resource_id)

    if not resource:
        raise HTTPException(status_code=404)

    # ✅ 소유자 검증
    if resource.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없어요",
        )
```

---

### 5. XSS 방지

#### 출력 이스케이프

```python
from markupsafe import escape

# ✅ 사용자 입력 이스케이프
def safe_output(user_input: str) -> str:
    return escape(user_input)
```

#### 응답 헤더 설정

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# ✅ CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # 명시적 도메인만
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# ✅ 보안 헤더 미들웨어
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response
```

---

### 6. Rate Limiting (권장, 선택)

> 공개 API나 인증 엔드포인트에서 권장. 내부 시스템/MVP는 선택.

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")  # 권장: 로그인 브루트포스 방지
async def login(request: Request, ...):
    ...

@router.post("/")
@limiter.limit("100/hour")  # 선택: 공개 API에서 권장
async def create(...):
    ...
```

**적용 기준:**
| 상황 | Rate Limiting |
|------|---------------|
| 내부 시스템 / 관리자 API | 불필요 |
| MVP / 프로토타입 | 불필요 (나중에 추가) |
| 공개 API / 인증 엔드포인트 | **권장** |
| 결제 / 민감한 작업 | **권장** |

---

### 7. 민감정보 로깅 방지

#### 금지 패턴
```python
# ❌ 비밀번호 로깅
logger.info(f"User login: {email}, password: {password}")

# ❌ 전체 요청 로깅
logger.debug(f"Request: {request.json()}")
```

#### 올바른 패턴
```python
# ✅ 민감정보 마스킹
logger.info(f"User login attempt: {email}")

# ✅ 필요한 정보만 로깅
logger.debug(f"Request path: {request.url.path}")
```

---

### 8. 비밀번호 보안

```python
from passlib.context import CryptContext

# ✅ bcrypt 사용 (느린 해시)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

---

## 보안 검토 체크리스트

### Phase 4 완료 후 필수 검토

| 항목 | 검증 방법 |
|------|----------|
| 하드코딩된 비밀정보 없음 | `grep -rn "password\|secret\|key" src/` |
| SQL 인젝션 방지 | 모든 쿼리가 SQLModel 사용 확인 |
| 입력 검증 | 모든 Request 클래스에 Pydantic 검증 |
| 인증 미들웨어 | 보호 필요 엔드포인트에 Depends 확인 |
| 권한 검사 | 리소스 접근 시 소유자 검증 |
| Rate Limiting | 인증/생성 API에 제한 적용 |
| 에러 메시지 | 내부 정보 노출 없음 확인 |

### 검증 명령어

```bash
# 1. 하드코딩된 비밀정보 검색
grep -rn "password\s*=\s*['\"]" src/ --include="*.py"
grep -rn "secret\s*=\s*['\"]" src/ --include="*.py"
grep -rn "api_key\s*=\s*['\"]" src/ --include="*.py"

# 2. Raw SQL 사용 검색
grep -rn "text(" src/ --include="*.py"
grep -rn "execute(" src/ --include="*.py"

# 3. 로깅 검토
grep -rn "logger\." src/ --include="*.py" | grep -i "password\|token\|secret"
```

---

## 출력 형식

```
## Security Review Report

### 검토 결과: ✅ PASS / ❌ FAIL

| 항목 | 상태 | 비고 |
|------|------|------|
| 비밀정보 관리 | ✅ | 환경변수 사용 |
| SQL 인젝션 | ✅ | SQLModel 사용 |
| 입력 검증 | ✅ | Pydantic 적용 |
| 인증/인가 | ⚠️ | /admin 권한 검사 필요 |
| Rate Limiting | ❌ | 미적용 |

### 조치 필요 항목
1. /admin 엔드포인트에 관리자 권한 검사 추가
2. 로그인 API에 Rate Limiting 적용
```
