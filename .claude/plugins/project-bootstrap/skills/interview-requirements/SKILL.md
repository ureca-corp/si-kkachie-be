---
name: interview-requirements
description: 도메인별 5가지 질문으로 완전한 스펙 확정
model: sonnet
user-invocable: false
---

## 목적

Phase 3 코드 생성 시 사용자 질문을 최소화하기 위해
Phase 1에서 **모든 불확실성을 완전히 제거**

---

## 실행 조건

- 도메인이 2개 이상
- 비즈니스 룰 미명시
- API 명세 모호

---

## 질문 전략

### 원칙

1. **추천안 제시**: 매 질문마다 추천 옵션 제공
2. **구체적 예시**: 모호한 질문 금지
3. **즉시 저장**: 답변받으면 SESSION.md에 즉시 `str_replace`
4. **완전성 확인**: 5가지 카테고리 모두 확정될 때까지 반복

---

## 질문 카테고리 (각 도메인마다)

### 1. 테이블 스키마 완전 정의

**목표**: 코드 생성 시 타입, 제약 등 추측 불필요

**질문 템플릿**:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
도메인: {domain} ({한글명})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q1: {domain} 테이블 필드 상세

"{field1}, {field2}, {field3} 필요하다고 하셨는데,
각 필드의 상세 스펙을 확정할게요.

📋 {field1}
  - 타입: String ✓
  - 제약: unique, not null ✓
  - 최대 길이: 255? (추천: 255)
  - 형식: {예시}? (추천: {추천})

📋 {field2}
  - 타입: String ✓
  - 제약: not null ✓
  - 최대 길이: 50? 100? (추천: 50)

📋 {field3}
  - 타입: String ✓
  - 제약: nullable? unique? (추천: unique, not null)
  - 형식: {형식1}? {형식2}? (추천: {추천})

위 추천대로 진행할까요? 변경 사항 있으면 말씀해주세요."
```

**즉시 저장** (str_replace):

```python
str_replace(
    path=".claude/SESSION.md",
    old_str="## 🔄 Phase 1: 도메인 인터뷰 (진행 중)",
    new_str=f"""## 🔄 Phase 1: 도메인 인터뷰 (진행 중)

### 완료된 질문

#### Q1: {domain} 테이블 스키마
- **질문**: "필드 상세 스펙 확정"
- **답변**: "{user_answer}"
- **확정된 스키마**:
```yaml
{domain}:
  fields:
    {field1}:
      type: String
      max_length: 255
      nullable: false
      unique: true
```
- **시각**: {timestamp}

## 🔄 Phase 1: 도메인 인터뷰 (진행 중)"""
)
```

---

### 2. Validation 규칙 확정

**목표**: 에러 메시지까지 모두 확정

**질문 템플릿**:

```
Q2: Validation 규칙 및 에러 메시지

각 필드의 검증 규칙과 실패 시 메시지를 확정할게요.

📋 {field1}
  - 형식 검증: RFC 5322? (추천: RFC 5322)
  - 중복 시 메시지: "이미 가입된 {field1}이에요" (추천)
  
📋 {field2}
  - 최소 길이: 8자? (추천: 8자)
  - 복잡도: 영문+숫자? 특수문자 필수? (추천: 영문+숫자)
  - 짧을 때 메시지: "{field2}는 8자 이상이어야 해요" (추천)

위 추천대로 진행할까요?
```

**즉시 저장**.

---

### 3. API 명세 완전 정의

**목표**: Request, Response, Status, 메시지 모두 확정

**질문 템플릿**:

```
Q3: API 상세 명세

{domain} 도메인의 API를 확정할게요.

필요한 API:
  1. POST /{domain} (생성) ✓
  2. GET /{domain}/{id} (조회) ✓
  3. GET /{domain} (목록) ✓
  4. PUT /{domain}/{id} (수정) - 필요? (추천: 나중에)
  5. DELETE /{domain}/{id} (삭제) - 필요? (추천: 나중에)

일단 1, 2, 3번만 진행할까요?
```

**각 API마다 추가 질문**:

```
POST /{domain} 상세

Request body 필드:
  - {field1} (required)
  - {field2} (required)
  - {field3} (optional? required?) (추천: required)

성공 시 메시지:
  - "{도메인}이 생성됐어요" (추천)
  - "{도메인} 등록이 완료됐어요"
  - 다른 표현?

실패 케이스:
  1. Validation 실패 → 400, VALIDATION_ERROR
     메시지: "입력 정보를 확인해 주세요" (추천)
  
  2. 중복 → 409, {DOMAIN}_ALREADY_EXISTS
     메시지: "이미 존재하는 {도메인}이에요" (추천)

