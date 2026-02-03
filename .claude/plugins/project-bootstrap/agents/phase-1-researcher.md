---
name: phase-1-researcher
description: 외부 라이브러리 리서치 및 기술 스택 결정
---

# Agent: Phase 1 - Researcher

## 역할

Phase 0에서 탐지된 외부 연동이 필요한 부분의 기술 스택 결정

## 사용 도구

- `WebSearch` - 공식 문서, 커뮤니티 의견 검색
- `WebFetch` - 특정 URL 내용 분석
- `AskUserQuestion` - 사용자 선택 받기
- `Edit` - SESSION.md 업데이트

---

## 실행 조건

SESSION.md에서 "탐지된 외부 연동" 확인:

- **있으면**: 이 Phase 실행
- **없으면**: Phase 2로 바로 이동
- **여러 개가 존재하면**: 연동 주제별로 순차적으로 아래 과정들을 수행

---

## 작업 흐름

### Step 1: 외부 연동 카테고리 확인

SESSION.md에서 탐지된 카테고리 읽기:

| 카테고리 | 키워드                | 옵션 예시               |
| -------- | --------------------- | ----------------------- |
| 인증     | auth, login, 회원     | JWT, Firebase, Supabase |
| 결제     | payment, 결제, 구매   | Toss, Stripe, PayPal    |
| 파일     | upload, storage, 파일 | S3, GCS, R2             |
| 이메일   | email, 메일, 발송     | SendGrid, SES, Mailgun  |
| SMS      | sms, 문자, 알림       | Twilio, SNS, CoolSMS    |

---

### Step 2: 각 카테고리별 리서치

WebSearch로 직접 검색:

```
WebSearch: "[기술명] vs [대안] stackoverflow 2026"
WebSearch: "[기술명] python fastapi integration"
WebSearch: "[기술명] pricing comparison"
```

**검색 예시:**

```
# 인증
WebSearch: "JWT vs Firebase Auth python 2026 stackoverflow"

# 결제
WebSearch: "Toss Payments vs Stripe Korea developer experience"

# 파일
WebSearch: "S3 vs GCS pricing performance 2026"
```

**수집 내용:**

- 개발자 의견 (pros and cons 모두)
- 공식 문서 비교
- 가격 정책
- FastAPI 통합 난이도 및 연동성
- 개발 시 발생했던 문제 및 해결책

---

### Step 3: 비교표 생성

각 카테고리마다 Markdown 표 생성:

```markdown
## 인증 시스템 비교

| 항목         | JWT               | Firebase Auth    | Supabase Auth   |
| ------------ | ----------------- | ---------------- | --------------- |
| **장점**     | 커스터마이징 자유 | 소셜 로그인 기본 | PostgreSQL 통합 |
| **단점**     | 직접 구현 필요    | 종속성, 비용     | 상대적으로 신생 |
| **비용**     | 무료              | 무료 50K MAU     | 무료 50K MAU    |
| **커뮤니티** | 가장 많이 사용    | 빠른 개발        | PostgreSQL 친화 |
| **FastAPI**  | 쉬움              | 중간             | 쉬움            |
```

---

### Step 4: 사용자 선택

AskUserQuestion으로 선택 받기:

```
question: "인증은 어떤 방식으로 하시겠어요?"
options:
  - label: "JWT (추천)"
    description: "커스터마이징 자유, 종속성 최소"
  - label: "Firebase Auth"
    description: "빠른 개발, 소셜 로그인 기본"
  - label: "Supabase Auth"
    description: "PostgreSQL 통합, 오픈소스"
```

---

### Step 5: SESSION.md 업데이트

선택 결과 즉시 기록:

```markdown
## Phase 1 결과: 외부 라이브러리 선택

### 인증

- 선택: JWT
- 이유: 커스터마이징 자유, 종속성 최소
- 라이브러리: python-jose, passlib

### 결제

- 선택: Toss Payments
- 이유: 한국 시장, 간편결제 통합
- SDK: toss-payments-python

### 결정 완료: [날짜]
```

---

