# Authentication & Profile Management

## Overview

Kkachie uses Supabase Auth for authentication with Google/Apple social login. The backend validates Supabase tokens and manages user profiles.

## User Flow Diagram

```
+-------------------+
|   App Launch      |
+--------+----------+
         |
         v
+-------------------+
| Supabase Login    |
| (Google/Apple)    |
+--------+----------+
         |
         v
+-------------------+
| POST /auth/       |
| verify-token      |
+--------+----------+
         |
    +----+----+
    |         |
    v         v
+-------+ +-------+
| 200   | | 201   |
|Existing| |New   |
| User  | | User  |
+-------+ +-------+
    |         |
    v         v
+-------------------+
|   Main Screen     |
+-------------------+
```

## Screen Mockups

### Login Screen
```
+---------------------------+
|                           |
|         Kkachie           |
|    Your Travel Buddy      |
|                           |
|   +-------------------+   |
|   |  [G] Google Login |   |
|   +-------------------+   |
|                           |
|   +-------------------+   |
|   |  [A] Apple Login  |   |
|   +-------------------+   |
|                           |
|   By continuing, you      |
|   agree to our Terms      |
|                           |
+---------------------------+
```

### Profile Screen
```
+---------------------------+
|  <  My Profile            |
+---------------------------+
|                           |
|      +----------+         |
|      |  Photo   |         |
|      +----------+         |
|                           |
|   Name: John Doe          |
|   Email: john@email.com   |
|   Language: English       |
|                           |
|   +-------------------+   |
|   |   Edit Profile    |   |
|   +-------------------+   |
|                           |
|   +-------------------+   |
|   |   Delete Account  |   |
|   +-------------------+   |
|                           |
+---------------------------+
```

## API Endpoints

### 1. Verify Token (POST /auth/verify-token)

Validates Supabase token and creates profile for new users.

**Request:**
```bash
curl -X POST "https://api.kkachie.com/auth/verify-token" \
  -H "Authorization: Bearer {supabase_access_token}"
```

**Response (200 - Existing User):**
```json
{
  "status": "SUCCESS",
  "message": "인증에 성공했어요",
  "data": {
    "id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
    "user_id": "auth-user-uuid",
    "email": "user@example.com",
    "display_name": "John Doe",
    "preferred_language": "en",
    "profile_image_url": "https://storage.supabase.co/...",
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
    "id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
    "user_id": "auth-user-uuid",
    "email": "new@example.com",
    "display_name": null,
    "preferred_language": "en",
    "profile_image_url": null,
    "is_new_user": true
  }
}
```

---

### 2. Get My Profile (GET /users/me)

Returns current user's profile information.

**Request:**
```bash
curl -X GET "https://api.kkachie.com/users/me" \
  -H "Authorization: Bearer {supabase_access_token}"
```

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "조회에 성공했어요",
  "data": {
    "id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
    "user_id": "auth-user-uuid",
    "email": "user@example.com",
    "display_name": "John Doe",
    "preferred_language": "en",
    "profile_image_url": "https://storage.supabase.co/...",
    "created_at": "2026-01-27T10:00:00Z"
  }
}
```

---

### 3. Update Profile (PATCH /users/me)

Updates user profile information.

**Request:**
```bash
curl -X PATCH "https://api.kkachie.com/users/me" \
  -H "Authorization: Bearer {supabase_access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "Jane Doe",
    "preferred_language": "ko"
  }'
```

**Request Body:**
```typescript
interface UpdateProfileRequest {
  display_name?: string;     // 2-50 characters
  preferred_language?: "ko" | "en";
}
```

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "정보가 수정됐어요",
  "data": {
    "id": "018d5c4f-xxxx-7xxx-xxxx-xxxxxxxxxxxx",
    "user_id": "auth-user-uuid",
    "email": "user@example.com",
    "display_name": "Jane Doe",
    "preferred_language": "ko",
    "profile_image_url": null
  }
}
```

---

### 4. Upload Profile Image (POST /users/me/profile-image)

Gets presigned URL for profile image upload.

