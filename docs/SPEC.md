# Project Specification

> 생성일: 2026-01-27
> 기반: SESSION.md

---

## 1. 프로젝트 개요

### 목표

**Kkachie** - 외국인 여행자를 위한 실시간 번역 및 미션 가이드 앱 백엔드

- 실시간 음성/텍스트 번역 (한국어 <-> 영어)
- 미션 기반 가이드 (택시, 결제, 체크인)
- 미션 단계별 추천 문장 템플릿 제공
- 경로 안내 (네이버 지도 연동)

### 범위

**포함:**
- 사용자 인증 (Supabase Auth - Google/Apple 소셜 로그인)
- 텍스트/음성 번역 API
- 미션 템플릿 관리 및 진행 상태 추적
- 추천 문장 관리
- 경로 검색 프록시

**제외:**
- 장소 검색 기능 (MVP 이후)
- 결제 기능
- 한/영 외 다국어 지원

### 제약조건

**기술적 제약:**
- Python 3.12+, FastAPI
- Supabase (Auth + PostgreSQL + Storage)
- Google Cloud APIs (Translation, STT, TTS)
- Naver Maps Directions API
- PostGIS 확장 (위치 데이터)

**Supabase 정책:**
- **RPC/RLS 절대 금지** - 반드시 JWT 검증으로만 인증 처리
- auth.users 테이블 직접 수정 금지 - profiles 테이블로 확장
- 이미지 업로드: Storage Bucket + Presigned URL

**비즈니스 제약:**
- 무료 티어 내 운영 (MVP)
- Google Cloud Translation: 월 500,000자
- Google Cloud STT: 월 60분
- Google Cloud TTS: 월 400만자

---

## 2. 개발 환경

### 테스트 환경

```bash
# Supabase Local 실행
supabase start

# 테스트 실행
uv run pytest
```

### 프로덕션 환경

```env
# .env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
GOOGLE_CLOUD_PROJECT=your-project-id

NAVER_CLIENT_ID=your-ncp-client-id
NAVER_CLIENT_SECRET=your-ncp-client-secret
```

---

## 3. 외부 연동

| 카테고리 | 서비스 | 라이브러리 | 용도 |
|---------|--------|-----------|------|
| 인증 | Supabase Auth | `supabase` | 소셜 로그인 (Google/Apple) |
| 번역 | Google Cloud Translation | `google-cloud-translate` | 텍스트 번역 |
| STT | Google Cloud Speech-to-Text | `google-cloud-speech` | 음성 -> 텍스트 |
| TTS | Google Cloud Text-to-Speech | `google-cloud-texttospeech` | 텍스트 -> 음성 |
| 지도 | Naver Maps Directions | `httpx` | 경로 검색 |
| 저장소 | Supabase Storage | `supabase` | 이미지/오디오 파일 |

---

## 4. DDD Class Diagram

> 별도 파일 참조: [DDD_CLASS_DIAGRAM.md](./DDD_CLASS_DIAGRAM.md)
>
> 코드 생성 전 반드시 위 파일을 확인하세요.

---

## 5. 도메인: profiles (사용자)

> **중요**: Supabase auth.users 테이블은 직접 수정하지 않습니다. profiles 테이블로 추가 정보만 관리합니다.

### 5.1 테이블 스키마

```sql
-- UUID v7 함수 필요 (DDD_CLASS_DIAGRAM.md 참조)

CREATE TABLE profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    user_id UUID UNIQUE NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    display_name TEXT,
    preferred_language VARCHAR(2) NOT NULL DEFAULT 'en',
    profile_image_url TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_profile_user_id ON profiles(user_id);
```

### 5.2 Validation 규칙

| 필드 | 규칙 | 에러 메시지 |
|------|------|------------|
| display_name | 길이 2-50자 (입력 시) | "이름은 2자 이상 50자 이하로 입력해주세요" |
| preferred_language | `ko` 또는 `en` | "지원하지 않는 언어에요" |

### 5.3 API 명세

#### POST /auth/verify-token (토큰 검증 + 자동 프로필 생성)

**Headers:**
```
Authorization: Bearer {supabase_access_token}
```

