# Complete API Reference

## Base URL

| Environment | URL |
|-------------|-----|
| Production | `https://api.kkachie.com` |
| Development | `http://localhost:8000` |

## Authentication

All endpoints (except `/health`) require Supabase Auth Bearer token:

```
Authorization: Bearer {supabase_access_token}
```

## Response Format

All responses follow this format:

```json
{
  "status": "SUCCESS | ERROR_*",
  "message": "Human-readable message (Korean)",
  "data": { ... } | null
}
```

---

## API Endpoints Summary

### Authentication & Profile

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/verify-token` | Verify token & auto-create profile |
| GET | `/users/me` | Get current user profile |
| PATCH | `/users/me` | Update profile |
| POST | `/users/me/profile-image` | Get profile image upload URL |
| DELETE | `/users/me` | Delete account |

### Translations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/translate/text` | Translate text |
| POST | `/translate/voice` | Translate voice (STT + Translate + TTS) |
| GET | `/translations` | Get translation history |
| DELETE | `/translations/{id}` | Delete translation record |

### Missions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/missions` | List all missions with progress |
| GET | `/missions/{id}` | Get mission detail with steps |
| POST | `/missions/{id}/start` | Start a mission |
| PATCH | `/missions/{id}/progress` | Mark step as complete |
| POST | `/missions/{id}/end` | End mission with result |

### Phrases

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/phrases` | Get recommended phrases |
| POST | `/phrases/{id}/use` | Record phrase usage |

### Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/routes/search` | Search route (Naver Maps) |
| GET | `/routes/recent` | Get recent route history |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check (no auth required) |

---

## Detailed API Specifications

### POST /auth/verify-token

Verifies Supabase token and creates profile for new users.

**Headers:**
```
Authorization: Bearer {supabase_access_token}
```

**Response (200 - Existing User):**
```json
{
  "status": "SUCCESS",
  "message": "인증에 성공했어요",
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "email": "user@example.com",
    "display_name": "John Doe",
    "preferred_language": "en",
    "profile_image_url": "https://...",
    "is_new_user": false
  }
}
```

**Response (201 - New User):**
```json
{
  "status": "SUCCESS",
  "message": "회원가입이 완료됐어요",
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "email": "user@example.com",
    "display_name": null,
    "preferred_language": "en",
    "profile_image_url": null,
    "is_new_user": true
  }
}
```

---

### GET /users/me

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "조회에 성공했어요",
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "email": "user@example.com",
    "display_name": "John Doe",
    "preferred_language": "en",
    "profile_image_url": "https://...",
    "created_at": "2026-01-27T10:00:00Z"
  }
}
```

---

### PATCH /users/me

**Request:**
```json
{
  "display_name": "Jane Doe",
  "preferred_language": "ko"
}
```

| Field | Type | Constraints |
|-------|------|-------------|
| display_name | string | 2-50 characters |
| preferred_language | string | "ko" or "en" |

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "정보가 수정됐어요",
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "email": "user@example.com",
    "display_name": "Jane Doe",
    "preferred_language": "ko",
    "profile_image_url": null
  }
}
```

---

### POST /users/me/profile-image

**Request:**
```json
{
  "file_name": "profile.jpg",
  "content_type": "image/jpeg"
}
```

| Field | Type | Constraints |
|-------|------|-------------|
| file_name | string | min 1 character |
| content_type | string | image/jpeg, image/png, image/gif, image/webp |

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "업로드 URL이 발급됐어요",
  "data": {
    "upload_url": "https://storage.supabase.co/.../presigned",
    "public_url": "https://storage.supabase.co/.../profile.jpg",
    "expires_in": 3600
  }
}
```

---

### DELETE /users/me

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "회원 탈퇴가 완료됐어요"
}
```

---

### POST /translate/text

**Request:**
```json
{
  "source_text": "안녕하세요",
  "source_lang": "ko",
  "target_lang": "en",
  "mission_progress_id": null
}
```

| Field | Type | Constraints |
|-------|------|-------------|
| source_text | string | 1-5000 characters |
| source_lang | string | "ko" or "en" |
| target_lang | string | "ko" or "en" (must differ from source_lang) |
| mission_progress_id | string | optional |

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "번역이 완료됐어요",
  "data": {
    "id": "uuid",
    "source_text": "안녕하세요",
    "translated_text": "Hello",
    "source_lang": "ko",
    "target_lang": "en",
    "translation_type": "text",
    "mission_progress_id": null,
    "created_at": "2026-01-27T10:00:00Z"
  }
}
```

---

### POST /translate/voice

**Request (multipart/form-data):**
| Field | Type | Constraints |
|-------|------|-------------|
| audio_file | file | required |
| source_lang | string | "ko" or "en" |
| target_lang | string | "ko" or "en" (must differ) |
| mission_progress_id | string | optional |

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "음성 번역이 완료됐어요",
  "data": {
    "id": "uuid",
    "source_text": "안녕하세요",
    "translated_text": "Hello",
    "source_lang": "ko",
    "target_lang": "en",
    "translation_type": "voice",
    "mission_progress_id": null,
    "audio_url": "https://storage.supabase.co/.../tts.mp3",
    "duration_ms": 1500,
    "confidence_score": 0.95,
    "created_at": "2026-01-27T10:00:00Z"
  }
}
```

---

### GET /translations

