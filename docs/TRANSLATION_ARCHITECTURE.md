# Translation Module Architecture

번역 모듈의 전체 아키텍처와 데이터 흐름을 설명합니다.

## 주요 기능

| 기능 | 설명 |
|------|------|
| 텍스트 번역 | 한/영 텍스트 번역 |
| 음성 번역 | STT → 번역 → TTS 파이프라인 |
| 스레드 관리 | 대화 컨텍스트 유지 |
| 카테고리 컨텍스트 | 상황별 맞춤 번역 (Vertex AI) |

---

## Clean Architecture 레이어

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ Presentation Layer (Controllers)                                            │
│ - translate_text.py, translate_voice.py                                     │
│ - threads_*.py, categories_list.py                                          │
│ - HTTP 요청/응답 처리만 담당                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ Application Layer (Use Cases)                                               │
│ - CreateTextTranslationUseCase                                              │
│ - CreateVoiceTranslationUseCase                                             │
│ - CreateThreadUseCase, GetThreadUseCase, etc.                               │
│ - 비즈니스 로직 캡슐화                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ Domain Layer                                                                │
│ - _models.py (Translation, TranslationThread, Categories)                   │
│ - _exceptions.py (InvalidCategoryError, ThreadNotFoundError)                │
│ - _context_service.py (컨텍스트 프롬프트 빌드)                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ Infrastructure Layer                                                        │
│ - _repository.py (DB 접근)                                                  │
│ - _translation_service.py (외부 API 호출)                                   │
│ - External Providers (Google, Vertex AI, Supabase)                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 번역 프로세스 흐름

### 1. 기본 번역 (컨텍스트 없음)

```
┌──────────┐     POST /translate/text      ┌─────────────────────────────────┐
│  Client  │  ────────────────────────────▶│  Controller                     │
│          │    • source_text              │  translate_text.py              │
│          │    • source_lang: "en"        └────────────────┬────────────────┘
│          │    • target_lang: "ko"                         │
└──────────┘                                                ▼
     ▲                                     ┌─────────────────────────────────┐
     │                                     │  Use Case                       │
     │                                     │  CreateTextTranslationUseCase   │
     │                                     └────────────────┬────────────────┘
     │                                                      │
     │                                                      ▼
     │                                     ┌─────────────────────────────────┐
     │                                     │  Google Translation API v3     │
     │                                     │  (context 없음)                 │
     │                                     └────────────────┬────────────────┘
     │                                                      │
     │  ┌───────────────────────────────────────────────────┘
     │  │  Response: { translated_text: "안녕하세요" }
     └──┘
```

### 2. 컨텍스트 기반 AI 번역 (Vertex AI)

```
┌──────────┐     POST /translate/voice     ┌─────────────────────────────────┐
│  Client  │  ────────────────────────────▶│  Controller                     │
│          │    • audio_file               │  translate_voice.py             │
│          │    • source_lang: "en"        └────────────────┬────────────────┘
│          │    • target_lang: "ko"                         │
│          │    • context_primary: "FD6"                    │
│          │    • context_sub: "ordering"                   │
└──────────┘                                                ▼
     ▲                                     ┌─────────────────────────────────┐
     │                                     │  Use Case                       │
     │                                     │  CreateVoiceTranslationUseCase  │
     │                                     └────────────────┬────────────────┘
     │                                                      │
     │                        ┌─────────────────────────────┼─────────────────────────────┐
     │                        │                             │                             │
     │                        ▼                             ▼                             ▼
     │           ┌────────────────────┐      ┌────────────────────┐      ┌────────────────────┐
     │           │ Step 1: STT        │      │ Step 2: Context    │      │ Step 3: Translate  │
     │           │ Google Speech API  │      │ _context_service   │      │ Vertex AI (Gemini) │
     │           │                    │      │                    │      │                    │
     │           │ audio → "Hello"    │      │ 카테고리 조회       │      │ 컨텍스트 + 원문    │
     │           └────────────────────┘      │ 프롬프트 빌드       │      │      ↓             │
     │                                       └────────────────────┘      │ 자연스러운 번역    │
     │                                                                   └────────────────────┘
     │                                                      │
     │                                                      ▼
     │                                       ┌────────────────────┐
     │                                       │ Step 4: TTS        │
     │                                       │ Google TTS API     │
     │                                       │                    │
     │                                       │ 번역문 → MP3       │
     │                                       └────────────────────┘
     │                                                      │
     │  ┌───────────────────────────────────────────────────┘
     │  │  Response: { translated_text, audio_url, ... }
     └──┘
```