**Response (200 - 기존 회원):**
```json
{
    "status": "SUCCESS",
    "message": "인증에 성공했어요",
    "data": {
        "id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
        "user_id": "auth-user-uuid",
        "email": "user@example.com",
        "display_name": "여행자",
        "preferred_language": "en",
        "profile_image_url": null,
        "is_new_user": false
    }
}
```

**Response (201 - 신규 회원):**
```json
{
    "status": "SUCCESS",
    "message": "회원가입이 완료됐어요",
    "data": {
        "id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
        "user_id": "auth-user-uuid",
        "email": "user@example.com",
        "display_name": null,
        "preferred_language": "en",
        "profile_image_url": null,
        "is_new_user": true
    }
}
```

**Response (401):**
```json
{
    "status": "ERROR_INVALID_TOKEN",
    "message": "유효하지 않은 토큰이에요"
}
```

---

#### GET /users/me (내 정보 조회)

**Headers:**
```
Authorization: Bearer {supabase_access_token}
```

**Response (200):**
```json
{
    "status": "SUCCESS",
    "message": "조회에 성공했어요",
    "data": {
        "id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
        "email": "user@example.com",
        "display_name": "여행자",
        "preferred_language": "en",
        "profile_image_url": "https://storage.supabase.co/...",
        "created_at": "2026-01-27T10:00:00Z"
    }
}
```

---

#### PATCH /users/me (내 정보 수정)

**Headers:**
```
Authorization: Bearer {supabase_access_token}
```

**Request:**
```json
{
    "display_name": "새 이름",
    "preferred_language": "ko"
}
```

**Response (200):**
```json
{
    "status": "SUCCESS",
    "message": "정보가 수정됐어요",
    "data": {
        "id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
        "display_name": "새 이름",
        "preferred_language": "ko",
        "profile_image_url": null
    }
}
```

---

#### POST /users/me/profile-image (프로필 이미지 업로드 URL 발급)

> Supabase Storage Bucket + Presigned URL 방식

**Headers:**
```
Authorization: Bearer {supabase_access_token}
```

**Request:**
```json
{
    "file_name": "profile.jpg",
    "content_type": "image/jpeg"
}
```

**Response (200):**
```json
{
    "status": "SUCCESS",
    "message": "업로드 URL이 발급됐어요",
    "data": {
        "upload_url": "https://storage.supabase.co/.../presigned-url",
        "public_url": "https://storage.supabase.co/.../profile.jpg",
        "expires_in": 3600
    }
}
```

---

#### DELETE /users/me (회원 탈퇴)

**Headers:**
```
Authorization: Bearer {supabase_access_token}
```

**Response (200):**
```json
{
    "status": "SUCCESS",
    "message": "회원 탈퇴가 완료됐어요"
}
```

### 5.4 비즈니스 룰

1. 첫 로그인 시 Supabase Auth 토큰에서 정보 추출하여 profiles 자동 생성
2. email은 auth.users에서 조회 (profiles에 저장하지 않음)
3. preferred_language 기본값은 'en' (영어)
4. 프로필 이미지는 Supabase Storage에 저장, Presigned URL로 업로드
5. 회원 탈퇴 시 CASCADE로 모든 관련 데이터 삭제

### 5.5 테스트 케이스

**성공 케이스:**

| ID | 설명 | 입력 | 기대 결과 |
|----|------|------|----------|
| TC-U-001 | 신규 회원 토큰 검증 | 유효한 Supabase 토큰 (신규) | 201, is_new_user: true |
| TC-U-002 | 기존 회원 토큰 검증 | 유효한 Supabase 토큰 (기존) | 200, is_new_user: false |
| TC-U-003 | 내 정보 조회 | 유효한 토큰 | 200, 프로필 정보 |
| TC-U-004 | 내 정보 수정 | 유효한 display_name | 200, 수정된 정보 |
| TC-U-005 | 프로필 이미지 URL 발급 | 유효한 파일명 | 200, presigned URL |
| TC-U-006 | 회원 탈퇴 | 유효한 토큰 | 200, 삭제 완료 |

**실패 케이스:**

