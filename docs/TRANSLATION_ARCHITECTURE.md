# Translation Voice API Architecture

음성 번역 API (`/translate/voice`)의 전체 아키텍처와 데이터 흐름을 설명합니다.

## 전체 흐름

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        /translate/voice API 전체 흐름                            │
└─────────────────────────────────────────────────────────────────────────────────┘

┌──────────┐     POST /translate/voice      ┌──────────────────────────────────────┐
│  Client  │  ─────────────────────────────▶│  translate_voice.py                  │
│ (App/Web)│    • audio_file (WAV)          │  ┌──────────────────────────────────┐│
│          │    • sourceLang: "en"          │  │ translate_voice() endpoint       ││
│          │    • targetLang: "ko"          │  └──────────────────────────────────┘│
└──────────┘                                └───────────────┬──────────────────────┘
     ▲                                                      │
     │                                                      ▼
     │                                      ┌──────────────────────────────────────┐
     │                                      │ create_voice_translation()           │
     │                                      │                                      │
     │                                      │  Step 1: STT (Speech-to-Text)        │
     │                                      │  Step 2: Translation                 │
     │                                      │  Step 3: TTS (Text-to-Speech)        │
     │                                      └───────────────┬──────────────────────┘
     │                                                      │
     │                                                      ▼
     │  ┌───────────────────────────────────────────────────────────────────────────┐
     │  │                    _translation_service.py (핵심 서비스)                   │
     │  └───────────────────────────────────────────────────────────────────────────┘
     │                         │                    │                    │
     │                         ▼                    ▼                    ▼
     │  ┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────┐
     │  │ speech_to_text()        │  │ translate()             │  │ text_to_speech()        │
     │  │                         │  │                         │  │                         │
     │  │ Input:                  │  │ Input:                  │  │ Input:                  │
     │  │  • audio_data (bytes)   │  │  • text: "Hello"        │  │  • text: "안녕하세요"    │
     │  │  • language: "en"       │  │  • source: "en"         │  │  • language: "ko"       │
     │  │                         │  │  • target: "ko"         │  │                         │
     │  │ Output:                 │  │                         │  │ Output:                 │
     │  │  • text: "Hello"        │  │ Output:                 │  │  • audio_url            │
     │  │  • confidence: 0.95     │  │  • "안녕하세요"          │  │  • duration_ms          │
     │  └────────────┬────────────┘  └────────────┬────────────┘  └────────────┬────────────┘
     │               │                            │                            │
     │               ▼                            ▼                            ▼
     │  ┌───────────────────────────────────────────────────────────────────────────┐
     │  │                         External Providers                                │
     │  │  ┌─────────────────────────────────────────────────────────────────────┐  │
     │  │  │                    src/external/ 모듈 구조                           │  │
     │  │  │                                                                     │  │
     │  │  │  ┌──────────────┐   ┌──────────────┐   ┌──────────────────────────┐ │  │
     │  │  │  │   speech/    │   │ translation/ │   │       storage/           │ │  │
     │  │  │  │              │   │              │   │                          │ │  │
     │  │  │  │ Google STT   │   │ Google       │   │  Supabase Storage        │ │  │
     │  │  │  │ Google TTS   │   │ Translation  │   │  (profiles 버킷)          │ │  │
     │  │  │  │              │   │ v3 API       │   │                          │ │  │
     │  │  │  └──────┬───────┘   └──────┬───────┘   └────────────┬─────────────┘ │  │
     │  │  └─────────┼──────────────────┼────────────────────────┼───────────────┘  │
     │  └────────────┼──────────────────┼────────────────────────┼─────────────────┘
     │               │                  │                        │
     │               ▼                  ▼                        ▼
     │  ┌───────────────────────────────────────────────────────────────────────────┐
     │  │                         Google Cloud Platform                             │
     │  │  ┌─────────────────┐  ┌─────────────────┐                                 │
     │  │  │ Speech-to-Text  │  │ Translation     │        ┌─────────────────────┐  │
     │  │  │ API             │  │ API v3          │        │ Supabase            │  │
     │  │  │                 │  │                 │        │ Storage             │  │
     │  │  │ "Hello" ◀──────┐│  │ "Hello"         │        │                     │  │
     │  │  │                ││  │    ↓            │        │ tts/{uuid}.mp3      │  │
     │  │  │ [Audio WAV]────┘│  │ "안녕하세요"     │        │         ↓           │  │
     │  │  │                 │  │                 │        │  Public URL 반환    │  │
     │  │  └─────────────────┘  └─────────────────┘        └─────────────────────┘  │
     │  └───────────────────────────────────────────────────────────────────────────┘
     │
     │  ┌───────────────────────────────────────────────────────────────────────────┐
     │  │                              Response                                     │
     │  │  {                                                                        │
     │  │    "originalText": "Hello",                                               │
     │  │    "translatedText": "안녕하세요",                                          │
     │  │    "sourceLang": "en",                                                    │
     │  │    "targetLang": "ko",                                                    │
     │  │    "audioUrl": "https://xxx.supabase.co/storage/v1/.../tts/uuid.mp3",     │
     │  │    "audioDurationMs": 1500                                                │
     │  │  }                                                                        │
     └──└───────────────────────────────────────────────────────────────────────────┘
