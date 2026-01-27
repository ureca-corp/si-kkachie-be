# SESSION: Kkachie 여행 도우미 백엔드

## 현재 상태
- **Phase**: 6 완료 ✅ (전체 완료)
- **마지막 작업**: 프론트엔드 API 문서 생성
- **다음 작업**: 없음 (프로젝트 완료)

---

## 프로젝트 개요

**Kkachie** - 외국인 여행자를 위한 실시간 번역 및 미션 가이드 앱 백엔드

### 핵심 기능
1. **실시간 음성/텍스트 번역** (한↔영)
2. **미션 기반 가이드** (택시/결제/체크인)
3. **추천 문장 템플릿** (미션+단계별)
4. **경로 안내** (네이버 지도 연동)

---

## Phase 0 결정 사항

### 1. 인증/사용자 관리
| 항목 | 결정 |
|------|------|
| 인증 필수 여부 | 필수 회원 |
| 인증 방식 | 소셜 로그인 (Google/Apple) |
| 구현 방법 | **Supabase Auth** ⚠️ 변경됨 (기존: Firebase Auth) |

### 2. 외부 API 선택
| 기능 | 서비스 | 무료 티어 |
|------|--------|----------|
| 인증 | Supabase Auth | 무료 (50,000 MAU) |
| 번역 | Google Cloud Translation | 월 500,000자 |
| STT | Google Cloud Speech-to-Text | 월 60분 |
| TTS | Google Cloud Text-to-Speech | 월 400만자 |
| 지도 | Naver Maps Directions API | - |

### 3. 기능 범위
| 항목 | 결정 |
|------|------|
| 지원 언어 | 한국어 <-> 영어만 (MVP) |
| 지도 기능 | 경로 검색만 (장소 검색 제외) |
| 미션 종류 | 택시, 결제, 체크인 (3종) |
| 추천 문장 관리 | DB 저장 (API로 CRUD) |

### 4. 데이터 저장
| 데이터 | 저장 위치 |
|--------|----------|
| 사용자 정보 | Supabase (Auth + DB) |
| 번역 히스토리 | 서버 (영구 저장) |
| 미션 진행 상태 | 서버 |
| 추천 문장 템플릿 | 서버 DB |

---

## Phase 1 결과: 외부 API 리서치 완료

### 1. Supabase Auth (인증) ⚠️ 변경됨

| 항목 | 내용 |
|------|------|
| **Python SDK** | `supabase` |
| **설치** | `uv add supabase` |
| **인증 방식** | JWT 토큰 |
| **토큰 검증** | `supabase.auth.get_user(token)` |
| **지원 OAuth** | Google, Apple (소셜 로그인) |

**FastAPI 통합 방법:**
- HTTPBearer + Depends로 의존성 주입
- `get_user(token)`으로 클라이언트 토큰 검증
- 검증된 토큰에서 `id`, `email` 추출

**환경 변수:**
- `SUPABASE_URL`: Supabase 프로젝트 URL
- `SUPABASE_KEY`: Supabase anon key
- `SUPABASE_SERVICE_KEY`: 서비스 역할 키 (백엔드용)

### 2. Google Cloud Translation (번역)

| 항목 | 내용 |
|------|------|
| **Python SDK** | `google-cloud-translate` |
| **설치** | `uv add google-cloud-translate` |
| **API 버전** | v3 (Advanced) |
| **무료 티어** | 월 500,000자 ($10 크레딧) |
| **초과 비용** | $20 / 100만자 |

### 3. Google Cloud Speech-to-Text (STT)

| 항목 | 내용 |
|------|------|
| **Python SDK** | `google-cloud-speech` |
| **설치** | `uv add google-cloud-speech` |
| **무료 티어** | 월 60분 |
| **초과 비용** | $0.006 / 15초 (standard) |

### 4. Google Cloud Text-to-Speech (TTS)

| 항목 | 내용 |
|------|------|
| **Python SDK** | `google-cloud-texttospeech` |
| **설치** | `uv add google-cloud-texttospeech` |
| **무료 티어** | 월 400만자 (Standard), 100만자 (WaveNet) |
| **초과 비용** | $4 / 100만자 (Standard) |

### 5. Naver Maps Directions API (경로)

| 항목 | 내용 |
|------|------|
| **API 유형** | REST API |
| **엔드포인트** | `https://naveropenapi.apigw.ntruss.com/map-direction/v1/driving` |
| **인증** | X-NCP-APIGW-API-KEY-ID, X-NCP-APIGW-API-KEY |

---