| ID | 설명 | 입력 | 기대 결과 |
|----|------|------|----------|
| TC-U-101 | 만료된 토큰 | 만료된 Supabase 토큰 | 401, ERROR_INVALID_TOKEN |
| TC-U-102 | 토큰 없음 | Authorization 헤더 없음 | 401, ERROR_UNAUTHORIZED |
| TC-U-103 | 잘못된 display_name | 1자 이름 | 400, ERROR_VALIDATION |
| TC-U-104 | 지원하지 않는 언어 | preferred_language: "jp" | 400, ERROR_VALIDATION |

---

## 6. 도메인: translations

### 6.1 테이블 스키마

```sql
CREATE TABLE translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    source_text TEXT NOT NULL,
    translated_text TEXT NOT NULL,
    source_lang VARCHAR(5) NOT NULL,
    target_lang VARCHAR(5) NOT NULL,
    translation_type TEXT NOT NULL,
    mission_progress_id UUID REFERENCES mission_progress(id) ON DELETE SET NULL,
    audio_url TEXT,
    duration_ms INT,
    confidence_score FLOAT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_translation_profile_id ON translations(profile_id);
CREATE INDEX idx_translation_type ON translations(translation_type);
CREATE INDEX idx_translation_created_at ON translations(created_at DESC);
```

### 6.2 Validation 규칙

| 필드 | 규칙 | 에러 메시지 |
|------|------|------------|
| source_text | 비어있지 않음, 최대 5000자 | "번역할 텍스트를 입력해주세요" |
| source_lang | `ko` 또는 `en` | "지원하지 않는 언어에요" |
| target_lang | `ko` 또는 `en` | "지원하지 않는 언어에요" |
| source_lang != target_lang | 다른 언어 | "같은 언어로는 번역할 수 없어요" |

### 6.3 API 명세

#### POST /translate/text (텍스트 번역)

**Headers:**
```
Authorization: Bearer {supabase_access_token}
```

**Request:**
```json
{
    "source_text": "안녕하세요",
    "source_lang": "ko",
    "target_lang": "en",
    "mission_progress_id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx"
}
```

**Response (200):**
```json
{
    "status": "SUCCESS",
    "message": "번역이 완료됐어요",
    "data": {
        "id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
        "source_text": "안녕하세요",
        "translated_text": "Hello",
        "source_lang": "ko",
        "target_lang": "en",
        "translation_type": "text",
        "mission_progress_id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
        "created_at": "2026-01-27T10:00:00Z"
    }
}
```

---

#### POST /translate/voice (음성 번역)

**Headers:**
```
Authorization: Bearer {supabase_access_token}
Content-Type: multipart/form-data
```

**Request:**
```
audio_file: (binary)
source_lang: ko
target_lang: en
mission_progress_id: 018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx (optional)
```

**Response (200):**
```json
{
    "status": "SUCCESS",
    "message": "음성 번역이 완료됐어요",
    "data": {
        "id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
        "source_text": "안녕하세요",
        "translated_text": "Hello",
        "source_lang": "ko",
        "target_lang": "en",
        "translation_type": "voice",
        "audio_url": "https://storage.supabase.co/.../tts/abc123.mp3",
        "duration_ms": 1500,
        "confidence_score": 0.95,
        "created_at": "2026-01-27T10:00:00Z"
    }
}
```

---

#### GET /translations (번역 히스토리 조회)

**Headers:**
```
Authorization: Bearer {supabase_access_token}
```

**Query Parameters:**
- `page`: 페이지 번호 (기본값: 1)
- `limit`: 페이지당 개수 (기본값: 20, 최대: 100)
- `type`: 번역 유형 필터 (`text` | `voice`)
- `mission_progress_id`: 미션별 필터

**Response (200):**
```json
{
    "status": "SUCCESS",
    "message": "조회에 성공했어요",
    "data": {
        "items": [
            {
                "id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
                "source_text": "안녕하세요",
                "translated_text": "Hello",
                "source_lang": "ko",
                "target_lang": "en",
                "translation_type": "text",
                "created_at": "2026-01-27T10:00:00Z"
            }
        ],
        "pagination": {
            "page": 1,
            "limit": 20,
            "total": 45,
            "total_pages": 3
        }
    }
}
```

---

