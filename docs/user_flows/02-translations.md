# Translation Features

## Overview

Kkachie provides real-time text and voice translation between Korean and English using Google Cloud APIs (Translation, Speech-to-Text, Text-to-Speech).

## User Flow Diagram

```
+-------------------+
|  Translation      |
|  Screen           |
+--------+----------+
         |
    +----+----+
    |         |
    v         v
+-------+ +-------+
| Text  | | Voice |
| Mode  | | Mode  |
+---+---+ +---+---+
    |         |
    v         v
+-------+ +-------+
| POST  | | POST  |
|/text  | |/voice |
+---+---+ +---+---+
    |         |
    +----+----+
         |
         v
+-------------------+
|  Translation      |
|  Result           |
|  (+ TTS Audio)    |
+-------------------+
         |
         v
+-------------------+
|  Save to          |
|  History          |
+-------------------+
```

## Screen Mockups

### Translation Screen (Text Mode)
```
+---------------------------+
|  <  Translate             |
+---------------------------+
|                           |
|  [Korean] --> [English]   |
|      v           v        |
|  +-------------------+    |
|  |                   |    |
|  | Enter text here   |    |
|  |                   |    |
|  +-------------------+    |
|                           |
|  +-------------------+    |
|  |    Translate      |    |
|  +-------------------+    |
|                           |
|  +-------------------+    |
|  |                   |    |
|  | Translation will  |    |
|  | appear here       |    |
|  |         [Speaker] |    |
|  +-------------------+    |
|                           |
+---------------------------+
```

### Translation Screen (Voice Mode)
```
+---------------------------+
|  <  Translate             |
+---------------------------+
|                           |
|  [Korean] --> [English]   |
|                           |
|      +----------+         |
|      |          |         |
|      |   Mic    |         |
|      |          |         |
|      +----------+         |
|   Hold to record voice    |
|                           |
|  +-------------------+    |
|  | Recognized:       |    |
|  | "안녕하세요"       |    |
|  +-------------------+    |
|                           |
|  +-------------------+    |
|  | Translation:      |    |
|  | "Hello"           |    |
|  |         [Speaker] |    |
|  +-------------------+    |
|                           |
+---------------------------+
```

### Translation History Screen
```
+---------------------------+
|  <  History               |
+---------------------------+
| [All] [Text] [Voice]      |
+---------------------------+
|                           |
| Today                     |
| +------------------------+|
| | 안녕하세요 -> Hello    ||
| | 10:30 AM    [Text]     ||
| +------------------------+|
|                           |
| +------------------------+|
| | 감사합니다 -> Thank you||
| | 10:15 AM    [Voice]    ||
| +------------------------+|
|                           |
| Yesterday                 |
| +------------------------+|
| | 택시! -> Taxi!         ||
| | 3:45 PM     [Text]     ||
| +------------------------+|
|                           |
+---------------------------+
```

## API Endpoints

### 1. Text Translation (POST /translate/text)

Translates text between Korean and English.

**Request:**
```bash
curl -X POST "https://api.kkachie.com/translate/text" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "source_text": "안녕하세요",
    "source_lang": "ko",
    "target_lang": "en",
    "mission_progress_id": null
  }'
```

**Request Body:**
```typescript
interface TextTranslateRequest {
  source_text: string;        // 1-5000 characters
  source_lang: "ko" | "en";
  target_lang: "ko" | "en";   // Must differ from source_lang
  mission_progress_id?: string; // Optional: link to active mission
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
    "mission_progress_id": null,
    "created_at": "2026-01-27T10:00:00Z"
  }
}
```

---

### 2. Voice Translation (POST /translate/voice)

Converts speech to text, translates, and generates audio output.

**Request:**
```bash
curl -X POST "https://api.kkachie.com/translate/voice" \
  -H "Authorization: Bearer {token}" \
  -F "audio_file=@recording.wav" \
  -F "source_lang=ko" \
  -F "target_lang=en" \
  -F "mission_progress_id="
```

**Form Data:**
```typescript
interface VoiceTranslateRequest {
  audio_file: File;           // Audio file (WAV, MP3, etc.)
  source_lang: "ko" | "en";
  target_lang: "ko" | "en";   // Must differ from source_lang
  mission_progress_id?: string;
}
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
    "mission_progress_id": null,
    "audio_url": "https://storage.supabase.co/.../tts/abc123.mp3",
    "duration_ms": 1500,
    "confidence_score": 0.95,
    "created_at": "2026-01-27T10:00:00Z"
  }
}
```

---

### 3. Get Translation History (GET /translations)

Retrieves paginated translation history.

**Request:**
```bash
curl -X GET "https://api.kkachie.com/translations?page=1&limit=20&type=text" \
  -H "Authorization: Bearer {token}"
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| page | number | 1 | Page number |
| limit | number | 20 | Items per page (max: 100) |
| type | string | - | Filter by type: `text` or `voice` |
| mission_progress_id | string | - | Filter by mission |

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
      },
      {
        "id": "018d5c4f-yyyy-7yyy-yyyy-yyyyyyyyyyyy",
        "source_text": "감사합니다",
        "translated_text": "Thank you",
        "source_lang": "ko",
        "target_lang": "en",
        "translation_type": "voice",
        "audio_url": "https://storage.supabase.co/.../tts/def456.mp3",
        "duration_ms": 1200,
        "confidence_score": 0.92,
        "created_at": "2026-01-27T09:45:00Z"
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

### 4. Delete Translation (DELETE /translations/{id})

Deletes a translation record from history.

**Request:**
```bash
curl -X DELETE "https://api.kkachie.com/translations/018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx" \
  -H "Authorization: Bearer {token}"
