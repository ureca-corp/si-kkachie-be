# External API Providers

외부 API 연동을 위한 벤더별 모듈

## 구조

```
src/external/
├── naver/          # Naver APIs (Maps, Search)
├── kakao/          # Kakao APIs (Mobility, Local)
├── google/         # Google Cloud (Vertex AI)
└── supabase/       # Supabase (Storage)
```

## 연동 가능 API 목록

| 벤더 | API | 설명 |
|------|-----|------|
| Naver | Reverse Geocoding | 좌표 -> 주소 변환 |
| Naver | Directions | 경로 검색 |
| Naver | Local Search | 장소 검색 |
| Kakao | Directions | 경로 검색 |
| Kakao | Category Search | 카테고리별 장소 검색 |
| Google | Vertex AI (Gemini) | AI 콘텐츠 생성, 번역 |
| Supabase | Storage | 파일 업로드/다운로드 |

## 사용법

### Naver
```python
from src.external.naver import get_naver_provider

provider = get_naver_provider()
result = await provider.reverse_geocode(lng=127.0, lat=37.5)
places = await provider.search_places("강남역 맛집")
route = await provider.directions(start_lng=127.0, start_lat=37.5, goal_lng=127.1, goal_lat=37.6)
```

### Kakao
```python
from src.external.kakao import get_kakao_provider

provider = get_kakao_provider()
places = await provider.search_by_category("FD6", lng=127.0, lat=37.5)
route = await provider.directions(start_lng=127.0, start_lat=37.5, goal_lng=127.1, goal_lat=37.6)
```

### Google (Vertex AI)
```python
from src.external.google import get_vertex_provider

provider = get_vertex_provider()
if provider:
    response = provider.generate_content("서울 관광 명소 추천")
    translated = provider.translate("Hello", "en", "ko", context="인사말")
```

### Supabase
```python
from src.external.supabase import get_storage_provider

provider = get_storage_provider()
if provider:
    url = provider.upload(file, "images/photo.jpg", content_type="image/jpeg")
    data = provider.download("images/photo.jpg")
```

## 환경 변수

| 변수명 | 설명 | 필요 모듈 |
|--------|------|-----------|
| `NAVER_CLIENT_ID` | Naver Cloud Platform API Key ID | naver |
| `NAVER_CLIENT_SECRET` | Naver Cloud Platform API Key | naver |
| `NAVER_SEARCH_CLIENT_ID` | Naver Developers Client ID | naver |
| `NAVER_SEARCH_CLIENT_SECRET` | Naver Developers Client Secret | naver |
| `KAKAO_REST_API_KEY` | Kakao REST API Key | kakao |
| `GOOGLE_CLOUD_PROJECT` | Google Cloud 프로젝트 ID | google |
| `GOOGLE_CREDENTIALS_JSON` | 서비스 계정 키 JSON | google |
| `SUPABASE_URL` | Supabase 프로젝트 URL | supabase |
| `SUPABASE_KEY` | Supabase anon key | supabase |
| `SUPABASE_SERVICE_KEY` | Supabase service key (선택) | supabase |
| `SUPABASE_STORAGE_BUCKET` | 스토리지 버킷 이름 | supabase |

## 각 모듈 상세

각 벤더별 디렉토리의 README.md 참조:
- [Naver](./naver/README.md)
- [Kakao](./kakao/README.md)
- [Google](./google/README.md)
- [Supabase](./supabase/README.md)
