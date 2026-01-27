# Error Handling Guide

## Overview

Kkachie API uses consistent error response format and status codes. This guide helps frontend developers handle all possible error scenarios.

## Error Response Format

All error responses follow this structure:

```json
{
  "status": "ERROR_*",
  "message": "Human-readable message in Korean",
  "data": null
}
```

## HTTP Status Codes

| Code | Category | Usage |
|------|----------|-------|
| 200 | Success | Successful GET, PATCH, DELETE, POST (existing) |
| 201 | Created | Successful POST (new resource) |
| 400 | Bad Request | Validation error, invalid request |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Authenticated but not authorized |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource state conflict |
| 422 | Unprocessable Entity | Validation failed |
| 500 | Server Error | Internal server error |

## Error Status Codes

### Authentication Errors

| Status | HTTP | Message | Description |
|--------|------|---------|-------------|
| ERROR_UNAUTHORIZED | 401 | 인증 토큰이 필요해요 | No token provided |
| ERROR_INVALID_TOKEN | 401 | 유효하지 않은 토큰이에요 | Token invalid or expired |
| ERROR_FORBIDDEN | 403 | 권한이 없어요 | Not authorized for this action |

### Validation Errors

| Status | HTTP | Message | Description |
|--------|------|---------|-------------|
| VALIDATION_FAILED | 400/422 | (varies) | Field validation failed |
| ERROR_VALIDATION | 400 | (varies) | General validation error |

### Resource Errors

| Status | HTTP | Message | Description |
|--------|------|---------|-------------|
| ERROR_NOT_FOUND | 404 | - | Generic not found |
| USER_NOT_FOUND | 404 | 사용자를 찾을 수 없어요 | User doesn't exist |

### Translation Errors

| Status | HTTP | Message | Description |
|--------|------|---------|-------------|
| ERROR_INVALID_AUDIO | 400 | 잘못된 오디오 파일이에요 | Invalid audio format |
| TRANSLATION_NOT_FOUND | 404 | 번역 기록을 찾을 수 없어요 | Translation record not found |

### Mission Errors

| Status | HTTP | Message | Description |
|--------|------|---------|-------------|
| MISSION_NOT_FOUND | 404 | 미션을 찾을 수 없어요 | Mission doesn't exist |
| ERROR_MISSION_ALREADY_STARTED | 409 | 이미 진행 중인 미션이에요 | Mission already in progress |
| ERROR_MISSION_NOT_STARTED | 400 | 시작된 미션이 없어요 | No active mission progress |
| MISSION_PROGRESS_NOT_FOUND | 404 | 미션 진행 정보를 찾을 수 없어요 | Progress record not found |
| MISSION_STEP_NOT_FOUND | 404 | 미션 단계를 찾을 수 없어요 | Step doesn't exist |

### Phrase Errors

| Status | HTTP | Message | Description |
|--------|------|---------|-------------|
| PHRASE_NOT_FOUND | 404 | 문장을 찾을 수 없어요 | Phrase doesn't exist |

### Route Errors

| Status | HTTP | Message | Description |
|--------|------|---------|-------------|
| ERROR_ROUTE_NOT_FOUND | 400 | 경로를 찾을 수 없어요 | No route available |
| ERROR_TOO_MANY_WAYPOINTS | 400 | 경유지는 최대 5개까지 가능해요 | Too many waypoints |
| ROUTE_SEARCH_FAILED | 400 | 경로 검색에 실패했어요 | External API failure |

### Server Errors

| Status | HTTP | Message | Description |
|--------|------|---------|-------------|
| INTERNAL_ERROR | 500 | 서버 오류가 발생했어요 | Unexpected server error |
| DATABASE_ERROR | 500 | 데이터베이스 오류가 발생했어요 | Database connection/query error |
| EXTERNAL_SERVICE_ERROR | 500 | 외부 서비스 오류가 발생했어요 | Third-party API failure |

## Error Handling by Endpoint

### /auth/verify-token

| Scenario | Status | Action |
|----------|--------|--------|
| No Authorization header | 401 ERROR_UNAUTHORIZED | Redirect to login |
| Expired token | 401 ERROR_INVALID_TOKEN | Refresh token |
| Invalid token | 401 ERROR_INVALID_TOKEN | Re-authenticate |

