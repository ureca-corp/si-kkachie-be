# 코드 분석 가이드

기존 Layer-based 모듈을 분석하여 Vertical Slice로 변환하기 위한 정보 추출 방법.

## 엔드포인트 추출

`controller.py`에서 FastAPI 라우터 엔드포인트 추출.

### 검색 패턴

```python
# 데코레이터로 HTTP 메서드 식별
@router.get("/path")
@router.post("/path")
@router.patch("/path")
@router.delete("/path")
```

### 추출 정보

각 엔드포인트마다:
- **HTTP 메서드**: GET, POST, PATCH, DELETE
- **경로**: 전체 경로 (prefix 제외)
- **함수명**: 엔드포인트 핸들러 함수명
- **파라미터**: path params, query params, body
- **Response 타입**: 반환 타입 힌트

### 예시

```python
@router.get("/reverse-geocode", response_model=ReverseGeocodeResponse)
async def reverse_geocode(
    lat: float = Query(...),
    lon: float = Query(...),
    current_profile: Profile = Depends(get_current_profile),
) -> ReverseGeocodeResponse:
    return await get_reverse_geocode(lat, lon, current_profile.id)
```

추출:
- Method: GET
- Path: /reverse-geocode
- Handler: reverse_geocode
- Service: get_reverse_geocode
- Response: ReverseGeocodeResponse

## 서비스 함수 매핑

`service.py`에서 비즈니스 로직 함수 추출.

### 추출 정보

각 서비스 함수마다:
- **함수명**
- **파라미터 타입**
- **반환 타입**
- **의존성**: 다른 함수, 외부 API, DB 호출

### 엔드포인트-서비스 매핑

컨트롤러 함수 본문에서 호출하는 서비스 함수 추적:

```python
# Controller
async def reverse_geocode(...):
    return await get_reverse_geocode(...)  # ← 서비스 함수 호출

# Service
async def get_reverse_geocode(...):  # ← 매핑 대상
    ...
```

## DTO 클래스 추출

`entities.py`에서 Pydantic 모델 추출.

### 검색 패턴

```python
class SomeRequest(BaseModel):
    ...

class SomeResponse(BaseModel):
    ...
```

### 분류

- **Request DTO**: 요청 본문, 일반적으로 `Request` suffix
- **Response DTO**: 응답 본문, 일반적으로 `Response` suffix
- **공유 DTO**: 여러 엔드포인트에서 사용되는 중첩 모델

## SQLModel 클래스 추출

`models.py`에서 데이터베이스 모델 추출.

### 검색 패턴

```python
class Model(SQLModel, table=True):
    __tablename__ = "..."
    ...
```

### 판단 기준

SQLModel은 항상 공유 파일(`_models.py`)로 분리.

## Repository 함수 추출

`repository.py`에서 데이터베이스 접근 함수 추출.

### 추출 정보

각 함수마다:
- **함수명**
- **사용하는 SQLModel**
- **쿼리 타입**: SELECT, INSERT, UPDATE, DELETE

### 판단 기준

Repository 함수는 항상 공유 파일(`_repository.py`)로 분리.

## 공유 로직 식별

### 식별 기준

다음 중 하나라도 해당하면 공유 파일로 분리:
1. **여러 엔드포인트에서 사용**: 2개 이상의 서비스 함수가 호출
2. **SQLModel**: 데이터베이스 모델
3. **Repository**: DB 접근 함수
4. **유틸리티**: 순수 함수 (외부 의존성 없음)

### 파일명 규칙

- `_models.py`: SQLModel 클래스
- `_repository.py`: DB 접근 함수
- `_utils.py`: 순수 유틸리티 함수
- `_parsers.py`: 외부 API 응답 파싱
- `_{custom}.py`: 도메인 특화 공유 로직

## 의존성 추적

각 엔드포인트가 의존하는 모든 요소 추적.

### 추적 대상

1. **DTO 클래스**: Request/Response 모델
2. **서비스 함수**: 비즈니스 로직
3. **공유 함수**: 유틸리티, 파서 등
4. **공유 모델**: SQLModel
5. **Repository 함수**: DB 접근
6. **외부 API**: Naver, Google 등
7. **FastAPI 의존성**: Depends(), Query() 등

### 예시

`GET /locations/search` 엔드포인트:

```python
# 의존성 맵
{
    "dtos": ["PlaceSearchItem"],
    "service": "search_places",
    "shared": {
        "parsers": ["parse_place_item"],
        "utils": ["calculate_distance"]
    },
    "external": ["naver_maps_api"],
    "dependencies": ["get_current_profile"]
}
```

## 테스트 분석

`test_controller.py`에서 테스트 케이스 추출.

### 추출 정보

각 테스트마다:
- **테스트하는 엔드포인트**
- **테스트 클래스/함수명**
- **Mock 대상**: service 함수, 외부 API 등
- **Fixture 의존성**

### 매핑 규칙

```python
# 테스트 클래스명 → 기능 파일
TestReverseGeocode → test_reverse_geocode.py
TestSearch → test_search.py

# 함수명 패턴
test_reverse_geocode_success → reverse_geocode 엔드포인트
test_search_places_with_filter → search 엔드포인트
```

## 분석 출력 예시

```python
{
    "domain": "locations",
    "endpoints": [
        {
            "method": "GET",
            "path": "/locations/reverse-geocode",
            "handler": "reverse_geocode",
            "service": "get_reverse_geocode",
            "file_name": "reverse_geocode.py",
            "dtos": ["ReverseGeocodeResponse"],
            "dependencies": {
                "shared": ["_parsers.parse_reverse_geocode"],
                "external": ["naver_maps_api"]
            }
        },
        {
            "method": "GET",
            "path": "/locations/search",
            "handler": "search_places_endpoint",
            "service": "search_places",
            "file_name": "search.py",
            "dtos": ["PlaceSearchItem"],
            "dependencies": {
                "shared": ["_parsers.parse_place_item", "_utils.calculate_distance"],
                "external": ["naver_maps_api"]
            }
        }
    ],
    "shared_files": {
        "_parsers.py": ["parse_reverse_geocode", "parse_place_item"],
        "_utils.py": ["calculate_distance"]
    },
    "tests": [
        {
            "class": "TestReverseGeocode",
            "file": "test_reverse_geocode.py",
            "endpoint": "reverse_geocode"
        },
        {
            "class": "TestSearch",
            "file": "test_search.py",
            "endpoint": "search"
        }
    ]
}
```