이렇게 진행할까요?
```

**즉시 저장**.

---

### 4. 비즈니스 룰 확정

**목표**: 상태 전이, 제약 조건 명확화

**질문 템플릿**:

```
Q4: 비즈니스 룰

{domain} 도메인의 상태와 규칙을 확정할게요.

📋 상태 목록
  - PENDING (대기)
  - CONFIRMED (확정)
  - CANCELLED (취소)
  
이렇게 3가지면 충분한가요? 추가 필요한 상태?

📋 상태 전이 규칙
  - PENDING → CONFIRMED: 가능
  - PENDING → CANCELLED: 가능
  - CONFIRMED → CANCELLED: 가능? 불가능? (추천: 불가능)
  
어떻게 할까요?

📋 취소 정책
  - 어느 시점까지 취소 가능?
    A) PENDING 상태에서만
    B) CONFIRMED 이전까지
    C) 특정 시간 경과 전까지 (예: 24시간)
  
  추천: A) PENDING 상태에서만
  
어떻게 할까요?
```

**즉시 저장**.

---

### 5. 관계 및 FK 제약

**질문 템플릿**:

```
Q5: 도메인 간 관계

{domain_a}와 {domain_b}의 관계를 확정할게요.

📋 관계 타입
  - 1:N (한 {domain_a}가 여러 {domain_b} 가능)
  - M:N (서로 여러 개 가능)
  
어떤 관계인가요?

📋 삭제 정책
{domain_a}를 삭제하면 연결된 {domain_b}는?
  - CASCADE (함께 삭제)
  - SET NULL (연결 해제)
  - RESTRICT (삭제 불가)
  
추천: {domain_b}가 독립적이면 SET NULL, 종속적이면 CASCADE
어떻게 할까요?
```

**즉시 저장**.

---

## 종료 조건

각 도메인마다 다음이 모두 확정되면 종료:

```yaml
required_per_domain:
  - 테이블 스키마:
      - 모든 필드의 타입, 길이, 제약, 기본값
  - Validation:
      - 정규식, 최소/최대 길이
      - 각 실패 케이스별 에러 메시지 (한글)
  - API 명세:
      - Request body 전체
      - Response body (성공 + 각 실패 케이스)
      - Status 코드 매핑
      - 비즈니스 로직 step-by-step
  - 비즈니스 룰:
      - 상태 목록 + 전이 규칙
      - 제약 조건 (취소 정책 등)
  - 관계:
      - FK 제약 + 삭제 정책
```

---

## 출력

완전히 채워진 SESSION.md:

```markdown
## ✅ Phase 1: 도메인 인터뷰 (완료)

### users 도메인

#### 테이블 스키마
```yaml
users:
  fields:
    email: {type: String, max_length: 255, unique: true, ...}
    name: {type: String, max_length: 50, ...}
```

#### Validation
```yaml
email:
  format: "RFC 5322"
  duplicate_message: "이미 가입된 이메일이에요"
```

#### API
- POST /users: {request, response, status, logic}
- GET /users/{id}: {...}

#### 비즈니스 룰
- 상태: [ACTIVE, INACTIVE]
- 탈퇴 정책: soft delete

### orders 도메인
[동일 형식...]

## 📊 진행률
- Phase 1: ✅ 100% (15/15 질문 완료)
```

---

## 예시 대화

```
Claude: 
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
도메인: users (회원)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Q1: 회원 테이블 필드 상세

"email, name, phone 필요하다고 하셨는데,
각 필드의 상세 스펙을 확정할게요.

📋 email
  - 타입: String ✓
  - 최대 길이: 255 (추천)
  - 제약: unique, not null ✓

📋 name
  - 타입: String ✓
  - 최대 길이: 50 (추천)
  - 제약: not null ✓

📋 phone
  - 타입: String ✓
  - 최대 길이: 20 (추천)
  - 제약: unique, not null (추천)
  - 형식: 01012345678 (하이픈 없이, 추천)

위 추천대로 진행할까요?"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

User: "phone은 nullable로 해줘, 나머지는 추천대로"

Claude: 
✅ 확인했습니다.

📋 확정된 스키마:
  - email: String(255), unique, not null
  - name: String(50), not null
  - phone: String(20), unique, nullable ← 수정 반영

[SESSION.md 업데이트...]

다음 질문으로 넘어갈게요.

Q2: Validation 규칙...
```