```

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "번역 기록이 삭제됐어요"
}
```

## TypeScript Types

```typescript
// Translation Response
interface TranslationResponse {
  id: string;
  source_text: string;
  translated_text: string;
  source_lang: "ko" | "en";
  target_lang: "ko" | "en";
  translation_type: "text" | "voice";
  mission_progress_id?: string | null;
  audio_url?: string | null;      // Only for voice
  duration_ms?: number | null;    // Only for voice
  confidence_score?: number | null; // Only for voice (0-1)
  created_at: string;
}

// Translation List Response
interface TranslationListResponse {
  items: TranslationResponse[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    total_pages: number;
  };
}

// Text Translation Request
interface TextTranslateRequest {
  source_text: string;
  source_lang: "ko" | "en";
  target_lang: "ko" | "en";
  mission_progress_id?: string;
}
```

## React Native Implementation Example

```typescript
import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';

// Text Translation
async function translateText(
  sourceText: string,
  sourceLang: 'ko' | 'en',
  targetLang: 'ko' | 'en',
  missionProgressId?: string
): Promise<TranslationResponse> {
  return apiClient<TranslationResponse>('/translate/text', {
    method: 'POST',
    body: JSON.stringify({
      source_text: sourceText,
      source_lang: sourceLang,
      target_lang: targetLang,
      mission_progress_id: missionProgressId || null,
    }),
  });
}

// Voice Translation
async function translateVoice(
  audioUri: string,
  sourceLang: 'ko' | 'en',
  targetLang: 'ko' | 'en',
  missionProgressId?: string
): Promise<TranslationResponse> {
  const { data: { session } } = await supabase.auth.getSession();

  const formData = new FormData();
  formData.append('audio_file', {
    uri: audioUri,
    type: 'audio/wav',
    name: 'recording.wav',
  } as any);
  formData.append('source_lang', sourceLang);
  formData.append('target_lang', targetLang);
  if (missionProgressId) {
    formData.append('mission_progress_id', missionProgressId);
  }

  const response = await fetch(`${API_BASE}/translate/voice`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${session?.access_token}`,
    },
    body: formData,
  });

  const data = await response.json();
  if (data.status !== 'SUCCESS') {
    throw new Error(data.message);
  }
  return data.data;
}

// Play TTS Audio
async function playTranslationAudio(audioUrl: string): Promise<void> {
  const { sound } = await Audio.Sound.createAsync(
    { uri: audioUrl },
    { shouldPlay: true }
  );

  sound.setOnPlaybackStatusUpdate((status) => {
    if (status.didJustFinish) {
      sound.unloadAsync();
    }
  });
}

// Get Translation History
async function getTranslationHistory(
  page: number = 1,
  limit: number = 20,
  type?: 'text' | 'voice'
): Promise<TranslationListResponse> {
  const params = new URLSearchParams({
    page: page.toString(),
    limit: limit.toString(),
  });
  if (type) params.append('type', type);

  return apiClient<TranslationListResponse>(
    `/translations?${params.toString()}`
  );
}

// Delete Translation
async function deleteTranslation(id: string): Promise<void> {
  await apiClient(`/translations/${id}`, { method: 'DELETE' });
}
```

## Voice Recording Example (React Native)

```typescript
import { Audio } from 'expo-av';

const [recording, setRecording] = useState<Audio.Recording | null>(null);

// Start Recording
async function startRecording() {
  const { granted } = await Audio.requestPermissionsAsync();
  if (!granted) {
    alert('Microphone permission required');
    return;
  }

  await Audio.setAudioModeAsync({
    allowsRecordingIOS: true,
    playsInSilentModeIOS: true,
  });

  const { recording } = await Audio.Recording.createAsync(
    Audio.RecordingOptionsPresets.HIGH_QUALITY
  );
  setRecording(recording);
}

// Stop Recording and Translate
async function stopRecording() {
  if (!recording) return;

  await recording.stopAndUnloadAsync();
  const uri = recording.getURI();
  setRecording(null);

  if (uri) {
    const result = await translateVoice(uri, 'ko', 'en');
    // Handle translation result
  }
}
```

## Error Handling

| Status Code | Error Status | Message | Action |
|-------------|--------------|---------|--------|
| 400 | ERROR_INVALID_AUDIO | 잘못된 오디오 파일이에요 | Check audio format |
| 422 | VALIDATION_FAILED | 같은 언어로는 번역할 수 없어요 | Change target language |
| 422 | VALIDATION_FAILED | 번역할 텍스트를 입력해주세요 | Enter source text |
| 404 | ERROR_NOT_FOUND | - | Translation not found |

## Best Practices

1. **Text Validation**: Validate text length (1-5000 chars) before API call
2. **Audio Format**: Use WAV or MP3 for best compatibility
3. **Progress Indicator**: Show loading state during voice processing
4. **Offline Support**: Queue translations when offline, sync when online
5. **TTS Caching**: Cache TTS audio locally for repeated playback
6. **Error Recovery**: Retry failed voice translations with text input option