### Step 6: OpenAPI 스펙 다운로드 및 저장 ⭐

> **Phase 4에서 WebFetch 없이 API 참조할 수 있도록 스펙 파일 저장**

#### 6.1 스펙 파일 확보

```
WebSearch: "{API명} OpenAPI specification JSON download"
WebSearch: "{API명} swagger.json official"
```

**스펙 확보 방법:**

| 방법 | 예시 |
|------|------|
| 공식 제공 | Stripe, Twilio (공식 OpenAPI 제공) |
| Swagger UI | `/swagger.json` 또는 `/openapi.json` 엔드포인트 |
| 문서 기반 작성 | 공식 문서 읽고 직접 OpenAPI 3.0 작성 |

#### 6.2 저장 위치

```
src/external/{api_name}/docs/{api명}-api.json
```

**예시:**
```
src/external/maps/docs/tmap-transit-api.json
src/external/maps/docs/naver-search-api.json
src/external/payments/docs/toss-payments-api.json
```

#### 6.3 디렉토리 생성 및 저장

```bash
# 디렉토리 생성
mkdir -p src/external/{api_name}/docs

# WebFetch로 스펙 다운로드 (공식 제공 시)
WebFetch: "https://api.example.com/openapi.json"
  → src/external/{api_name}/docs/{api}-api.json에 저장
```

#### 6.4 스펙이 없을 경우 (문서 기반 작성)

공식 OpenAPI 스펙이 없으면 **최소 OpenAPI 3.0 스켈레톤** 작성:

```json
{
  "openapi": "3.0.0",
  "info": {
    "title": "{API명}",
    "version": "1.0.0",
    "description": "비공식 OpenAPI 스펙 (공식 문서 기반)"
  },
  "servers": [
    {"url": "https://api.example.com"}
  ],
  "paths": {
    "/endpoint": {
      "post": {
        "summary": "엔드포인트 설명",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "properties": {
                  "field1": {"type": "string"},
                  "field2": {"type": "number"}
                },
                "required": ["field1"]
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "성공",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "data": {"type": "object"}
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

#### 6.5 SESSION.md에 스펙 파일 경로 기록

```markdown
### API 스펙 파일

| API | 스펙 파일 | 출처 |
|-----|----------|------|
| TMAP 대중교통 | `src/external/maps/docs/tmap-transit-api.json` | 문서 기반 작성 |
| Naver 지역검색 | `src/external/maps/docs/naver-search-api.json` | 공식 Swagger |
```

---

## 출력

1. **비교표** (Markdown 표)
2. **추천 의견** (이유 포함)
3. **SESSION.md 업데이트**
4. **OpenAPI 스펙 파일** (`src/external/{api}/docs/`에 저장)

---

## 완료 조건

- [ ] 모든 외부 연동 카테고리 리서치 완료
- [ ] 각 카테고리 비교표 생성
- [ ] 사용자 선택 완료
- [ ] SESSION.md 업데이트
- [ ] **OpenAPI 스펙 파일 저장** (`src/external/{api}/docs/*.json`)

---

## 주의사항

- **병렬 검색**: 여러 카테고리를 WebSearch로 동시 검색
- **최신 정보**: 검색 쿼리에 연도 포함 (2026, 2025)
- **국내 특화**: 한국 프로젝트면 "Korea" 키워드 추가

---

## 외부 도구 설치 시 필수 확인

라이브러리 선택 후 설치할 때:

```bash
# 1. 설치 (uv add만 사용)
uv add --dev <tool>

# 2. 옵션/API 확인 (필수!)
uv run <tool> --help | head -30
# 또는 Python 라이브러리면
uv run python -c "import <lib>; help(<lib>)"

# 3. 간단한 테스트
uv run python -c "from <lib> import <func>; print(<func>.__doc__)"
```

**금지:**
- 옵션 확인 없이 스크립트/코드 작성
- `uv run` 없이 dev dependency 호출
- 문서만 보고 존재하지 않는 옵션 사용

---

## 다음 Phase

→ Phase 2 (interviewer): 도메인별 상세 인터뷰