#### DELETE /translations/{id} (번역 기록 삭제)

**Response (200):**
```json
{
    "status": "SUCCESS",
    "message": "번역 기록이 삭제됐어요"
}
```

### 6.4 비즈니스 룰

1. 모든 번역 기록은 영구 저장
2. 음성 번역 시 STT -> 번역 -> TTS 순서로 처리
3. TTS 결과는 Supabase Storage에 저장, audio_url로 반환
4. 다른 사용자의 번역 기록 접근 불가
5. mission_progress_id가 있으면 해당 미션과 연결

### 6.5 테스트 케이스

**성공 케이스:**

| ID | 설명 | 입력 | 기대 결과 |
|----|------|------|----------|
| TC-T-001 | 텍스트 번역 (한->영) | 한국어 텍스트 | 200, 영어 번역 |
| TC-T-002 | 텍스트 번역 (영->한) | 영어 텍스트 | 200, 한국어 번역 |
| TC-T-003 | 음성 번역 | 유효한 오디오 파일 | 200, 번역 + audio_url |
| TC-T-004 | 히스토리 조회 | 유효한 토큰 | 200, 목록 |
| TC-T-005 | 기록 삭제 | 본인 기록 ID | 200, 삭제 완료 |
| TC-T-006 | 대용량 텍스트 번역 | 5000자 텍스트 | 200, 번역 완료 |

**실패 케이스:**

| ID | 설명 | 입력 | 기대 결과 |
|----|------|------|----------|
| TC-T-101 | 빈 텍스트 | source_text: "" | 400, ERROR_VALIDATION |
| TC-T-102 | 같은 언어 번역 | ko -> ko | 400, ERROR_VALIDATION |
| TC-T-103 | 잘못된 오디오 | 손상된 파일 | 400, ERROR_INVALID_AUDIO |
| TC-T-104 | 타인 기록 삭제 | 다른 사용자 ID | 404, ERROR_NOT_FOUND |
| TC-T-105 | 텍스트 길이 초과 | 5001자 이상 | 400, ERROR_VALIDATION |

---

## 7. 도메인: missions

### 7.1 테이블 스키마

```sql
-- 미션 템플릿 (관리자가 관리)
CREATE TABLE mission_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    title_ko TEXT NOT NULL,
    title_en TEXT NOT NULL,
    description_ko TEXT NOT NULL,
    description_en TEXT NOT NULL,
    mission_type TEXT UNIQUE NOT NULL,
    estimated_duration_min INT NOT NULL,
    icon_url TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 미션 단계 (템플릿에 종속)
CREATE TABLE mission_steps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    mission_template_id UUID NOT NULL REFERENCES mission_templates(id) ON DELETE CASCADE,
    step_order INT NOT NULL,
    title_ko TEXT NOT NULL,
    title_en TEXT NOT NULL,
    description_ko TEXT NOT NULL,
    description_en TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(mission_template_id, step_order)
);

-- 사용자별 미션 진행 상태
CREATE TABLE mission_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    mission_template_id UUID NOT NULL REFERENCES mission_templates(id) ON DELETE RESTRICT,
    status TEXT NOT NULL DEFAULT 'not_started',
    result TEXT,
    current_step INT NOT NULL DEFAULT 0,
    started_at TIMESTAMPTZ,
    ended_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 단계별 진행 상태
CREATE TABLE mission_step_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    mission_progress_id UUID NOT NULL REFERENCES mission_progress(id) ON DELETE CASCADE,
    mission_step_id UUID NOT NULL REFERENCES mission_steps(id) ON DELETE RESTRICT,
    is_completed BOOLEAN NOT NULL DEFAULT false,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(mission_progress_id, mission_step_id)
);
```

### 7.2 Enum 값

**MissionType:**
- `taxi` - 택시 이용
- `payment` - 결제
- `checkin` - 체크인

**MissionStatus:**
- `not_started` - 시작 전
- `in_progress` - 진행 중
- `ended` - 종료됨

**MissionResult (종료 시 선택):**
- `resolved` - 해결됨
- `partially_resolved` - 부분 해결
- `unresolved` - 미해결

### 7.3 API 명세

#### GET /missions (미션 목록 조회)