```

## 디렉토리 구조

```
src/
├── modules/
│   └── translations/
│       ├── translate_voice.py        # API 엔드포인트
│       └── _translation_service.py   # 핵심 비즈니스 로직
│
└── external/
    ├── speech/
    │   ├── __init__.py               # get_speech_provider()
    │   ├── base.py                   # ISpeechProvider 인터페이스
    │   └── google_provider.py        # Google Cloud STT/TTS 구현
    │
    ├── translation/
    │   ├── __init__.py               # get_translation_provider()
    │   ├── base.py                   # ITranslationProvider 인터페이스
    │   └── google_provider.py        # Google Cloud Translation 구현
    │
    └── storage/
        ├── __init__.py               # get_storage_provider()
        ├── base.py                   # IStorageProvider 인터페이스
        └── supabase_provider.py      # Supabase Storage 구현
```

## Provider 선택 로직 (Strategy Pattern)

```
                    ┌─────────────────────────────────────┐
                    │       get_speech_provider()         │
                    │       get_translation_provider()    │
                    └─────────────────┬───────────────────┘
                                      │
                    ┌─────────────────┴───────────────────┐
                    │                                     │
                    ▼                                     ▼
    ┌───────────────────────────────┐    ┌───────────────────────────────┐
    │  Credentials 있음              │    │  Credentials 없음              │
    │  (GOOGLE_CLOUD_PROJECT +      │    │                               │
    │   GOOGLE_CREDENTIALS_JSON)    │    │                               │
    └───────────────┬───────────────┘    └───────────────┬───────────────┘
                    │                                     │
                    ▼                                     ▼
    ┌───────────────────────────────┐    ┌───────────────────────────────┐
    │  GoogleSpeechProvider         │    │  Mock Response (Fallback)     │
    │  GoogleTranslationProvider    │    │                               │
    │                               │    │  "en" → "Hello"               │
    │  실제 API 호출                 │    │  "ko" → "안녕하세요"            │
    └───────────────────────────────┘    └───────────────────────────────┘
```

### Provider 인터페이스

**ISpeechProvider** (`src/external/speech/base.py`)
```python
class ISpeechProvider(ABC):
    @abstractmethod
    def speech_to_text(self, audio_data: bytes, language: str) -> dict:
        """음성 → 텍스트 변환"""
        pass

    @abstractmethod
    def text_to_speech(self, text: str, language: str) -> dict:
        """텍스트 → 음성 변환"""
        pass
```

**ITranslationProvider** (`src/external/translation/base.py`)
```python
class ITranslationProvider(ABC):
    @abstractmethod
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """텍스트 번역"""
        pass
