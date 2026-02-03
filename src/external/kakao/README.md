# Kakao API Provider

카카오 모빌리티 및 로컬 API 연동 모듈

## 연동 준비 완료 API 목록

| API | 설명 | 플랫폼 |
|-----|------|--------|
| Directions | 경로 검색 | Kakao Mobility |
| Category Search | 카테고리별 장소 검색 | Kakao Local |

## 필요한 환경 변수

| 변수명 | 설명 |
|--------|------|
| `KAKAO_REST_API_KEY` | Kakao REST API Key |

## 사용법

```python
from src.external.kakao import get_kakao_provider

provider = get_kakao_provider()

# 카테고리 검색
result = await provider.search_by_category(
    category="FD6",  # 음식점
    lng=127.0, lat=37.5,
    radius=1000
)

# 경로 검색
route = await provider.directions(
    start_lng=127.0, start_lat=37.5,
    goal_lng=127.1, goal_lat=37.6
)
```

## 카테고리 코드

| 코드 | 설명 |
|------|------|
| MT1 | 대형마트 |
| CS2 | 편의점 |
| PS3 | 어린이집, 유치원 |
| SC4 | 학교 |
| AC5 | 학원 |
| PK6 | 주차장 |
| OL7 | 주유소, 충전소 |
| SW8 | 지하철역 |
| BK9 | 은행 |
| CT1 | 문화시설 |
| AG2 | 중개업소 |
| PO3 | 공공기관 |
| AT4 | 관광명소 |
| AD5 | 숙박 |
| FD6 | 음식점 |
| CE7 | 카페 |
| HP8 | 병원 |
| PM9 | 약국 |

## 공식 문서

- [Kakao Mobility Directions API](https://developers.kakaomobility.com/docs/navi-api/directions/)
- [Kakao Local Category Search API](https://developers.kakao.com/docs/latest/ko/local/dev-guide#search-by-category)