**Response (200):**
```json
{
    "status": "SUCCESS",
    "message": "조회에 성공했어요",
    "data": [
        {
            "id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
            "title": "Taking a Taxi",
            "description": "Learn how to take a taxi in Korea",
            "mission_type": "taxi",
            "estimated_duration_min": 15,
            "icon_url": "https://storage.supabase.co/.../taxi.png",
            "steps_count": 5,
            "user_progress": {
                "status": "in_progress",
                "current_step": 2,
                "started_at": "2026-01-27T09:00:00Z"
            }
        }
    ]
}
```

---

#### GET /missions/{id} (미션 상세 조회)

**Response (200):**
```json
{
    "status": "SUCCESS",
    "message": "조회에 성공했어요",
    "data": {
        "id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
        "title": "Taking a Taxi",
        "description": "Learn how to take a taxi in Korea",
        "mission_type": "taxi",
        "estimated_duration_min": 15,
        "steps": [
            {
                "id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
                "step_order": 1,
                "title": "Hailing a Taxi",
                "description": "How to stop a taxi on the street",
                "is_completed": true,
                "phrases": [
                    {
                        "id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
                        "text_ko": "택시!",
                        "text_en": "Taxi!",
                        "category": "request"
                    }
                ]
            }
        ],
        "user_progress": {
            "id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
            "status": "in_progress",
            "current_step": 2,
            "started_at": "2026-01-27T09:00:00Z"
        }
    }
}
```

---

#### POST /missions/{id}/start (미션 시작)

**Response (201):**
```json
{
    "status": "SUCCESS",
    "message": "미션을 시작했어요",
    "data": {
        "progress_id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
        "mission_id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
        "status": "in_progress",
        "current_step": 1,
        "started_at": "2026-01-27T10:00:00Z"
    }
}
```

---

#### PATCH /missions/{id}/progress (단계 완료 처리)

**Request:**
```json
{
    "step_id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
    "is_completed": true
}
```

**Response (200):**
```json
{
    "status": "SUCCESS",
    "message": "단계를 완료했어요",
    "data": {
        "progress_id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
        "current_step": 2,
        "completed_steps": 1,
        "total_steps": 5
    }
}
```

---

#### POST /missions/{id}/end (미션 종료)

**Request:**
```json
{
    "result": "resolved"
}
```

**Response (200):**
```json
{
    "status": "SUCCESS",
    "message": "미션을 종료했어요",
    "data": {
        "progress_id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
        "status": "ended",
        "result": "resolved",
        "ended_at": "2026-01-27T10:30:00Z",
        "duration_minutes": 30
    }
}
```

### 7.4 비즈니스 룰

1. 미션은 3종류: 택시, 결제, 체크인
2. 미션 시작 시 `in_progress` 상태로 변경
3. 사용자가 "미션 종료" 클릭 시 결과 선택 필수 (resolved/partially_resolved/unresolved)
4. 같은 미션 여러 번 진행 가능 (매번 새 progress 생성)
5. 미션 템플릿 삭제 시 진행 중인 사용자가 있으면 RESTRICT

### 7.5 테스트 케이스

**성공 케이스:**

| ID | 설명 | 입력 | 기대 결과 |
|----|------|------|----------|
| TC-M-001 | 미션 목록 조회 | 유효한 토큰 | 200, 미션 목록 + 진행상태 |
| TC-M-002 | 미션 상세 조회 | 유효한 미션 ID | 200, 단계 목록 포함 |
| TC-M-003 | 미션 시작 | 시작 전 미션 | 201, in_progress |
| TC-M-004 | 단계 완료 | 진행 중인 미션 | 200, current_step 증가 |
| TC-M-005 | 미션 종료 (해결) | result: resolved | 200, ended |
| TC-M-006 | 미션 종료 (부분해결) | result: partially_resolved | 200, ended |
| TC-M-007 | 미션 종료 (미해결) | result: unresolved | 200, ended |

**실패 케이스:**