## Phase 2 결과: 도메인 상세 인터뷰 완료

### 1. users 도메인

| 항목 | 결정 |
|------|------|
| **스키마** | id, supabase_uid, email, display_name, preferred_language, profile_image_url, created_at |
| **Validation** | Supabase Auth 기반 + email 형식, display_name 길이(2-50자), preferred_language(ko/en) |
| **API** | GET /users/me, PATCH /users/me, POST /auth/verify-token, DELETE /users/me |
| **비즈니스 룰** | 첫 로그인 시 자동 생성, Supabase Auth 토큰 검증 |
| **테스트** | 전체 커버리지 (Happy Path + 실패 + 엣지 케이스) |

### 2. translations 도메인

| 항목 | 결정 |
|------|------|
| **스키마** | id, user_id, source_text, translated_text, source_lang, target_lang, translation_type(text/voice), mission_id(nullable), audio_url, duration, confidence_score, created_at |
| **저장 정책** | 영구 저장 |
| **API** | POST /translate/text, POST /translate/voice, GET /translations, DELETE /translations/{id} |
| **음성 응답** | 번역 텍스트 + TTS 오디오 URL 함께 반환 |
| **테스트** | 전체 커버리지 |

### 3. missions 도메인

| 항목 | 결정 |
|------|------|
| **구조** | 완전 정규화 (mission_templates, mission_steps, mission_progress, mission_step_progress) |
| **진행 상태** | not_started → in_progress → 종료 시 result 선택 |
| **종료 방식** | 사용자가 "미션 종료" 클릭 → 해결/부분해결/미해결 중 선택 → 기록 후 종료 |
| **API** | GET /missions, GET /missions/{id}, POST /missions/{id}/start, PATCH /missions/{id}/progress, POST /missions/{id}/end + 관리자 CRUD |
| **초기 데이터** | 시드 데이터 + 관리자 API로 관리 |
| **테스트** | 전체 커버리지 (3가지 결과 각각 테스트) |

**미션 종류 (3종):**
- 택시: 택시 잡기 → 목적지 전달 → 요금 확인 → 결제 → 하차
- 결제: 상품 선택 → 결제 방법 → 카드/현금 → 영수증
- 체크인: 예약 확인 → 신분증 제시 → 객실 배정 → 와이파이/조식 확인

### 4. phrases 도메인

| 항목 | 결정 |
|------|------|
| **스키마** | id, text_ko, text_en, category(인사/요청/확인/감사 등), usage_count, created_at |
| **관계** | N:M (phrase_step_mapping 중간 테이블로 미션 단계와 연결) |
| **API** | GET /phrases, POST /phrases/{id}/use + 관리자 CRUD |
| **테스트** | 전체 커버리지 |

### 5. routes 도메인

| 항목 | 결정 |
|------|------|
| **방식** | 가공만 (Naver API 응답에서 distance, duration, path 추출) |
| **저장** | 세션 동안만 임시 저장 |
| **API** | POST /routes/search (옵션: traoptimal/trafast 등), GET /routes/recent, 경유지 지원 |
| **테스트** | 전체 커버리지 |

---

## 도메인 구조

```
src/modules/
├── users/          # 사용자 관리 (Supabase Auth 연동)
├── translations/   # 번역 기록 관리
├── missions/       # 미션 템플릿 및 진행 상태
├── phrases/        # 추천 문장 템플릿
└── routes/         # 경로 검색 (Naver API 프록시)
```

---

## External 모듈 구조

```
src/external/
├── auth/
│   └── supabase_provider.py    # Supabase Auth ⚠️ 변경됨
├── translation/
│   └── google_provider.py      # Google Cloud Translation
├── speech/
│   ├── google_stt_provider.py  # Google Cloud STT
│   └── google_tts_provider.py  # Google Cloud TTS
└── maps/
    └── naver_provider.py       # Naver Maps Directions
```

---

## 필요 Python 패키지

```
supabase                # Supabase Auth ⚠️ 변경됨
google-cloud-translate  # 번역
google-cloud-speech     # STT
google-cloud-texttospeech  # TTS
httpx                   # Naver API 호출용
```

---

## 필요 환경 변수

```env
# Supabase ⚠️ 변경됨
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# Google Cloud (공통)
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
GOOGLE_CLOUD_PROJECT=your-project-id

# Naver Cloud Platform
NAVER_CLIENT_ID=your-ncp-client-id
NAVER_CLIENT_SECRET=your-ncp-client-secret
```

---

## Phase 3 결과: 설계 원칙 확정

### 주요 설계 원칙

