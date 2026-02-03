# 도메인 SPEC 템플릿

> write-spec 스킬에서 참조하는 도메인별 SPEC 템플릿

---

## 기본 템플릿

```markdown
# Domain Spec: {domain}

**도메인명**: {domain}
**설명**: {도메인 설명}

---

## 테이블 스키마

### {domain} 테이블

```sql
CREATE TABLE {domain} (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  {필드1} {타입1} {제약조건1},
  {필드2} {타입2} {제약조건2},
  ...
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**관계:**
```sql
-- 외래키
ALTER TABLE orders ADD CONSTRAINT fk_user
  FOREIGN KEY (user_id) REFERENCES users(id)
  ON DELETE CASCADE;

-- 인덱스
CREATE INDEX idx_{domain}_{field} ON {domain}({field});
```

---

## Validation 규칙

### {필드1}
- **타입**: {타입}
- **제약**: {제약 조건}
- **정규식**: `{regex}`
- **에러 메시지**: "{한글 메시지}"

**예시:**
```python
email: EmailStr
  정규식: ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
  에러: "올바른 이메일 형식이 아니에요"

password: str (8-50자)
  정규식: ^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$
  에러: "비밀번호는 최소 8자, 대소문자와 숫자를 포함해야 해요"
```

---

## API 명세

### POST /{domain} (생성)

**Request:**
```json
{
  "{필드1}": "{값1}",
  "{필드2}": "{값2}"
}
```

**Response (201):**
```json
{
  "status": "SUCCESS",
  "message": "{도메인} 생성이 완료됐어요",
  "data": {
    "id": "uuid",
    "{필드1}": "{값1}",
    "created_at": "2026-01-17T03:00:00Z"
  }
}
```

**Response (400 - Validation):**
```json
{
  "status": "VALIDATION_ERROR",
  "message": "올바른 {필드1} 형식이 아니에요",
  "data": null
}
```

**Response (409 - 중복):**
```json
{
  "status": "{DOMAIN}_ALREADY_EXISTS",
  "message": "이미 존재하는 {도메인}이에요",
  "data": null
}
```

---

### GET /{domain}/{id} (조회)

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "{도메인} 조회가 완료됐어요",
  "data": {
    "id": "uuid",
    ...
  }
}
```

**Response (404):**
```json
{
  "status": "{DOMAIN}_NOT_FOUND",
  "message": "{도메인}을 찾을 수 없어요",
  "data": null
}
```

---

### GET /{domain} (목록)

**Query Parameters:**
- `page`: int (default: 1)
- `size`: int (default: 20, max: 100)
- `sort`: str (default: "-created_at")

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "{도메인} 목록 조회가 완료됐어요",
  "data": {
    "items": [...],
    "total": 150,
    "page": 1,
    "size": 20,
    "pages": 8
  }
}
```

---

## 비즈니스 룰

### 상태 전이 (해당 시)
```
{상태1} → {상태2} → {상태3}
         ↓
      {취소 상태}
```

**전이 규칙:**
- {상태1} → {상태2}: {조건}
- {상태2} → {상태3}: {조건}
- {취소 가능 시점}: {조건}

### 권한
- **생성**: {권한 설명}
- **조회**: {권한 설명}
- **수정**: {권한 설명}
- **삭제**: {권한 설명}

### 제약 조건
1. {제약 조건 1}
2. {제약 조건 2}
3. {제약 조건 3}

---

## 테스트 케이스

**중요: 모든 테스트는 코드와 함께 작성 필수!**

### 성공 케이스

#### 1. 정상 생성
```python
async def test_{domain}_생성_성공(session):
    """정상적인 {domain} 생성"""
    request = Create{Domain}Request(
        {필드1}="{값1}",
        {필드2}="{값2}"
    )

    response = await create_{domain}(request, session)

    assert response.status == Status.SUCCESS
    assert response.data.{필드1} == "{값1}"
```

#### 2. 정상 조회
```python
async def test_{domain}_조회_성공(session):
    """존재하는 {domain} 조회"""
    # Given: {domain} 생성
    {domain} = await create_test_{domain}(session)

    # When: 조회
    response = await get_{domain}(session, {domain}.id)

    # Then: 성공
    assert response.status == Status.SUCCESS
    assert response.data.id == {domain}.id
```

### 실패 케이스

#### 1. Validation 실패
```python
async def test_{domain}_생성_실패_잘못된_형식(session):
    """잘못된 {필드1} 형식으로 생성 시도"""
    request = Create{Domain}Request(
        {필드1}="invalid",
        {필드2}="{값2}"
    )

    response = await create_{domain}(request, session)

    assert response.status == Status.VALIDATION_ERROR
```

#### 2. 중복 생성
```python
async def test_{domain}_생성_실패_중복(session):
    """이미 존재하는 {필드1}로 생성 시도"""
    # Given: {domain} 생성
    await create_test_{domain}(session, {필드1}="{값1}")

    # When: 같은 {필드1}로 재생성
    request = Create{Domain}Request({필드1}="{값1}")
    response = await create_{domain}(request, session)

    # Then: 중복 에러
    assert response.status == Status.{DOMAIN}_ALREADY_EXISTS
```

---

## 파일 생성 체크리스트 (CSR 패턴)

### 소스 코드
- [ ] `src/modules/{domain}/models.py` - Model (테이블)
- [ ] `src/modules/{domain}/entities.py` - DTO (Request/Response)
- [ ] `src/modules/{domain}/repository.py` - Repository (데이터 접근)
- [ ] `src/modules/{domain}/service.py` - Service (비즈니스 로직)
- [ ] `src/modules/{domain}/controller.py` - Controller (엔드포인트)

### 테스트 코드 (필수!)
- [ ] `tests/modules/{domain}/conftest.py` - 픽스처
- [ ] `tests/modules/{domain}/test_controller.py` - 엔드포인트 테스트
- [ ] `tests/modules/{domain}/test_service.py` - 비즈니스 로직 테스트

**테스트 없이 소스만 작성 = 미완성!**
```

---

## 예시: users.md

```markdown
# Domain Spec: users

**도메인명**: users
**설명**: 회원 관리 (가입, 로그인, 프로필)

---

## 테이블 스키마

### users 테이블

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(100) NOT NULL,
  profile_image_url VARCHAR(500) NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
```

---

## Validation 규칙

### email
- **타입**: EmailStr
- **정규식**: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
- **에러**: "올바른 이메일 형식이 아니에요"

### password
- **길이**: 8-50자
- **정규식**: `^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$`
- **에러**: "비밀번호는 최소 8자, 대소문자와 숫자를 포함해야 해요"

(... 나머지 상세 내용)
```