| ID | 설명 | 입력 | 기대 결과 |
|----|------|------|----------|
| TC-M-101 | 없는 미션 조회 | 존재하지 않는 ID | 404, ERROR_NOT_FOUND |
| TC-M-102 | 이미 시작한 미션 | 진행 중인 미션 시작 | 409, ERROR_MISSION_ALREADY_STARTED |
| TC-M-103 | 시작 전 단계 완료 | not_started 상태 | 400, ERROR_MISSION_NOT_STARTED |
| TC-M-104 | 잘못된 결과값 | result: "invalid" | 400, ERROR_VALIDATION |

---

## 8. 도메인: phrases

### 8.1 테이블 스키마

```sql
CREATE TABLE phrases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    text_ko TEXT NOT NULL,
    text_en TEXT NOT NULL,
    category TEXT NOT NULL,
    usage_count INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE phrase_step_mapping (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    phrase_id UUID NOT NULL REFERENCES phrases(id) ON DELETE CASCADE,
    mission_step_id UUID NOT NULL REFERENCES mission_steps(id) ON DELETE CASCADE,
    display_order INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(phrase_id, mission_step_id)
);
```

### 8.2 Enum 값

**PhraseCategory:**
- `greeting` - 인사
- `request` - 요청
- `confirmation` - 확인
- `thanks` - 감사
- `apology` - 사과
- `emergency` - 긴급 상황

### 8.3 API 명세

#### GET /phrases (추천 문장 목록)

**Query Parameters:**
- `category`: 카테고리 필터
- `mission_step_id`: 특정 미션 단계용 문장
- `lang`: 언어 (`ko` | `en`)

**Response (200):**
```json
{
    "status": "SUCCESS",
    "message": "조회에 성공했어요",
    "data": [
        {
            "id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
            "text_ko": "안녕하세요",
            "text_en": "Hello",
            "category": "greeting",
            "usage_count": 150
        }
    ]
}
```

---

#### POST /phrases/{id}/use (문장 사용 기록)

**Response (200):**
```json
{
    "status": "SUCCESS",
    "message": "사용이 기록됐어요",
    "data": {
        "id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
        "usage_count": 151
    }
}
```

### 8.4 비즈니스 룰

1. 하나의 문장이 여러 미션 단계에 연결 가능 (N:M)
2. usage_count로 인기 문장 정렬
3. is_active=false인 문장은 목록에서 제외
4. 미션 단계 조회 시 해당 단계의 추천 문장 함께 반환

### 8.5 테스트 케이스

| ID | 설명 | 입력 | 기대 결과 |
|----|------|------|----------|
| TC-P-001 | 전체 문장 조회 | - | 200, 문장 목록 |
| TC-P-002 | 카테고리별 조회 | category: greeting | 200, 필터된 목록 |
| TC-P-003 | 미션 단계별 조회 | mission_step_id | 200, 해당 단계 문장 |
| TC-P-004 | 문장 사용 기록 | 유효한 phrase_id | 200, usage_count 증가 |
| TC-P-101 | 없는 문장 사용 | 존재하지 않는 ID | 404, ERROR_NOT_FOUND |

---

## 9. 도메인: routes

### 9.1 테이블 스키마

```sql
-- PostGIS 확장 필요
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE route_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v7(),
    profile_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    start_name TEXT NOT NULL,
    start_point GEOGRAPHY(Point, 4326) NOT NULL,
    end_name TEXT NOT NULL,
    end_point GEOGRAPHY(Point, 4326) NOT NULL,
    waypoints JSONB,
    route_option TEXT NOT NULL DEFAULT 'traoptimal',
    total_distance_m INT NOT NULL,
    total_duration_s INT NOT NULL,
    path_data JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_route_history_profile_id ON route_history(profile_id);
CREATE INDEX idx_route_history_created_at ON route_history(created_at DESC);
CREATE INDEX idx_route_history_start_point ON route_history USING GIST(start_point);
CREATE INDEX idx_route_history_end_point ON route_history USING GIST(end_point);
```

### 9.2 Enum 값

**RouteOption:**
- `traoptimal` - 실시간 최적
- `trafast` - 실시간 빠른길
- `tracomfort` - 실시간 편한길
- `traavoidtoll` - 무료 우선
- `traavoidcaronly` - 자동차 전용도로 회피

### 9.3 API 명세

#### POST /routes/search (경로 검색)