**Request:**
```bash
curl -X POST "https://api.kkachie.com/users/me/profile-image" \
  -H "Authorization: Bearer {supabase_access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "file_name": "profile.jpg",
    "content_type": "image/jpeg"
  }'
```

**Request Body:**
```typescript
interface ProfileImageUploadRequest {
  file_name: string;
  content_type: "image/jpeg" | "image/png" | "image/gif" | "image/webp";
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

**Usage Flow:**
```
1. Call POST /users/me/profile-image
2. Upload file to upload_url using PUT
3. Call PATCH /users/me with profile_image_url = public_url
```

---

### 5. Delete Account (DELETE /users/me)

Permanently deletes user account and all related data.

**Request:**
```bash
curl -X DELETE "https://api.kkachie.com/users/me" \
  -H "Authorization: Bearer {supabase_access_token}"
```

**Response (200):**
```json
{
  "status": "SUCCESS",
  "message": "회원 탈퇴가 완료됐어요"
}
```

## TypeScript Types

```typescript
// Profile Response
interface ProfileResponse {
  id: string;
  user_id: string;
  email: string;
  display_name: string | null;
  preferred_language: "ko" | "en";
  profile_image_url: string | null;
  is_new_user?: boolean;
  created_at?: string;
}

// Update Profile Request
interface UpdateProfileRequest {
  display_name?: string;
  preferred_language?: "ko" | "en";
}

// Profile Image Upload Request
interface ProfileImageUploadRequest {
  file_name: string;
  content_type: string;
}

// Profile Image Upload Response
interface ProfileImageUploadResponse {
  upload_url: string;
  public_url: string;
  expires_in: number;
}
```

## React Native Implementation Example

```typescript
import { supabase } from './supabase';

const API_BASE = 'https://api.kkachie.com';

// API Client with Auth
async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const { data: { session } } = await supabase.auth.getSession();

  if (!session) {
    throw new Error('Not authenticated');
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

  if (data.status !== 'SUCCESS') {
    throw new Error(data.message);
  }

  return data.data;
}

// Verify Token and Get/Create Profile
async function verifyToken(): Promise<ProfileResponse> {
  return apiClient<ProfileResponse>('/auth/verify-token', {
    method: 'POST',
  });
}

// Get Current Profile
async function getProfile(): Promise<ProfileResponse> {
  return apiClient<ProfileResponse>('/users/me');
}

// Update Profile
async function updateProfile(
  data: UpdateProfileRequest
): Promise<ProfileResponse> {
  return apiClient<ProfileResponse>('/users/me', {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

// Upload Profile Image
async function uploadProfileImage(file: File): Promise<string> {
  // 1. Get presigned URL
  const uploadInfo = await apiClient<ProfileImageUploadResponse>(
    '/users/me/profile-image',
    {
      method: 'POST',
      body: JSON.stringify({
        file_name: file.name,
        content_type: file.type,
      }),
    }
  );

  // 2. Upload to presigned URL
  await fetch(uploadInfo.upload_url, {
    method: 'PUT',
    body: file,
    headers: {
      'Content-Type': file.type,
    },
  });

  // 3. Return public URL
  return uploadInfo.public_url;
}

// Delete Account
async function deleteAccount(): Promise<void> {
  await apiClient('/users/me', { method: 'DELETE' });
  await supabase.auth.signOut();
}
```

## Error Handling

| Status Code | Error Status | Message | Action |
|-------------|--------------|---------|--------|
| 401 | ERROR_UNAUTHORIZED | 인증 토큰이 필요해요 | Redirect to login |
| 401 | ERROR_INVALID_TOKEN | 유효하지 않은 토큰이에요 | Refresh token or re-login |
| 400 | ERROR_VALIDATION | (varies) | Show validation error |

## Best Practices

1. **Token Management**: Implement automatic token refresh using Supabase's `onAuthStateChange`
2. **Profile Caching**: Cache profile data locally, invalidate on updates
3. **Image Upload**: Show progress indicator during presigned URL upload
4. **Account Deletion**: Show confirmation dialog with warning about data loss
