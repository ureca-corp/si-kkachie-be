# Naver API Provider

Naver Cloud Platform과 Naver Developers API 연동 모듈

## 연동 준비 완료 API 목록

| API | 설명 | 플랫폼 |
|-----|------|--------|
| Reverse Geocoding | 좌표 -> 주소 변환 | Naver Cloud Platform |
| Directions | 경로 검색 | Naver Cloud Platform |
| Local Search | 장소 검색 | Naver Developers |

## 필요한 환경 변수

| 변수명 | 설명 |
|--------|------|
| `NAVER_CLIENT_ID` | Naver Cloud Platform API Key ID |
| `NAVER_CLIENT_SECRET` | Naver Cloud Platform API Key |
| `NAVER_SEARCH_CLIENT_ID` | Naver Developers Client ID |
| `NAVER_SEARCH_CLIENT_SECRET` | Naver Developers Client Secret |

## 사용법

```python
from src.external.naver import get_naver_provider

provider = get_naver_provider()

# 역지오코딩
result = await provider.reverse_geocode(lng=127.0, lat=37.5)

# 장소 검색
places = await provider.search_places("강남역 맛집", display=5)

# 경로 검색
route = await provider.directions(
    start_lng=127.0, start_lat=37.5,
    goal_lng=127.1, goal_lat=37.6
)
```

## 공식 문서

- [Naver Cloud Maps API](https://api.ncloud-docs.com/docs/ai-naver-mapsreversegeocoding)
- [Naver Cloud Directions API](https://api.ncloud-docs.com/docs/ai-naver-mapsdirections)
- [Naver Developers Local Search](https://developers.naver.com/docs/serviceapi/search/local/local.md)