**Request:**
```json
{
    "start": {
        "name": "서울역",
        "lat": 37.5547,
        "lng": 126.9706
    },
    "end": {
        "name": "강남역",
        "lat": 37.4979,
        "lng": 127.0276
    },
    "waypoints": [
        {
            "name": "명동",
            "lat": 37.5636,
            "lng": 126.9869
        }
    ],
    "option": "traoptimal"
}
```

**Response (200):**
```json
{
    "status": "SUCCESS",
    "message": "경로 검색에 성공했어요",
    "data": {
        "id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
        "start": {
            "name": "서울역",
            "lat": 37.5547,
            "lng": 126.9706
        },
        "end": {
            "name": "강남역",
            "lat": 37.4979,
            "lng": 127.0276
        },
        "total_distance_m": 12500,
        "total_duration_s": 1800,
        "distance_text": "12.5km",
        "duration_text": "약 30분",
        "path": [
            {"lat": 37.5547, "lng": 126.9706},
            {"lat": 37.5500, "lng": 126.9800},
            {"lat": 37.4979, "lng": 127.0276}
        ]
    }
}
```

---

#### GET /routes/recent (최근 경로 조회)

**Query Parameters:**
- `limit`: 조회 개수 (기본값: 10, 최대: 50)

**Response (200):**
```json
{
    "status": "SUCCESS",
    "message": "조회에 성공했어요",
    "data": [
        {
            "id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
            "start_name": "서울역",
            "end_name": "강남역",
            "total_distance_m": 12500,
            "total_duration_s": 1800,
            "created_at": "2026-01-27T10:00:00Z"
        }
    ]
}
```

---

#### GET /routes/{route_id} (경로 상세 조회)

**Path Parameters:**
- `route_id`: 경로 기록 UUID

**Response (200):**
```json
{
    "status": "SUCCESS",
    "message": "경로 조회에 성공했어요",
    "data": {
        "id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
        "start": {
            "name": "서울역",
            "lat": 37.5547,
            "lng": 126.9706
        },
        "end": {
            "name": "강남역",
            "lat": 37.4979,
            "lng": 127.0276
        },
        "total_distance_m": 12500,
        "total_duration_s": 1800,
        "distance_text": "12.5km",
        "duration_text": "약 30분",
        "path": [[126.9706, 37.5547], [126.98, 37.55], [127.0276, 37.4979]]
    }
}
```

**Error (404):**
```json
{
    "status": "RESOURCE_NOT_FOUND",
    "message": "경로 기록을 찾을 수 없어요",
    "data": null
}
```

### 9.4 비즈니스 룰

1. Naver Maps Directions API 응답에서 필요한 정보만 추출
2. 좌표는 PostGIS GEOGRAPHY(Point, 4326) 타입으로 저장
3. 네이버 지도 API는 WGS84 좌표계 사용 (호환됨)
4. 경유지는 최대 5개까지 지원

### 9.5 테스트 케이스

| ID | 설명 | 입력 | 기대 결과 |
|----|------|------|----------|
| TC-R-001 | 기본 경로 검색 | 출발지, 도착지 | 200, 경로 정보 |
| TC-R-002 | 경유지 포함 검색 | 출발지, 경유지, 도착지 | 200, 경로 정보 |
| TC-R-003 | 옵션 변경 검색 | option: trafast | 200, 빠른길 경로 |
| TC-R-004 | 최근 경로 조회 | - | 200, 히스토리 목록 |
| TC-R-005 | 경로 상세 조회 | route_id | 200, 전체 경로 데이터 |
| TC-R-101 | 경로 없음 | 도달 불가능한 좌표 | 400, ERROR_ROUTE_NOT_FOUND |
| TC-R-102 | 잘못된 좌표 | lat: 200 (범위 초과) | 400, ERROR_VALIDATION |
| TC-R-103 | 경유지 초과 | 6개 이상 경유지 | 400, ERROR_TOO_MANY_WAYPOINTS |
| TC-R-104 | 존재하지 않는 경로 | 잘못된 route_id | 404, RESOURCE_NOT_FOUND |

---

## 10. 공통 규칙

### 응답 형식

