# Mission System

## Overview

Kkachie's mission system provides step-by-step guidance for common travel scenarios in Korea. Each mission includes recommended phrases and translation integration.

## Mission Types

| Type | Korean | English | Steps | Duration |
|------|--------|---------|-------|----------|
| taxi | 택시 이용하기 | Taking a Taxi | 5 | ~15 min |
| payment | 결제하기 | Making Payment | 4 | ~10 min |
| checkin | 체크인하기 | Hotel Check-in | 4 | ~10 min |

## Mission Status Flow

```
+---------------+     Start      +---------------+
|               |--------------->|               |
|  not_started  |                |  in_progress  |
|               |                |               |
+---------------+                +-------+-------+
                                        |
                                        | End (with result)
                                        |
                                        v
                                +---------------+
                                |               |
                                |    ended      |
                                |  (resolved/   |
                                |  partial/     |
                                |  unresolved)  |
                                +---------------+
```

## User Flow Diagram

```
+-------------------+
|  Mission List     |
+--------+----------+
         |
         v Select
+-------------------+
|  Mission Detail   |
|  (with steps)     |
+--------+----------+
         |
         v Start
+-------------------+
|  Step 1           |
|  + Phrases        |
|  + Translation    |
+--------+----------+
         |
         v Complete Step
+-------------------+
|  Step 2, 3...     |
+--------+----------+
         |
         v End Mission
+-------------------+
|  Result Selection |
|  - Resolved       |
|  - Partial        |
|  - Unresolved     |
+-------------------+
```

## Screen Mockups

### Mission List Screen
```
+---------------------------+
|  <  Missions              |
+---------------------------+
|                           |
| +------------------------+|
| | [Taxi]                 ||
| | Taking a Taxi          ||
| | ~15 min | 5 steps      ||
| | [In Progress: 2/5]     ||
| +------------------------+|
|                           |
| +------------------------+|
| | [Card]                 ||
| | Making Payment         ||
| | ~10 min | 4 steps      ||
| | [Not Started]          ||
| +------------------------+|
|                           |
| +------------------------+|
| | [Hotel]                ||
| | Hotel Check-in         ||
| | ~10 min | 4 steps      ||
| | [Not Started]          ||
| +------------------------+|
|                           |
+---------------------------+
```

### Mission Detail Screen
```
+---------------------------+
|  <  Taking a Taxi         |
+---------------------------+
|                           |
|  Learn how to take a      |
|  taxi in Korea            |
|                           |
|  Duration: ~15 min        |
|                           |
|  Steps:                   |
|  [v] 1. Hailing a Taxi    |
|  [v] 2. Telling Destination|
|  [ ] 3. Checking Fare     |
|  [ ] 4. Making Payment    |
|  [ ] 5. Getting Off       |
|                           |
|  +-------------------+    |
|  |   Continue (3/5)  |    |
|  +-------------------+    |
|                           |
+---------------------------+
```

### Mission Step Screen
```
+---------------------------+
|  <  Step 3: Checking Fare |
+---------------------------+
|                           |
|  Ask the driver about     |
|  the fare before paying   |
|                           |
|  Recommended Phrases:     |
|  +------------------------+
|  | "얼마예요?"            |
|  | How much is it?        |
|  |        [Speak] [Copy]  |
|  +------------------------+
|  +------------------------+
|  | "카드 돼요?"           |
|  | Can I pay by card?     |
|  |        [Speak] [Copy]  |
|  +------------------------+
|                           |
|  [Translate Custom Text]  |
|                           |
|  +-------------------+    |
|  |   Complete Step   |    |
|  +-------------------+    |
|                           |
+---------------------------+
```

### Mission End Screen
```
+---------------------------+
|  <  End Mission           |
+---------------------------+
|                           |
|  How did your taxi        |
|  experience go?           |
|                           |
|  +------------------------+
|  | [check] Resolved       |
|  | Everything went well   |
|  +------------------------+
|                           |
|  +------------------------+
|  | [ ] Partially Resolved |
|  | Some issues but okay   |
|  +------------------------+
|                           |
|  +------------------------+
|  | [ ] Unresolved         |
|  | Couldn't complete      |
|  +------------------------+
|                           |
|  +-------------------+    |
|  |   Finish Mission  |    |
|  +-------------------+    |
|                           |
+---------------------------+
```

## API Endpoints

### 1. List Missions (GET /missions)

Returns all available missions with user's progress.

