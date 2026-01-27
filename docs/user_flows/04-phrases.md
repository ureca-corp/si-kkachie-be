# Recommended Phrases

## Overview

Kkachie provides a curated collection of useful Korean phrases for travelers. Phrases are categorized and linked to mission steps for contextual recommendations.

## Phrase Categories

| Category | Korean | Description | Example |
|----------|--------|-------------|---------|
| greeting | 인사 | Greetings | 안녕하세요 (Hello) |
| request | 요청 | Making requests | 여기로 가주세요 (Please take me here) |
| confirmation | 확인 | Confirming information | 얼마예요? (How much?) |
| thanks | 감사 | Expressing gratitude | 감사합니다 (Thank you) |
| apology | 사과 | Apologizing | 죄송합니다 (I'm sorry) |
| emergency | 긴급 상황 | Emergency situations | 도와주세요! (Help!) |

## User Flow Diagram

```
+-------------------+
|  Phrases List     |
|  (All/Category)   |
+--------+----------+
         |
    +----+----+
    |         |
    v         v
+-------+ +-------+
| Filter| | Search|
|  by   | |       |
|Category|       |
+---+---+ +---+---+
    |         |
    +----+----+
         |
         v
+-------------------+
|  Phrase Card      |
|  - Korean text    |
|  - English text   |
|  - [Speak] [Copy] |
+--------+----------+
         |
         v (optional)
+-------------------+
|  Usage Tracking   |
+-------------------+
```

## Screen Mockups

### Phrases List Screen
```
+---------------------------+
|  <  Phrases               |
+---------------------------+
| [All][Greeting][Request]  |
| [Confirm][Thanks][Emerge] |
+---------------------------+
|                           |
| Greeting                  |
| +------------------------+|
| | 안녕하세요              ||
| | Hello                  ||
| | Used 150 times         ||
| |    [TTS] [Copy] [Use]  ||
| +------------------------+|
|                           |
| Request                   |
| +------------------------+|
| | 여기로 가주세요         ||
| | Please take me here    ||
| | Used 98 times          ||
| |    [TTS] [Copy] [Use]  ||
| +------------------------+|
|                           |
| +------------------------+|
| | 택시!                   ||
| | Taxi!                  ||
| | Used 76 times          ||
| |    [TTS] [Copy] [Use]  ||
| +------------------------+|
|                           |
+---------------------------+
```

### Mission Step with Phrases
```
+---------------------------+
|  <  Step 1: Hailing Taxi  |
+---------------------------+
|                           |
|  How to stop a taxi       |
|  on the street            |
|                           |
|  Recommended Phrases:     |
|  +------------------------+
|  | 택시!                  |
|  | Taxi!                  |
|  |        [TTS] [Copy]    |
|  +------------------------+
|                           |
|  +------------------------+
|  | 빈차예요?              |
|  | Are you available?     |
|  |        [TTS] [Copy]    |
|  +------------------------+
|                           |
|  [Or translate your own]  |
|                           |
+---------------------------+
```

### Phrase Detail (Quick View)
```
+---------------------------+
|         Phrase            |
+---------------------------+
|                           |
|      안녕하세요           |
|                           |
|      Hello                |
|                           |
|  +-------------------+    |
|  |   [Speaker] TTS   |    |
|  +-------------------+    |
|                           |
|  +-------------------+    |
|  |   [Copy] Korean   |    |
|  +-------------------+    |
|                           |
|  +-------------------+    |
|  |   [Copy] English  |    |
|  +-------------------+    |
|                           |
|  Category: Greeting       |
|  Used: 150 times          |
|                           |
+---------------------------+
```

## API Endpoints

### 1. Get Phrases (GET /phrases)

Returns filtered list of recommended phrases.

**Request:**
```bash
# Get all phrases
curl -X GET "https://api.kkachie.com/phrases" \
  -H "Authorization: Bearer {token}"

# Filter by category
curl -X GET "https://api.kkachie.com/phrases?category=greeting" \
  -H "Authorization: Bearer {token}"

# Get phrases for a specific mission step
curl -X GET "https://api.kkachie.com/phrases?mission_step_id=018d5c4f-step-xxxx" \
  -H "Authorization: Bearer {token}"
```

**Query Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| category | string | Filter by category (greeting, request, etc.) |
| mission_step_id | string | Get phrases linked to a mission step |

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "조회에 성공했어요",
  "data": [
    {
      "id": "018d5c4f-phr1-xxxx-xxxx-xxxxxxxxxxxx",
      "text_ko": "안녕하세요",
      "text_en": "Hello",
      "category": "greeting",
      "usage_count": 150
    },
    {
      "id": "018d5c4f-phr2-xxxx-xxxx-xxxxxxxxxxxx",
      "text_ko": "감사합니다",
      "text_en": "Thank you",
      "category": "thanks",
      "usage_count": 120
    },
    {
      "id": "018d5c4f-phr3-xxxx-xxxx-xxxxxxxxxxxx",
      "text_ko": "택시!",
      "text_en": "Taxi!",
      "category": "request",
      "usage_count": 76
    }
  ]
}
```

---

### 2. Record Phrase Usage (POST /phrases/{id}/use)

Records that a phrase was used, incrementing its usage count.

**Request:**
```bash
curl -X POST "https://api.kkachie.com/phrases/018d5c4f-phr1-xxxx-xxxx-xxxxxxxxxxxx/use" \
  -H "Authorization: Bearer {token}"