```json
{
    "status": "SUCCESS | ERROR_*",
    "message": "한글 메시지",
    "data": { ... }
}
```

### 에러 코드 규칙

- `ERROR_` 접두사
- 대문자 스네이크 케이스

**공통 에러:**
- `ERROR_UNAUTHORIZED` - 인증 필요
- `ERROR_INVALID_TOKEN` - 유효하지 않은 토큰
- `ERROR_FORBIDDEN` - 권한 없음
- `ERROR_NOT_FOUND` - 리소스 없음
- `ERROR_VALIDATION` - 유효성 검사 실패

**도메인별 에러:**
- `ERROR_INVALID_AUDIO` - 잘못된 오디오 파일 (translations)
- `ERROR_MISSION_ALREADY_STARTED` - 이미 시작한 미션 (missions)
- `ERROR_MISSION_NOT_STARTED` - 시작하지 않은 미션 (missions)
- `ERROR_ROUTE_NOT_FOUND` - 경로 없음 (routes)
- `ERROR_TOO_MANY_WAYPOINTS` - 경유지 초과 (routes)

### 인증

- 모든 API는 Supabase Auth Bearer 토큰 필요
- **RPC/RLS 사용 금지** - FastAPI에서 JWT 검증만 사용
- 토큰 검증 실패 시 401 반환

---

## 11. 시드 데이터

### 미션 템플릿

```json
[
    {
        "mission_type": "taxi",
        "title_ko": "택시 이용하기",
        "title_en": "Taking a Taxi",
        "estimated_duration_min": 15,
        "steps": [
            {"step_order": 1, "title_ko": "택시 잡기", "title_en": "Hailing a Taxi"},
            {"step_order": 2, "title_ko": "목적지 전달", "title_en": "Telling Destination"},
            {"step_order": 3, "title_ko": "요금 확인", "title_en": "Checking Fare"},
            {"step_order": 4, "title_ko": "결제하기", "title_en": "Making Payment"},
            {"step_order": 5, "title_ko": "하차하기", "title_en": "Getting Off"}
        ]
    },
    {
        "mission_type": "payment",
        "title_ko": "결제하기",
        "title_en": "Making Payment",
        "estimated_duration_min": 10,
        "steps": [
            {"step_order": 1, "title_ko": "상품 선택", "title_en": "Selecting Items"},
            {"step_order": 2, "title_ko": "결제 방법 선택", "title_en": "Choosing Payment Method"},
            {"step_order": 3, "title_ko": "카드/현금 결제", "title_en": "Card/Cash Payment"},
            {"step_order": 4, "title_ko": "영수증 받기", "title_en": "Getting Receipt"}
        ]
    },
    {
        "mission_type": "checkin",
        "title_ko": "체크인하기",
        "title_en": "Hotel Check-in",
        "estimated_duration_min": 10,
        "steps": [
            {"step_order": 1, "title_ko": "예약 확인", "title_en": "Confirming Reservation"},
            {"step_order": 2, "title_ko": "신분증 제시", "title_en": "Showing ID"},
            {"step_order": 3, "title_ko": "객실 배정", "title_en": "Room Assignment"},
            {"step_order": 4, "title_ko": "와이파이/조식 확인", "title_en": "WiFi/Breakfast Info"}
        ]
    }
]
```

### 추천 문장

```json
[
    {"text_ko": "안녕하세요", "text_en": "Hello", "category": "greeting"},
    {"text_ko": "감사합니다", "text_en": "Thank you", "category": "thanks"},
    {"text_ko": "택시!", "text_en": "Taxi!", "category": "request"},
    {"text_ko": "여기로 가주세요", "text_en": "Please take me here", "category": "request"},
    {"text_ko": "얼마예요?", "text_en": "How much is it?", "category": "confirmation"},
    {"text_ko": "카드로 결제할게요", "text_en": "I'll pay by card", "category": "request"},
    {"text_ko": "예약했어요", "text_en": "I have a reservation", "category": "confirmation"},
    {"text_ko": "죄송합니다", "text_en": "I'm sorry", "category": "apology"},
    {"text_ko": "도와주세요!", "text_en": "Please help me!", "category": "emergency"}
]
```