---

## 컨텍스트 프롬프트 빌드

### 프롬프트 구성 요소

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         컨텍스트 프롬프트 구조                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. 사용자 상황 설명 (자동 생성)                                              │
│     ────────────────────────────────────────────────                        │
│     "이 사용자는 음식점에서 주문을(를) 원합니다."                              │
│                                                                             │
│  2. 카테고리별 프롬프트 (DB 저장)                                             │
│     ────────────────────────────────────────────────                        │
│     "음식점 주문 상황입니다. 메뉴, 수량, 요청사항 관련                         │
│      표현을 자연스럽게 번역해주세요."                                          │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  최종 프롬프트 예시:                                                          │
│  ─────────────────                                                          │
│  "이 사용자는 음식점에서 주문을(를) 원합니다.                                  │
│   음식점 주문 상황입니다. 메뉴, 수량, 요청사항 관련 표현을                      │
│   자연스럽게 번역해주세요."                                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### _context_service.py 흐름

```python
def build_translation_context(session, primary_code, sub_code, target_lang):
    # 1. 카테고리 이름 조회
    primary_name = "음식점"   # from DB (FD6 → 음식점)
    sub_name = "주문"         # from DB (ordering → 주문)

    # 2. 사용자 상황 설명 생성
    situation = f"이 사용자는 {primary_name}에서 {sub_name}을(를) 원합니다."

    # 3. 카테고리별 프롬프트 조회
    category_prompt = get_context_prompt(session, primary_code, sub_code)

    # 4. 전체 컨텍스트 조합
    return f"{situation}\n{category_prompt}"
```

---

## Provider 선택 로직

```
                    ┌─────────────────────────────────────┐
                    │       _translation_service.py       │
                    │            translate()              │
                    └─────────────────┬───────────────────┘
                                      │
                    ┌─────────────────┴───────────────────┐
                    │                                     │
                    ▼                                     ▼
    ┌───────────────────────────────┐    ┌───────────────────────────────┐
    │  context 있음                  │    │  context 없음                  │
    └───────────────┬───────────────┘    └───────────────┬───────────────┘
                    │                                     │
                    ▼                                     ▼
    ┌───────────────────────────────┐    ┌───────────────────────────────┐
    │  Vertex AI (Gemini 1.5 Flash) │    │  Google Translation API v3   │
    │                               │    │                               │
    │  • 컨텍스트 기반 번역          │    │  • 단순 번역                   │
    │  • 자연스러운 표현             │    │  • 빠른 속도                   │
    │  • 상황 맞춤 어휘              │    │  • 저렴한 비용                 │
    └───────────────────────────────┘    └───────────────────────────────┘
```

---

## 카테고리 시스템

### 1차 카테고리 (장소 유형)

| code | name_ko | name_en |
|------|---------|---------|
| FD6 | 음식점 | Restaurant |
| CE7 | 카페 | Cafe |
| HP8 | 병원 | Hospital |
| PM9 | 약국 | Pharmacy |
| MT1 | 대형마트 | Mart |
| CS2 | 편의점 | Convenience Store |
| BK9 | 은행 | Bank |
| SW8 | 지하철역 | Subway |
| AD5 | 숙박 | Hotel |
| AT4 | 관광명소 | Attraction |
| GEN | 일반 | General |

### 2차 카테고리 (상황/의도)

| code | name_ko | name_en |
|------|---------|---------|
| ordering | 주문 | Ordering |
| payment | 결제 | Payment |
| complaint | 불만 | Complaint |
| reservation | 예약 | Reservation |
| reception | 접수 | Reception |
| symptom_explain | 증상설명 | Symptom Explanation |
| buy_medicine | 약구매 | Buy Medicine |
| find_item | 물건찾기 | Find Item |
| exchange_refund | 교환/환불 | Exchange/Refund |
| inquiry | 문의 | Inquiry |
| other | 기타 | Other |