```

## 인증 흐름 (Credentials)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              config.py                                      │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  GOOGLE_CLOUD_PROJECT: str | None      # 프로젝트 ID                   │ │
│  │  GOOGLE_CREDENTIALS_JSON: str | None   # JSON 문자열 (서버용)          │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         _get_credentials()                                  │
│                                                                             │
│   if GOOGLE_CREDENTIALS_JSON:                                               │
│       ─────────────────────────────▶  JSON 파싱 → Credentials 객체          │
│                                       (Render 서버 환경)                     │
│   else:                                                                     │
│       ─────────────────────────────▶  None 반환 → ADC 사용                   │
│                                       (로컬 개발 환경)                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 환경별 인증 방식

| 환경 | 인증 방식 | 설정 |
|------|----------|------|
| 로컬 개발 | ADC (Application Default Credentials) | `gcloud auth application-default login` |
| Render 서버 | JSON 문자열 | `GOOGLE_CREDENTIALS_JSON` 환경변수 |

## Supabase Storage 구조

```
Supabase Project: kkachie (cuihfzfmyhczgnsfauud)
│
└── Storage
    │
    └── Bucket: profiles (public: true)
        │
        └── tts/
            ├── {uuid1}.mp3   ◀── TTS 결과 오디오 파일
            ├── {uuid2}.mp3
            └── ...
```

### RLS Policies (storage.objects)

| Policy Name | Command | Role / Condition |
|-------------|---------|------------------|
| Allow service role uploads | INSERT | service_role |
| Allow service role downloads | SELECT | service_role |
| Allow public downloads | SELECT | public |
| Allow anon uploads to tts | INSERT | anon (tts 폴더만) |
| Allow authenticated uploads | INSERT | authenticated |

## 언어 코드 정규화

### Speech API (BCP-47 형식)

```python
LANGUAGE_MAP = {
    "en": "en-US",
    "ko": "ko-KR",
    "ja": "ja-JP",
    "zh": "zh-CN",
    "es": "es-ES",
    "fr": "fr-FR",
    "de": "de-DE",
}
```

### Translation API (ISO 639-1 형식)

```python
# BCP-47 → ISO 639-1 변환
"en-US" → "en"
"ko-KR" → "ko"
```

## API 스펙

### Request

```http
POST /translate/voice
Content-Type: multipart/form-data

audio_file: <WAV 파일>
sourceLang: "en"
targetLang: "ko"
```

### Response

```json
{
  "originalText": "Hello",
  "translatedText": "안녕하세요",
  "sourceLang": "en",
  "targetLang": "ko",
  "audioUrl": "https://cuihfzfmyhczgnsfauud.supabase.co/storage/v1/object/public/profiles/tts/abc123.mp3",
  "audioDurationMs": 1500
}
```

## 오디오 형식 지원

### STT (Speech-to-Text)

- **지원 형식**: WAV, MP3, FLAC, OGG
- **인코딩**: 자동 감지 (`ENCODING_UNSPECIFIED`)
- **샘플레이트**: WAV 헤더에서 자동 감지
- **채널**: 모노/스테레오 모두 지원 (`audio_channel_count=2`)

### TTS (Text-to-Speech)

- **출력 형식**: MP3
- **음성 성별**: NEUTRAL (기본)

## 에러 처리

| 에러 | 원인 | 해결 |
|------|------|------|
| `DefaultCredentialsError` | 인증 정보 없음 | `GOOGLE_CREDENTIALS_JSON` 설정 |
| `InvalidArgument: sample_rate_hertz` | 샘플레이트 불일치 | 자동 감지 사용 (파라미터 제거) |
| `InvalidArgument: Must use single channel` | 스테레오 오디오 | `audio_channel_count=2` 설정 |
| `StorageApiError: Bucket not found` | 버킷 없음 | Supabase에서 버킷 생성 |
| `StorageApiError: row-level security policy` | RLS 정책 없음 | Storage RLS 정책 추가 |

## 의존성

```toml
# pyproject.toml
google-cloud-speech = "^2.x"
google-cloud-translate = "^3.x"
google-cloud-texttospeech = "^2.x"
supabase = "^2.x"
```