**Request:**
```bash
curl -X GET "https://api.kkachie.com/missions" \
  -H "Authorization: Bearer {token}"
```

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
        "id": "018d5c4f-yyyy-7yyy-yyyy-yyyyyyyyyyyy",
        "status": "in_progress",
        "current_step": 2,
        "started_at": "2026-01-27T09:00:00Z"
      }
    },
    {
      "id": "018d5c4f-aaaa-7aaa-aaaa-aaaaaaaaaaaa",
      "title": "Making Payment",
      "description": "Learn how to pay in Korean stores",
      "mission_type": "payment",
      "estimated_duration_min": 10,
      "icon_url": "https://storage.supabase.co/.../payment.png",
      "steps_count": 4,
      "user_progress": null
    }
  ]
}
```

---

### 2. Get Mission Detail (GET /missions/{id})

Returns mission details including steps and phrases.

**Request:**
```bash
curl -X GET "https://api.kkachie.com/missions/018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx" \
  -H "Authorization: Bearer {token}"
```

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
    "icon_url": "https://storage.supabase.co/.../taxi.png",
    "steps": [
      {
        "id": "018d5c4f-step-0001-xxxx-xxxxxxxxxxxx",
        "step_order": 1,
        "title": "Hailing a Taxi",
        "description": "How to stop a taxi on the street",
        "is_completed": true,
        "phrases": [
          {
            "id": "018d5c4f-phr1-xxxx-xxxx-xxxxxxxxxxxx",
            "text_ko": "택시!",
            "text_en": "Taxi!",
            "category": "request"
          }
        ]
      },
      {
        "id": "018d5c4f-step-0002-xxxx-xxxxxxxxxxxx",
        "step_order": 2,
        "title": "Telling Destination",
        "description": "How to tell the driver where to go",
        "is_completed": true,
        "phrases": [
          {
            "id": "018d5c4f-phr2-xxxx-xxxx-xxxxxxxxxxxx",
            "text_ko": "여기로 가주세요",
            "text_en": "Please take me here",
            "category": "request"
          }
        ]
      },
      {
        "id": "018d5c4f-step-0003-xxxx-xxxxxxxxxxxx",
        "step_order": 3,
        "title": "Checking Fare",
        "description": "Ask about the fare",
        "is_completed": false,
        "phrases": [
          {
            "id": "018d5c4f-phr3-xxxx-xxxx-xxxxxxxxxxxx",
            "text_ko": "얼마예요?",
            "text_en": "How much is it?",
            "category": "confirmation"
          }
        ]
      }
    ],
    "user_progress": {
      "id": "018d5c4f-prog-xxxx-xxxx-xxxxxxxxxxxx",
      "status": "in_progress",
      "current_step": 2,
      "started_at": "2026-01-27T09:00:00Z"
    }
  }
}
```

---

### 3. Start Mission (POST /missions/{id}/start)

Starts a new mission progress.

**Request:**
```bash
curl -X POST "https://api.kkachie.com/missions/018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx/start" \
  -H "Authorization: Bearer {token}"
```

**Response (201):**
```json
{
  "status": "SUCCESS",
  "message": "미션을 시작했어요",
  "data": {
    "progress_id": "018d5c4f-prog-xxxx-xxxx-xxxxxxxxxxxx",
    "mission_id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
    "status": "in_progress",
    "current_step": 1,
    "started_at": "2026-01-27T10:00:00Z"
  }
}
```

---

### 4. Update Progress (PATCH /missions/{id}/progress)

Marks a step as completed.

**Request:**
```bash
curl -X PATCH "https://api.kkachie.com/missions/018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx/progress" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "step_id": "018d5c4f-step-0003-xxxx-xxxxxxxxxxxx",
    "is_completed": true
  }'
```

**Request Body:**
```typescript
interface UpdateProgressRequest {
  step_id: string;
  is_completed: boolean;
}
```

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "단계를 완료했어요",
  "data": {
    "progress_id": "018d5c4f-prog-xxxx-xxxx-xxxxxxxxxxxx",
    "current_step": 3,
    "completed_steps": 3,
    "total_steps": 5
  }
}
```

---

### 5. End Mission (POST /missions/{id}/end)

Ends the mission with a result.

**Request:**
```bash
curl -X POST "https://api.kkachie.com/missions/018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx/end" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "result": "resolved"
  }'
```

**Request Body:**
```typescript
interface EndMissionRequest {
  result: "resolved" | "partially_resolved" | "unresolved";
}
```

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "미션을 종료했어요",
  "data": {
    "progress_id": "018d5c4f-prog-xxxx-xxxx-xxxxxxxxxxxx",
    "status": "ended",
    "result": "resolved",
    "ended_at": "2026-01-27T10:30:00Z",
    "duration_minutes": 30
  }
}
```