| 항목 | 결정 |
|------|------|
| **사용자 테이블** | auth.users (Supabase 관리) + profiles 테이블 (추가 정보, FK 연결) |
| **UUID** | UUID v7 사용 (`uuid_generate_v7()`) - 시간순 정렬 가능 |
| **위치 데이터** | PostGIS `GEOGRAPHY(Point, 4326)` 타입 - 네이버 지도 WGS84 호환 |
| **VARCHAR** | 길이 미지정 (TEXT 사용) - 특수 경우만 제한 |
| **Supabase 정책** | **RPC/RLS 절대 금지** - JWT 검증으로만 인증 |
| **이미지 업로드** | Supabase Storage Bucket + Presigned URL |
| **테스트 환경** | Supabase Local (`supabase start`) |

### 생성된 문서

- [x] `docs/DDD_CLASS_DIAGRAM.md` - Entity 관계도 + 상세 명세
- [x] `docs/SPEC.md` - 도메인별 API 명세

---

## Phase 4 결과: TDD 코드 생성 완료 ✅

### 생성된 모듈
| 도메인 | 모델 | 테스트 | 상태 |
|--------|------|--------|------|
| profiles | Profile | 12개 | ✅ PASSED |
| translations | Translation | 13개 | ✅ PASSED |
| missions | MissionTemplate, MissionStep, MissionProgress, MissionStepProgress | 15개 | ✅ PASSED |
| phrases | PhraseCategory, Phrase, PhraseStepMapping | 10개 | ✅ PASSED |
| routes | RouteSession | 10개 | ✅ PASSED |
| health | - | 2개 | ✅ PASSED |

**총 테스트: 63개 모두 통과**

### Alembic 마이그레이션
- `4b5c6a12bd75_add_domain_tables.py` 생성
- 10개 테이블 생성 완료

---

## Phase 5 결과: 코드 리뷰 완료 ✅

### 수정된 이슈
| 우선순위 | 내용 | 상태 |
|----------|------|------|
| HIGH | 미사용 users 모듈 삭제 | ✅ 수정 |
| HIGH | storage 메서드명 수정 (get_upload_url) | ✅ 수정 |
| HIGH | controller None 체크 추가 | ✅ 수정 |

### Supabase Local 설정
- PostgreSQL 드라이버 설치 (psycopg2-binary)
- conftest.py 트랜잭션 롤백 패턴 적용
- .env.test 생성
- 63개 테스트 Supabase Local에서 통과

---

## Phase 6 결과: 프론트엔드 문서 완료 ✅

### 생성된 문서 (docs/user_flows/)
| 파일 | 내용 |
|------|------|
| README.md | 개요 & 네비게이션 |
| 01-auth-profile.md | 인증 + 프로필 |
| 02-translations.md | 번역 기능 |
| 03-missions.md | 미션 시스템 |
| 04-phrases.md | 상용 표현 |
| 05-routes.md | 경로 검색 |
| 06-api-reference.md | 전체 API 레퍼런스 |
| 07-error-handling.md | 에러 처리 가이드 |

### 문서 포함 내용
- ASCII 모바일 화면 목업
- API Request/Response 예시
- TypeScript 타입 정의
- React Native 구현 예시

---

## 프로젝트 완료 ✅

### 커밋 히스토리
| 커밋 | 내용 |
|------|------|
| `b4ec40e` | DDD class diagram + API specification (Phase 0-3) |
| `08e80a1` | TDD code generation for all domains (Phase 4) |
| `1cdbcf7` | Resolve HIGH issues from code review (Phase 5) |
| `2946eff` | Configure Supabase Local for integration testing |
| `a1539e7` | Frontend developer API documentation (Phase 6) |

---

## 변경 이력

| 날짜 | Phase | 변경 내용 |
|------|-------|----------|
| 2026-01-27 | 0 | 초기 요구사항 명확화 완료 |
| 2026-01-27 | 1 | 외부 API 리서치 완료, 스펙 파일 생성 |
| 2026-01-27 | 2 | 도메인 상세 인터뷰 완료, Firebase → Supabase 변경 |
| 2026-01-27 | 3 | DDD Class Diagram + SPEC.md 작성 완료 (설계 원칙 반영) |
| 2026-01-27 | 4 | TDD 코드 생성 완료, 63개 테스트 통과 |
| 2026-01-27 | 5 | 코드 리뷰 완료, HIGH 이슈 수정, Supabase Local 설정 |
| 2026-01-27 | 6 | 프론트엔드 API 문서 8개 생성 |