### /users/me (GET/PATCH/DELETE)

| Scenario | Status | Action |
|----------|--------|--------|
| Not authenticated | 401 ERROR_UNAUTHORIZED | Redirect to login |
| Invalid display_name | 400 VALIDATION_FAILED | Show validation error |
| Invalid language | 400 VALIDATION_FAILED | Show validation error |

### /translate/text

| Scenario | Status | Action |
|----------|--------|--------|
| Empty source_text | 422 VALIDATION_FAILED | Show "Enter text" error |
| Text too long (>5000) | 422 VALIDATION_FAILED | Show length limit error |
| Same source/target lang | 422 VALIDATION_FAILED | Show "Different language" error |
| Translation service down | 500 EXTERNAL_SERVICE_ERROR | Show retry option |

### /translate/voice

| Scenario | Status | Action |
|----------|--------|--------|
| Invalid audio file | 400 ERROR_INVALID_AUDIO | Show "Invalid format" error |
| Same source/target lang | 422 VALIDATION_FAILED | Show "Different language" error |
| STT service down | 500 EXTERNAL_SERVICE_ERROR | Suggest text translation |

### /missions/*

| Scenario | Status | Action |
|----------|--------|--------|
| Mission not found | 404 MISSION_NOT_FOUND | Show error, go back |
| Already started | 409 ERROR_MISSION_ALREADY_STARTED | Continue existing |
| Not started yet | 400 ERROR_MISSION_NOT_STARTED | Prompt to start |
| Invalid result | 400 VALIDATION_FAILED | Show valid options |

### /phrases/*

| Scenario | Status | Action |
|----------|--------|--------|
| Phrase not found | 404 PHRASE_NOT_FOUND | Refresh list |

### /routes/*

| Scenario | Status | Action |
|----------|--------|--------|
| Route not found | 400 ERROR_ROUTE_NOT_FOUND | Suggest alternative |
| Too many waypoints | 400 ERROR_TOO_MANY_WAYPOINTS | Remove waypoints |
| Invalid coordinates | 422 VALIDATION_FAILED | Check coordinate input |

## TypeScript Error Handling

```typescript
// Error types
interface ApiErrorResponse {
  status: string;
  message: string;
  data: null;
}

// Custom error class
class ApiError extends Error {
  status: string;
  httpCode: number;

  constructor(response: ApiErrorResponse, httpCode: number) {
    super(response.message);
    this.status = response.status;
    this.httpCode = httpCode;
  }
}

// API client with error handling
async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const { data: { session } } = await supabase.auth.getSession();

  if (!session) {
    throw new ApiError(
      { status: 'ERROR_UNAUTHORIZED', message: '로그인이 필요해요', data: null },
      401
    );
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${session.access_token}`,
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  const data = await response.json();

  if (!response.ok || data.status !== 'SUCCESS') {
    throw new ApiError(data, response.status);
  }

  return data.data;
}

// Error handler hook
function useApiError() {
  const handleError = (error: unknown) => {
    if (error instanceof ApiError) {
      switch (error.status) {
        case 'ERROR_UNAUTHORIZED':
        case 'ERROR_INVALID_TOKEN':
          // Redirect to login
          navigation.navigate('Login');
          break;

        case 'ERROR_FORBIDDEN':
          Alert.alert('Access Denied', error.message);
          break;

        case 'VALIDATION_FAILED':
        case 'ERROR_VALIDATION':
          // Show validation error (usually handled by form)
          Alert.alert('Validation Error', error.message);
          break;

        case 'MISSION_NOT_FOUND':
        case 'PHRASE_NOT_FOUND':
        case 'ERROR_NOT_FOUND':
          Alert.alert('Not Found', error.message);
          navigation.goBack();
          break;

        case 'ERROR_MISSION_ALREADY_STARTED':
          // Navigate to existing mission
          Alert.alert('Mission in Progress', 'You already have an active mission.');
          break;

        case 'INTERNAL_ERROR':
        case 'DATABASE_ERROR':
        case 'EXTERNAL_SERVICE_ERROR':
          Alert.alert('Server Error', 'Please try again later.');
          break;

        default:
          Alert.alert('Error', error.message);
      }
    } else {
      // Network error or unexpected error
      Alert.alert('Connection Error', 'Please check your internet connection.');
    }
  };

  return { handleError };
}