## TypeScript Types

```typescript
// Mission Types
type MissionType = "taxi" | "payment" | "checkin";
type MissionStatus = "not_started" | "in_progress" | "ended";
type MissionResult = "resolved" | "partially_resolved" | "unresolved";

// User Progress
interface UserProgressResponse {
  id?: string;
  status: MissionStatus;
  current_step: number;
  started_at?: string;
}

// Mission Step
interface MissionStepResponse {
  id: string;
  step_order: number;
  title: string;
  description: string;
  is_completed: boolean;
  phrases: PhraseResponse[];
}

// Mission List Item
interface MissionListItemResponse {
  id: string;
  title: string;
  description: string;
  mission_type: MissionType;
  estimated_duration_min: number;
  icon_url?: string;
  steps_count: number;
  user_progress?: UserProgressResponse | null;
}

// Mission Detail
interface MissionDetailResponse {
  id: string;
  title: string;
  description: string;
  mission_type: MissionType;
  estimated_duration_min: number;
  icon_url?: string;
  steps: MissionStepResponse[];
  user_progress?: UserProgressResponse | null;
}

// Mission Start Response
interface MissionStartResponse {
  progress_id: string;
  mission_id: string;
  status: MissionStatus;
  current_step: number;
  started_at: string;
}

// Mission Progress Update Response
interface MissionProgressUpdateResponse {
  progress_id: string;
  current_step: number;
  completed_steps: number;
  total_steps: number;
}

// Mission End Response
interface MissionEndResponse {
  progress_id: string;
  status: MissionStatus;
  result: MissionResult;
  ended_at: string;
  duration_minutes: number;
}
```

## React Native Implementation Example

```typescript
// Get Mission List
async function getMissions(): Promise<MissionListItemResponse[]> {
  return apiClient<MissionListItemResponse[]>('/missions');
}

// Get Mission Detail
async function getMissionDetail(
  missionId: string
): Promise<MissionDetailResponse> {
  return apiClient<MissionDetailResponse>(`/missions/${missionId}`);
}

// Start Mission
async function startMission(
  missionId: string
): Promise<MissionStartResponse> {
  return apiClient<MissionStartResponse>(`/missions/${missionId}/start`, {
    method: 'POST',
  });
}

// Complete Step
async function completeStep(
  missionId: string,
  stepId: string
): Promise<MissionProgressUpdateResponse> {
  return apiClient<MissionProgressUpdateResponse>(
    `/missions/${missionId}/progress`,
    {
      method: 'PATCH',
      body: JSON.stringify({
        step_id: stepId,
        is_completed: true,
      }),
    }
  );
}

// End Mission
async function endMission(
  missionId: string,
  result: MissionResult
): Promise<MissionEndResponse> {
  return apiClient<MissionEndResponse>(`/missions/${missionId}/end`, {
    method: 'POST',
    body: JSON.stringify({ result }),
  });
}

// Example: Mission Flow Hook
function useMissionFlow(missionId: string) {
  const [mission, setMission] = useState<MissionDetailResponse | null>(null);
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    getMissionDetail(missionId).then(setMission);
  }, [missionId]);

  const start = async () => {
    const result = await startMission(missionId);
    setCurrentStep(result.current_step);
  };

  const completeCurrentStep = async () => {
    if (!mission) return;
    const step = mission.steps[currentStep - 1];
    const result = await completeStep(missionId, step.id);
    setCurrentStep(result.current_step);
  };

  const finish = async (result: MissionResult) => {
    return endMission(missionId, result);
  };

  return { mission, currentStep, start, completeCurrentStep, finish };
}
```

## Error Handling

| Status Code | Error Status | Message | Action |
|-------------|--------------|---------|--------|
| 404 | MISSION_NOT_FOUND | 미션을 찾을 수 없어요 | Check mission ID |
| 409 | ERROR_MISSION_ALREADY_STARTED | 이미 진행 중인 미션이에요 | Continue existing |
| 400 | ERROR_MISSION_NOT_STARTED | 시작된 미션이 없어요 | Start mission first |
| 400 | ERROR_VALIDATION | 잘못된 결과 값이에요 | Use valid result enum |

## Best Practices

1. **Progress Persistence**: Mission progress is saved automatically, users can resume anytime
2. **Multiple Attempts**: Users can start the same mission multiple times (new progress each time)
3. **Translation Integration**: Use `mission_progress_id` when translating during a mission
4. **Offline Support**: Cache mission details and phrases for offline access
5. **Progress Indicator**: Show step progress (e.g., "3/5 steps completed")
6. **Step Navigation**: Allow users to review completed steps (read-only)
