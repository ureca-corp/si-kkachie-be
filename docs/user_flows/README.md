# Kkachie API - Frontend Developer Guide

> Kkachie - Real-time Translation & Mission Guide App for Foreign Travelers in Korea

## Overview

This documentation provides frontend developers with comprehensive guides for integrating with the Kkachie backend API. Each document includes:

- Mobile screen mockups (ASCII)
- API request/response examples
- User flow diagrams
- TypeScript/React Native implementation hints

## Quick Start

### Base URL
```
Production: https://api.kkachie.com
Development: http://localhost:8000
```

### Authentication
All API endpoints (except health check) require Supabase Auth Bearer token:
```
Authorization: Bearer {supabase_access_token}
```

## Documentation Index

| # | Document | Description |
|---|----------|-------------|
| 1 | [01-auth-profile.md](./01-auth-profile.md) | Authentication & Profile Management |
| 2 | [02-translations.md](./02-translations.md) | Text & Voice Translation |
| 3 | [03-missions.md](./03-missions.md) | Mission System (Taxi, Payment, Check-in) |
| 4 | [04-phrases.md](./04-phrases.md) | Recommended Phrases |
| 5 | [05-routes.md](./05-routes.md) | Route Search (Naver Maps) |
| 6 | [06-api-reference.md](./06-api-reference.md) | Complete API Reference |
| 7 | [07-error-handling.md](./07-error-handling.md) | Error Codes & Handling |

## Architecture Overview

```
+------------------+     +------------------+     +------------------+
|                  |     |                  |     |                  |
|  Mobile App      |---->|  Kkachie API     |---->|  External APIs   |
|  (React Native)  |     |  (FastAPI)       |     |                  |
|                  |     |                  |     +------------------+
+------------------+     +------------------+     | - Supabase Auth  |
                               |                  | - Google Cloud   |
                               |                  |   - Translation  |
                               v                  |   - STT / TTS    |
                         +------------------+     | - Naver Maps     |
                         |                  |     +------------------+
                         |  Supabase        |
                         |  (PostgreSQL)    |
                         |                  |
                         +------------------+
```

## Domain Overview

### 1. Profiles (Authentication + User)
- Supabase Auth token verification
- Auto profile creation on first login
- Profile image upload via Presigned URL

### 2. Translations
- Text translation (Korean <-> English)
- Voice translation (STT -> Translate -> TTS)
- Translation history management

### 3. Missions
- 3 mission types: Taxi, Payment, Check-in
- Step-by-step guided flow
- Progress tracking with results

### 4. Phrases
- Pre-defined recommended phrases
- Category filtering (greeting, request, etc.)
- Usage count tracking

### 5. Routes
- Naver Maps Directions API proxy
- Route history storage
- Support for waypoints

## Response Format

All API responses follow this standard format:

```typescript
interface ApiResponse<T> {
  status: string;      // "SUCCESS" or "ERROR_*"
  message: string;     // Human-readable message (Korean)
  data: T | null;      // Response payload
}
```

## Language Support

- Supported languages: Korean (`ko`), English (`en`)
- User preferred language affects:
  - Mission titles/descriptions
  - API response messages

## Getting Started

1. Set up Supabase Auth in your React Native app
2. Implement token refresh logic
3. Create API client with Bearer token header
4. Follow individual domain guides for feature implementation

---

**Version:** 1.0.0
**Last Updated:** 2026-01-27
