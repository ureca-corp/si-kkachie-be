# Supabase Storage Provider

Supabase Storage API 연동 모듈

## 연동 준비 완료 API 목록

| API | 설명 |
|-----|------|
| upload | 파일 업로드 |
| download | 파일 다운로드 |
| delete | 파일 삭제 |
| get_presigned_url | 다운로드용 서명된 URL 생성 |
| get_upload_url | 업로드용 서명된 URL 생성 |

## 필요한 환경 변수

| 변수명 | 설명 |
|--------|------|
| `SUPABASE_URL` | Supabase 프로젝트 URL |
| `SUPABASE_KEY` | Supabase anon key |
| `SUPABASE_SERVICE_KEY` | Supabase service key (백엔드 전용, 선택) |
| `SUPABASE_STORAGE_BUCKET` | 스토리지 버킷 이름 (기본: profiles) |

## 사용법

```python
from src.external.supabase import get_storage_provider, get_async_storage_provider

# 동기
provider = get_storage_provider()
if provider:
    # 업로드
    url = provider.upload(file, "images/photo.jpg", content_type="image/jpeg")

    # 다운로드
    data = provider.download("images/photo.jpg")

    # 삭제
    provider.delete("images/photo.jpg")

    # 서명된 URL 생성
    signed_url = provider.get_presigned_url("images/photo.jpg", expires_in=3600)
    upload_url = provider.get_upload_url("images/new.jpg", expires_in=3600)

# 비동기
async_provider = await get_async_storage_provider()
if async_provider:
    url = await async_provider.upload(file, "images/photo.jpg")
    data = await async_provider.download("images/photo.jpg")
    await async_provider.delete("images/photo.jpg")
    await async_provider.close()  # 종료 시 호출
```

## 공식 문서

- [Supabase Storage](https://supabase.com/docs/guides/storage)
- [Supabase Python Client](https://supabase.com/docs/reference/python/storage-createbucket)