```

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "사용이 기록됐어요",
  "data": {
    "id": "018d5c4f-phr1-xxxx-xxxx-xxxxxxxxxxxx",
    "usage_count": 151
  }
}
```

## TypeScript Types

```typescript
// Phrase Categories
type PhraseCategory =
  | "greeting"
  | "request"
  | "confirmation"
  | "thanks"
  | "apology"
  | "emergency";

// Phrase Response
interface PhraseResponse {
  id: string;
  text_ko: string;
  text_en: string;
  category: PhraseCategory;
  usage_count: number;
}

// Phrase Use Response
interface PhraseUseResponse {
  id: string;
  usage_count: number;
}
```

## React Native Implementation Example

```typescript
import * as Clipboard from 'expo-clipboard';
import * as Speech from 'expo-speech';

// Get Phrases
async function getPhrases(
  category?: PhraseCategory,
  missionStepId?: string
): Promise<PhraseResponse[]> {
  const params = new URLSearchParams();
  if (category) params.append('category', category);
  if (missionStepId) params.append('mission_step_id', missionStepId);

  const query = params.toString();
  return apiClient<PhraseResponse[]>(`/phrases${query ? `?${query}` : ''}`);
}

// Record Phrase Usage
async function usePhrase(phraseId: string): Promise<PhraseUseResponse> {
  return apiClient<PhraseUseResponse>(`/phrases/${phraseId}/use`, {
    method: 'POST',
  });
}

// Speak Korean Text (TTS)
function speakKorean(text: string): void {
  Speech.speak(text, {
    language: 'ko-KR',
    rate: 0.9,
  });
}

// Copy Text to Clipboard
async function copyToClipboard(text: string): Promise<void> {
  await Clipboard.setStringAsync(text);
}

// Phrase Card Component
function PhraseCard({ phrase }: { phrase: PhraseResponse }) {
  const handleSpeak = () => {
    speakKorean(phrase.text_ko);
    usePhrase(phrase.id); // Track usage
  };

  const handleCopy = async () => {
    await copyToClipboard(phrase.text_ko);
    usePhrase(phrase.id); // Track usage
  };

  return (
    <View style={styles.card}>
      <Text style={styles.korean}>{phrase.text_ko}</Text>
      <Text style={styles.english}>{phrase.text_en}</Text>
      <View style={styles.actions}>
        <TouchableOpacity onPress={handleSpeak}>
          <Text>Speak</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={handleCopy}>
          <Text>Copy</Text>
        </TouchableOpacity>
      </View>
      <Text style={styles.usage}>Used {phrase.usage_count} times</Text>
    </View>
  );
}

// Phrases Screen with Category Filter
function PhrasesScreen() {
  const [phrases, setPhrases] = useState<PhraseResponse[]>([]);
  const [category, setCategory] = useState<PhraseCategory | undefined>();

  useEffect(() => {
    getPhrases(category).then(setPhrases);
  }, [category]);

  const categories: PhraseCategory[] = [
    'greeting',
    'request',
    'confirmation',
    'thanks',
    'apology',
    'emergency',
  ];

  return (
    <View>
      <ScrollView horizontal>
        <TouchableOpacity onPress={() => setCategory(undefined)}>
          <Text>All</Text>
        </TouchableOpacity>
        {categories.map((cat) => (
          <TouchableOpacity
            key={cat}
            onPress={() => setCategory(cat)}
          >
            <Text>{cat}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      <FlatList
        data={phrases}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <PhraseCard phrase={item} />}
      />
    </View>
  );
}
```

## Seed Data (Pre-loaded Phrases)

The following phrases are pre-loaded in the database:

| Korean | English | Category |
|--------|---------|----------|
| 안녕하세요 | Hello | greeting |
| 감사합니다 | Thank you | thanks |
| 택시! | Taxi! | request |
| 여기로 가주세요 | Please take me here | request |
| 얼마예요? | How much is it? | confirmation |
| 카드로 결제할게요 | I'll pay by card | request |
| 예약했어요 | I have a reservation | confirmation |
| 죄송합니다 | I'm sorry | apology |
| 도와주세요! | Please help me! | emergency |

## Error Handling

| Status Code | Error Status | Message | Action |
|-------------|--------------|---------|--------|
| 404 | PHRASE_NOT_FOUND | 문장을 찾을 수 없어요 | Check phrase ID |

## Best Practices

1. **Caching**: Cache phrases locally since they rarely change
2. **TTS Quality**: Use native device TTS for Korean pronunciation
3. **Usage Analytics**: Track phrase usage to improve recommendations
4. **Sorting**: Sort by usage_count for "Popular" tab
5. **Context**: Show relevant phrases based on active mission step
6. **Offline Mode**: Make phrases available offline for use without internet
7. **Haptic Feedback**: Add haptic feedback when copying to clipboard