**Query Parameters:**
| Parameter | Type | Default | Constraints |
|-----------|------|---------|-------------|
| page | int | 1 | >= 1 |
| limit | int | 20 | 1-100 |
| type | string | - | "text" or "voice" |
| mission_progress_id | string | - | UUID |

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "조회에 성공했어요",
  "data": {
    "items": [...],
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

### DELETE /translations/{id}

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "번역 기록이 삭제됐어요"
}
```

---

### GET /missions

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "조회에 성공했어요",
  "data": [
    {
      "id": "uuid",
      "title": "Taking a Taxi",
      "description": "Learn how to take a taxi in Korea",
      "mission_type": "taxi",
      "estimated_duration_min": 15,
      "icon_url": "https://...",
      "steps_count": 5,
      "user_progress": {
        "id": "uuid",
        "status": "in_progress",
        "current_step": 2,
        "started_at": "2026-01-27T09:00:00Z"
      }
    }
  ]
}
```

---

### GET /missions/{id}

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "조회에 성공했어요",
  "data": {
    "id": "uuid",
    "title": "Taking a Taxi",
    "description": "...",
    "mission_type": "taxi",
    "estimated_duration_min": 15,
    "icon_url": "https://...",
    "steps": [
      {
        "id": "uuid",
        "step_order": 1,
        "title": "Hailing a Taxi",
        "description": "...",
        "is_completed": true,
        "phrases": [
          {
            "id": "uuid",
            "text_ko": "택시!",
            "text_en": "Taxi!",
            "category": "request"
          }
        ]
      }
    ],
    "user_progress": {...}
  }
}
```

---

### POST /missions/{id}/start

**Response (201):**
```json
{
  "status": "SUCCESS",
  "message": "미션을 시작했어요",
  "data": {
    "progress_id": "uuid",
    "mission_id": "uuid",
    "status": "in_progress",
    "current_step": 1,
    "started_at": "2026-01-27T10:00:00Z"
  }
}
```

---

### PATCH /missions/{id}/progress

**Request:**
```json
{
  "step_id": "uuid",
  "is_completed": true
}
```

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "단계를 완료했어요",
  "data": {
    "progress_id": "uuid",
    "current_step": 3,
    "completed_steps": 3,
    "total_steps": 5
  }
}
```

---

### POST /missions/{id}/end

**Request:**
```json
{
  "result": "resolved"
}
```

| Field | Type | Values |
|-------|------|--------|
| result | string | "resolved", "partially_resolved", "unresolved" |

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "미션을 종료했어요",
  "data": {
    "progress_id": "uuid",
    "status": "ended",
    "result": "resolved",
    "ended_at": "2026-01-27T10:30:00Z",
    "duration_minutes": 30
  }
}
```

---

### GET /phrases

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| category | string | greeting, request, confirmation, thanks, apology, emergency |
| mission_step_id | string | UUID of mission step |

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "조회에 성공했어요",
  "data": [
    {
      "id": "uuid",
      "text_ko": "안녕하세요",
      "text_en": "Hello",
      "category": "greeting",
      "usage_count": 150
    }
  ]
}
```

---

### POST /phrases/{id}/use

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "사용이 기록됐어요",
  "data": {
    "id": "uuid",
    "usage_count": 151
  }
}
```

---

### POST /routes/search

**Request:**
```json
{
  "start": {
    "name": "Seoul Station",
    "lat": 37.5547,
    "lng": 126.9706
  },
  "end": {
    "name": "Gangnam Station",
    "lat": 37.4979,
    "lng": 127.0276
  },
  "waypoints": [...],
  "option": "traoptimal"
}
```

| Field | Type | Constraints |
|-------|------|-------------|
| start.lat | float | -90 to 90 |
| start.lng | float | -180 to 180 |
| waypoints | array | max 5 items |
| option | string | traoptimal, trafast, tracomfort, traavoidtoll, traavoidcaronly |

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "경로 검색에 성공했어요",
  "data": {
    "id": "uuid",
    "start": {...},
    "end": {...},
    "total_distance_m": 12500,
    "total_duration_s": 1800,
    "distance_text": "12.5km",
    "duration_text": "약 30분",
    "path": [
      {"lat": 37.5547, "lng": 126.9706},
      ...
    ]
  }
}
```

---

### GET /routes/recent

**Query Parameters:**
| Parameter | Type | Default | Constraints |
|-----------|------|---------|-------------|
| limit | int | 10 | 1-50 |

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "조회에 성공했어요",
  "data": [
    {
      "id": "uuid",
      "start_name": "Seoul Station",
      "end_name": "Gangnam Station",
      "total_distance_m": 12500,
      "total_duration_s": 1800,
      "created_at": "2026-01-27T10:30:00Z"
    }
  ]
}
```

---

## Enum Values

### PreferredLanguage
- `ko` - Korean
- `en` - English

### TranslationType
- `text` - Text translation
- `voice` - Voice translation (STT + Translate + TTS)

### MissionType
- `taxi` - Taking a Taxi
- `payment` - Making Payment
- `checkin` - Hotel Check-in

### MissionStatus
- `not_started` - Not started
- `in_progress` - In progress
- `ended` - Ended

### MissionResult
- `resolved` - Resolved
- `partially_resolved` - Partially resolved
- `unresolved` - Unresolved

### PhraseCategory
- `greeting` - Greetings
- `request` - Requests
- `confirmation` - Confirmations
- `thanks` - Thanks
- `apology` - Apologies
- `emergency` - Emergency

### RouteOption
- `traoptimal` - Real-time optimal
- `trafast` - Fastest route
- `tracomfort` - Most comfortable
- `traavoidtoll` - Toll-free
- `traavoidcaronly` - Avoid car-only roads