### 카테고리 매핑

```
FD6 (음식점)    → ordering, payment, complaint, reservation, inquiry, other
CE7 (카페)      → ordering, payment, complaint, inquiry, other
HP8 (병원)      → reception, symptom_explain, payment, inquiry, other
PM9 (약국)      → symptom_explain, buy_medicine, payment, inquiry, other
MT1 (대형마트)  → find_item, payment, exchange_refund, inquiry, other
CS2 (편의점)    → find_item, payment, exchange_refund, inquiry, other
BK9 (은행)      → inquiry, other
SW8 (지하철역)  → inquiry, other
AD5 (숙박)      → reservation, payment, inquiry, other
AT4 (관광명소)  → inquiry, other
GEN (일반)      → inquiry, other
```

---

## 스레드 기반 대화 관리

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Translation Thread                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  id: UUID                                                                   │
│  profile_id: UUID (사용자)                                                  │
│  primary_category: "FD6" (음식점)                                           │
│  sub_category: "ordering" (주문)                                            │
│  created_at: datetime                                                       │
│  deleted_at: datetime (soft delete)                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Translations (연결된 번역 기록들)                                           │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ [1] "I'd like to order bulgogi" → "불고기 주문하고 싶어요"              │ │
│  │ [2] "Two servings please" → "2인분 주세요"                             │ │
│  │ [3] "Can I get more side dishes?" → "반찬 더 주실 수 있나요?"          │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## API 엔드포인트

### 번역 API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/translate/text` | 텍스트 번역 |
| POST | `/translate/voice` | 음성 번역 (STT → 번역 → TTS) |
| GET | `/translations` | 번역 기록 목록 |
| DELETE | `/translations/{id}` | 번역 기록 삭제 |

### 스레드 API

| Method | Path | Description |
|--------|------|-------------|
| POST | `/translation/threads` | 스레드 생성 |
| GET | `/translation/threads` | 스레드 목록 |
| GET | `/translation/threads/{id}` | 스레드 상세 (번역 기록 포함) |
| DELETE | `/translation/threads/{id}` | 스레드 삭제 (soft delete) |

### 카테고리 API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/translation/categories` | 카테고리 목록 + 매핑 |

---

## 디렉토리 구조

```
src/modules/translations/
├── __init__.py                 # 라우터 등록
├── translate_text.py           # POST /translate/text
├── translate_voice.py          # POST /translate/voice
├── list.py                     # GET /translations
├── delete.py                   # DELETE /translations/{id}
├── threads_create.py           # POST /translation/threads
├── threads_list.py             # GET /translation/threads
├── threads_detail.py           # GET /translation/threads/{id}
├── threads_delete.py           # DELETE /translation/threads/{id}
├── categories_list.py          # GET /translation/categories
├── _use_cases.py               # Use Cases (비즈니스 로직)
├── _models.py                  # Domain Models
├── _repository.py              # DB 접근
├── _exceptions.py              # Domain Exceptions
├── _context_service.py         # 컨텍스트 프롬프트 빌드
└── _translation_service.py     # 외부 API 호출

src/external/translation/
├── __init__.py                 # get_translation_provider(), get_vertex_provider()
├── base.py                     # ITranslationProvider 인터페이스
├── google_provider.py          # Google Translation API v3
└── vertex_provider.py          # Vertex AI (Gemini) - 컨텍스트 번역
```

---

## 환경 변수

| 변수 | 설명 | 필수 |
|------|------|------|
| `GOOGLE_CLOUD_PROJECT` | GCP 프로젝트 ID | Yes |
| `GOOGLE_CREDENTIALS_JSON` | 서비스 계정 JSON (서버용) | Yes (서버) |
| `SUPABASE_URL` | Supabase 프로젝트 URL | Yes |
| `SUPABASE_SERVICE_KEY` | Supabase 서비스 키 | Yes |

---

## 의존성

```toml
# pyproject.toml
google-cloud-aiplatform = ">=1.38.0"   # Vertex AI (Gemini)
google-cloud-speech = ">=2.36.0"       # STT
google-cloud-texttospeech = ">=2.34.0" # TTS
google-cloud-translate = ">=3.24.0"    # Translation API
supabase = ">=2.0.0"                   # Storage
```