// Usage in component
function TranslationScreen() {
  const { handleError } = useApiError();
  const [loading, setLoading] = useState(false);

  const handleTranslate = async () => {
    setLoading(true);
    try {
      const result = await translateText(text, 'ko', 'en');
      setTranslation(result);
    } catch (error) {
      handleError(error);
    } finally {
      setLoading(false);
    }
  };

  return (/* ... */);
}
```

## Form Validation Error Handling

```typescript
// Validation error display
interface ValidationErrors {
  [field: string]: string[];
}

function useFormValidation<T extends object>(schema: ZodSchema<T>) {
  const [errors, setErrors] = useState<ValidationErrors>({});

  const validate = (data: unknown): data is T => {
    try {
      schema.parse(data);
      setErrors({});
      return true;
    } catch (error) {
      if (error instanceof z.ZodError) {
        const fieldErrors: ValidationErrors = {};
        error.errors.forEach((err) => {
          const path = err.path.join('.');
          if (!fieldErrors[path]) {
            fieldErrors[path] = [];
          }
          fieldErrors[path].push(err.message);
        });
        setErrors(fieldErrors);
      }
      return false;
    }
  };

  return { errors, validate, clearErrors: () => setErrors({}) };
}

// Form component with validation
function ProfileEditForm() {
  const { errors, validate } = useFormValidation(profileSchema);

  const handleSubmit = async () => {
    const formData = { display_name, preferred_language };

    if (!validate(formData)) {
      return; // Show validation errors
    }

    try {
      await updateProfile(formData);
    } catch (error) {
      handleError(error);
    }
  };

  return (
    <View>
      <TextInput
        value={display_name}
        onChangeText={setDisplayName}
        error={errors.display_name?.[0]}
      />
      {errors.display_name && (
        <Text style={styles.error}>{errors.display_name[0]}</Text>
      )}
      {/* ... */}
    </View>
  );
}
```

## Token Refresh Strategy

```typescript
import { useEffect } from 'react';

function useTokenRefresh() {
  useEffect(() => {
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        if (event === 'TOKEN_REFRESHED') {
          console.log('Token refreshed');
        } else if (event === 'SIGNED_OUT') {
          // Clear local state, navigate to login
          navigation.reset({
            index: 0,
            routes: [{ name: 'Login' }],
          });
        }
      }
    );

    return () => {
      subscription.unsubscribe();
    };
  }, []);
}

// Automatic retry on 401
async function apiClientWithRetry<T>(
  endpoint: string,
  options: RequestInit = {},
  retries: number = 1
): Promise<T> {
  try {
    return await apiClient<T>(endpoint, options);
  } catch (error) {
    if (
      error instanceof ApiError &&
      error.httpCode === 401 &&
      error.status === 'ERROR_INVALID_TOKEN' &&
      retries > 0
    ) {
      // Try to refresh token
      const { error: refreshError } = await supabase.auth.refreshSession();

      if (!refreshError) {
        // Retry with new token
        return apiClientWithRetry<T>(endpoint, options, retries - 1);
      }
    }
    throw error;
  }
}
```

## User-Friendly Error Messages

| Technical Error | User-Friendly Message |
|-----------------|----------------------|
| ERROR_UNAUTHORIZED | Please log in to continue |
| ERROR_INVALID_TOKEN | Your session has expired. Please log in again. |
| VALIDATION_FAILED | Please check your input and try again. |
| ERROR_INVALID_AUDIO | Sorry, we couldn't process that audio. Try recording again. |
| ERROR_ROUTE_NOT_FOUND | We couldn't find a route. Try different locations. |
| INTERNAL_ERROR | Something went wrong. Please try again. |
| EXTERNAL_SERVICE_ERROR | Service temporarily unavailable. Please try again later. |

## Best Practices

1. **Always catch errors**: Wrap all API calls in try-catch
2. **Show loading states**: Disable buttons during API calls
3. **Graceful degradation**: Provide fallback behavior when services fail
4. **Retry logic**: Implement automatic retry for transient errors
5. **Offline handling**: Queue actions when offline, sync when online
6. **Error logging**: Log errors for debugging (without sensitive data)
7. **User feedback**: Always inform users what went wrong and what to do
