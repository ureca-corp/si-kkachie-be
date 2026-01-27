# Session Memory
> Last Updated: 2026-01-24
> Status: IN_PROGRESS
> Current Phase: Phase 3 - SPEC 작성 완료

---

## 📋 프로젝트 개요

**프로젝트명**: 외국인 관광객 대상 대중교통 상황별 가이드 서비스

**핵심 컨셉**:
단순 길찾기가 아닌 **상황별 단계적 가이드 시스템**
- 상황 분류 (버스 탑승/하차, 지하철 환승, 터미널 이동, 티머니 충전 등)
- 사용자 의도 파악 (최소 선택으로 목표 좁히기)
- 맞춤형 카드 제공 (정보, 안내, 문장, 주의사항)
- 추가 액션 필요 시 상세 단계 (외부링크, CTA 버튼)

**구간 전환 처리**:
- 외부 지도앱 경로 → 앱에 입력
- 버스/지하철/도보 구간별 분할 표시
- 구간 종료 시점에서 사용자 확인
- "이전/다음" CTA로 단계 이동

---

## ✅ 확정된 요구사항

### 기술 스택

| 항목 | 결정 |
|------|------|
| 대중교통 API | **TMAP 단독** (transit/routes) |
| 지도 API | **Naver Maps** (장소검색, Geocoding, POI) |
| LLM | **불필요** (규칙 기반으로 충분) |
| 인증 | **JWT** (필수 가입) |
| 타겟 지역 | **전국** |
| 다국어 | **한국어 + 영어** |

### 회원 시스템

| 항목 | 상세 |
|------|------|
| 수집 정보 | 이메일 + 비밀번호 + 닉네임 + 국적 |
| 인증 방식 | JWT Bearer Token |
| 필수 여부 | **가입 필수** (비회원 사용 불가) |

### 핵심 기능

| 기능 | 상세 |
|------|------|
| **경로 탐색** | TMAP 대중교통 API (구간별 분할) |
| **경로 옵션** | 최단시간 / 최소환승 / 최소도보 |
| **교통수단 구분** | BUS/SUBWAY/WALK/EXPRESSBUS/TRAIN + 버스종류 |
| **예상 요금** | 경로별 교통비 계산 표시 |
| **실시간 정보** | TMAP 제공 실시간 정보 활용 |
| **관광지 POI** | 경로 주변 관광지/맛집 추천 (Naver Maps) |
| **즐겨찾기** | 장소 + **전체 경로 데이터 저장** |
| **검색 히스토리** | 자주 가는 도착지 TOP 5 추천 |

### 상황별 가이드 시스템 (4-Depth 정보 체계)

```
Level 1: 상황 분류
├── 버스 탑승/하차
├── 지하철 탑승/환승
├── 터미널 내부 이동
├── 티머니 충전
└── 길 묻기

Level 2: 사용자 의도
├── 어디로 가야 하는지 질문
├── 하차 타이밍
├── 환승 통로 찾기
├── 구매
└── 직원 문의

Level 3: 대응 카드
├── 정보 카드
├── 안내 카드
├── 문장 카드 (외국인용 한국어 문장)
└── 주의사항 카드

Level 4: 추가 액션
├── 외부 링크
└── CTA 버튼
```

### 구간 전환 흐름

```
1. 사용자가 앱 지도에서 정보 확인
2. 외부 지도앱으로 경로 확인
3. 경로를 앱에 입력
4. 앱이 구간별로 분할 표시 (버스-지하철-도보)
5. 구간 종료 지점 통과 시 → 사용자 확인
6. 다음 상황 실행
7. 오류 시 "이전" CTA로 되돌아가기 가능
```

### 데이터 수집 요소

사용자 입력 기반 맥락 유추:
- 승차지점
- 승차지점 경유 버스 정보
- 목적지
- 선택한 버스 정보
- 사용자 실시간 GPS 정보

---

## 🏗️ 예상 도메인 구조

```
src/domains/
├── users/           # 회원 (가입/로그인/프로필/국적)
├── routes/          # 경로 탐색 (TMAP 연동, 구간 분할)
├── places/          # 장소 검색 (Naver 연동)
├── favorites/       # 즐겨찾기 (장소 + 전체 경로)
├── history/         # 검색 히스토리 (TOP 5 추천)
├── pois/            # 관광지 POI 추천
├── guides/          # 상황별 가이드 (4-Depth 카드)
└── situations/      # 상황 인식 및 전환 로직
```

---

## 🔌 외부 연동

| API | 용도 | 우선순위 |
|-----|------|----------|
| **TMAP 대중교통 API** | 경로 탐색, 구간 분할, 요금, 실시간 | 필수 |
| **Naver Maps API** | 장소검색, Geocoding, 관광지 POI | 필수 |

---

## Phase 1 결과: 외부 API 리서치

### 1. TMAP 대중교통 API

#### 기본 정보
| 항목 | 내용 |
|------|------|
| **공식 문서** | https://transit.tmapmobility.com/ |
| **SK Open API** | https://skopenapi.readme.io/reference/대중교통-소개 |
| **기반 표준** | GTFS (General Transit Feed Specification) |

#### API 엔드포인트
| API | 엔드포인트 | 메서드 |
|-----|-----------|--------|
| **대중교통 경로안내** | `https://apis.openapi.sk.com/transit/routes` | POST |
| **대중교통 요약정보** | `https://apis.openapi.sk.com/transit/routes/sub` | POST |

#### 인증 방식
- **Header 인증**: `appKey` 헤더에 발급받은 AppKey 포함
- **발급 위치**: SK Open API 마이페이지 > 앱에서 발급

#### 요금제
| 플랜 | 비용 | 제한 |
|------|------|------|
| **FREE** | 무료 | 10건/일 |
| **종량제** | 0.88원/건 | 무제한 |

#### 요청 파라미터 (필수)
```json
{
  "startX": "127.02479803562213",  // 출발지 경도 (WGS84)
  "startY": "37.504585233865086",  // 출발지 위도
  "endX": "127.03747630119366",    // 도착지 경도
  "endY": "37.479103923078995",    // 도착지 위도
  "count": 5,                       // 경로 개수
  "lang": 0,                        // 언어 (0: 한국어, 1: 영어)
  "format": "json"                  // 응답 포맷
}
```

#### 응답 구조
```
metaData
└── plan
    └── itineraries[]              // 경로 배열
        ├── totalTime              // 총 소요시간 (초)
        ├── transferCount          // 환승 횟수
        ├── totalDistance          // 총 거리 (m)
        ├── totalWalkDistance      // 총 도보 거리 (m)
        ├── fare
        │   └── regular
        │       ├── currency
        │       │   ├── symbol     // "￦"
        │       │   ├── currency   // "원"
        │       │   └── currencyCode // "KRW"
        │       └── totalFare      // 요금 (원)
        └── legs[]                 // 구간별 정보
            ├── mode               // 이동수단
            ├── sectionTime        // 구간 소요시간 (초)
            ├── distance           // 구간 거리 (m)
            ├── start              // 출발 정보
            ├── end                // 도착 정보
            ├── route              // 노선 정보 (버스/지하철)
            ├── type               // 노선 유형 코드
            └── service            // 운행 상태 (1=운행중, 0=종료)
```

#### mode 값 (이동수단)
| mode | 설명 |
|------|------|
| `WALK` | 도보 |
| `BUS` | 버스 |
| `SUBWAY` | 지하철 |
| `EXPRESSBUS` | 고속/시외버스 |
| `TRAIN` | 기차 |
| `AIRPLANE` | 항공 |
| `FERRY` | 해운 |

#### 버스 type 코드 (노선 유형)
| 코드 | 종류 | 비고 |
|------|------|------|
| 1 | 일반 | |
| 2 | 좌석 | |
| 3 | 마을버스 | 마을 |
| 4 | 직행좌석 | 광역 |
| 5 | 공항 | |
| 11 | 간선 | 파란색 (서울) |
| 12 | 지선 | 녹색 (서울) |
| 13 | 순환 | |
| 14 | 광역 | 빨간색 |
| 15 | 급행 | |

#### 지하철 type 코드
| 코드 | 노선 |
|------|------|
| 1-9 | 1~9호선 |
| 100 | 수인분당선 |
| 104 | 경의중앙선 |
| 109 | 신분당선 |
| ... | (기타 노선) |

#### 실시간 정보
- **service 필드**: 운행 상태 (1=운행중, 0=종료)
- **searchDttm 파라미터**: 타임머신 기능 (특정 시각 기준 조회)
- **실시간 위치/도착 정보**: TMAP 대중교통 API에서는 미제공
  - 실시간 버스 도착 정보가 필요하면 공공데이터포털 API 별도 연동 필요
  - https://www.data.go.kr/data/15000314/openapi.do (서울 버스도착정보)

#### 추가 기능 (별도 API)
- 지하철 혼잡도 API (통계성/실시간)
- 열차 칸별 혼잡도
- 칸별 하차 비율

---

### 2. Naver Maps API

#### 기본 정보
| 항목 | 내용 |
|------|------|
| **공식 문서** | https://www.ncloud.com/product/applicationservice/maps |
| **API 문서** | https://api.ncloud-docs.com/docs/ai-naver-mapsgeocoding-geocode |
| **콘솔** | NAVER Cloud Platform Console |

#### API 엔드포인트
| API | 엔드포인트 | 용도 |
|-----|-----------|------|
| **Geocoding** | `https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode` | 주소 -> 좌표 |
| **Reverse Geocoding** | `https://naveropenapi.apigw.ntruss.com/map-reversegeocode/v2/gc` | 좌표 -> 주소 |
| **지역검색** | `https://openapi.naver.com/v1/search/local.json` | 장소/POI 검색 |

#### 인증 방식

**Naver Cloud Platform (Geocoding/Reverse Geocoding)**
```python
headers = {
    "X-NCP-APIGW-API-KEY-ID": "<Client ID>",
    "X-NCP-APIGW-API-KEY": "<Client Secret>"
}
```

**Naver Developers (지역검색)**
```python
headers = {
    "X-Naver-Client-Id": "<Client ID>",
    "X-Naver-Client-Secret": "<Client Secret>"
}
```

#### 요금제 (2025년 7월 이후)
| API | 무료 이용량 | 종량제 |
|-----|------------|--------|
| **Maps API (NCP)** | 무료 이용량 없음 | 유료 종량제 |
| **지역검색 (Developers)** | 일일 호출 제한 있음 | 무료 (제한 내) |

**주의**: 2025년 7월 1일부터 Naver Cloud Platform의 지도 API는 무료 이용량이 종료됨

#### Geocoding API 요청 예시
```
GET /map-geocode/v2/geocode?query=서울특별시+중구+명동
```

#### Reverse Geocoding API 요청 예시
```
GET /map-reversegeocode/v2/gc?coords=126.969594,37.586541&output=json&orders=addr
```

#### 지역검색 API 응답 구조
```json
{
  "items": [
    {
      "title": "장소명",
      "link": "네이버 플레이스 URL",
      "category": "여행,명소>궁궐",
      "description": "설명",
      "telephone": "전화번호",
      "address": "지번주소",
      "roadAddress": "도로명주소",
      "mapx": "경도 (TM128)",
      "mapy": "위도 (TM128)"
    }
  ]
}
```

#### 지역검색 주요 파라미터
| 파라미터 | 설명 | 비고 |
|----------|------|------|
| query | 검색어 | 필수 |
| display | 출력 건수 | 최대 5개 (트래픽 제한) |
| start | 시작 위치 | 1~1000 |
| sort | 정렬 | random(기본), comment |

---

### 3. API 선택 결론

| 용도 | 선택 | 이유 |
|------|------|------|
| **경로 탐색** | TMAP 대중교통 API | 전국 대중교통 통합, 구간별 분할, 요금 정보 제공 |
| **장소 검색 (POI)** | Naver 지역검색 API | 관광지/맛집 카테고리, 한국 로컬 데이터 우수 |
| **좌표 변환** | Naver Geocoding API | 주소-좌표 변환, TMAP 입력용 |

---

### 4. 구현 시 고려사항

#### TMAP API
- 무료 플랜 10건/일 제한 -> 개발 시 캐싱 필수
- 실시간 버스 도착 정보 미제공 -> 공공데이터포털 연동 검토
- legs 배열의 순서가 이동 순서와 동일

#### Naver API
- 지역검색 display 최대 5개 제한
- 좌표계 TM128 사용 -> WGS84 변환 필요
- 2025년 7월부터 Maps API 유료화

#### 에러 처리
- TMAP: 에러 코드 문서 제공
- Naver: 429 Quota Exceed 에러 주의 (API 미선택 시 발생)

---

### 5. Python 라이브러리 (예정)

```python
# HTTP 클라이언트
httpx  # 비동기 HTTP 요청

# 좌표계 변환 (필요시)
pyproj  # TM128 <-> WGS84 변환
```

### 6. API 스펙 파일 (로컬 저장)

| 파일 | 경로 | 설명 |
|------|------|------|
| Naver OpenAPI | `docs/api-specs/naver-openapi-swagger.json` | 공식 Swagger (지역검색 등) |
| TMAP Transit | `docs/api-specs/tmap-transit-api.json` | 비공식 OpenAPI 3.0 (문서 기반) |

---

## Phase 2 결과: 도메인별 상세 스펙

### 1. users 도메인

#### 엔티티
```
User
├── id: UUID (PK)
├── email: str (unique, not null)
├── password_hash: str (not null)
├── nickname: str (not null)
├── nationality: str (ISO 3166-1 alpha-2, not null)
├── preferred_language: str (default: 'en')
├── profile_image_url: str (nullable)
├── last_login_at: datetime (nullable)
├── login_count: int (default: 0)
├── is_active: bool (default: true)
├── created_at: datetime
├── updated_at: datetime
└── deleted_at: datetime (nullable, soft delete)
```

#### API
```
POST   /auth/register              # 회원가입
POST   /auth/login                 # 로그인
POST   /auth/logout                # 로그아웃
POST   /auth/refresh               # 토큰 갱신
POST   /auth/password              # 비밀번호 변경
POST   /auth/password-reset/request  # 비밀번호 재설정 요청
POST   /auth/password-reset/confirm  # 비밀번호 재설정 확인
GET    /users/me                   # 내 정보 조회
PATCH  /users/me                   # 내 정보 수정
DELETE /users/me                   # 회원 탈퇴 (soft delete)
```

#### 비즈니스 룰
- 이메일: 형식만 검사 (인증 메일 없음)
- 비밀번호: 최소 8자
- 로그인 실패: 제한 없음
- JWT: Access 1시간 / Refresh 30일
- 국적: ISO 3166-1 alpha-2 코드

#### 에러 코드
| 코드 | 한글 | 영문 |
|------|------|------|
| EMAIL_ALREADY_EXISTS | 이미 가입된 이메일이에요 | This email is already registered |
| INVALID_CREDENTIALS | 이메일 또는 비밀번호가 맞지 않아요 | Invalid email or password |
| TOKEN_EXPIRED | 로그인이 만료되었어요 | Your session has expired |

---

### 2. routes 도메인

#### 엔티티
```
Route
├── id: UUID (PK)
├── user_id: UUID (FK -> User)
├── origin_place_id: UUID (FK -> Place)
├── destination_place_id: UUID (FK -> Place)
├── route_option: enum (FASTEST, LEAST_TRANSFER, LEAST_WALK)
├── total_time: int (초)
├── total_distance: int (m)
├── total_walk_distance: int (m)
├── transfer_count: int
├── total_fare: int (원)
├── is_favorite: bool (default: false)
├── created_at: datetime
└── updated_at: datetime

RouteLeg
├── id: UUID (PK)
├── route_id: UUID (FK -> Route)
├── sequence: int (순서)
├── mode: enum (WALK, BUS, SUBWAY, EXPRESSBUS, TRAIN)
├── section_time: int (초)
├── distance: int (m)
├── start_name: str
├── start_lat: float
├── start_lon: float
├── end_name: str
├── end_lat: float
├── end_lon: float
├── route_name: str (nullable, 버스번호/지하철노선)
├── route_type: int (nullable, 노선유형코드)
└── pass_stop_list: JSON (정류장 목록)
```

#### API
```
POST   /routes/search              # 경로 검색 (3가지 옵션 모두 반환)
GET    /routes/{id}                # 경로 상세 조회
GET    /routes/{id}/legs           # 구간 목록 조회
POST   /routes/{id}/favorite       # 즐겨찾기 추가
DELETE /routes/{id}/favorite       # 즐겨찾기 제거
```

#### 비즈니스 룰
- 모든 검색 결과 DB 저장 (분석용)
- 3가지 옵션 (최단시간/최소환승/최소도보) 모두 반환
- 구간 정보 전체 저장 (정류장 목록 포함)
- TMAP API 실패 시 3회 재시도 후 에러

#### 외부 연동
- TMAP 대중교통 API (`/transit/routes`)

---

### 3. places 도메인

#### 엔티티
```
Place
├── id: UUID (PK)
├── name: str
├── address: str
├── road_address: str (nullable)
├── lat: float (WGS84)
├── lon: float (WGS84)
├── category: str (nullable)
├── naver_place_url: str (nullable)
├── telephone: str (nullable)
├── created_at: datetime
└── updated_at: datetime
```

#### API
```
GET    /places/search              # 장소 검색 (Naver 연동)
GET    /places/geocode             # 주소 -> 좌표 변환
GET    /places/reverse-geocode     # 좌표 -> 주소 변환
GET    /places/{id}                # 장소 상세 조회
```

#### 비즈니스 룰
- Naver 지역검색 + Geocoding 연동
- 캐싱 없음 (실시간 검색)
- 좌표계 변환: 백엔드에서 TM128 → WGS84

#### 외부 연동
- Naver 지역검색 API
- Naver Geocoding API

---

### 4. favorites 도메인

#### 엔티티
```
FavoritePlace
├── id: UUID (PK)
├── user_id: UUID (FK -> User)
├── place_id: UUID (FK -> Place)
├── alias: str (nullable, 사용자 지정 이름)
├── created_at: datetime

FavoriteRoute
├── id: UUID (PK)
├── user_id: UUID (FK -> User)
├── route_id: UUID (FK -> Route)
├── alias: str (nullable)
├── created_at: datetime
```

#### API
```
GET    /favorites/places           # 즐겨찾기 장소 목록
POST   /favorites/places           # 즐겨찾기 장소 추가
DELETE /favorites/places/{id}      # 즐겨찾기 장소 삭제
GET    /favorites/routes           # 즐겨찾기 경로 목록
POST   /favorites/routes           # 즐겨찾기 경로 추가
DELETE /favorites/routes/{id}      # 즐겨찾기 경로 삭제
```

#### 비즈니스 룰
- 장소와 경로 분리 관리
- 경로는 전체 데이터 저장 (Route FK 참조)
- 개수 제한 없음

---

### 5. history 도메인

#### 엔티티
```
SearchHistory
├── id: UUID (PK)
├── user_id: UUID (FK -> User)
├── route_id: UUID (FK -> Route)
├── searched_at: datetime
```

#### API
```
GET    /history                    # 검색 히스토리 목록
GET    /history/recommendations    # TOP 5 추천 (빈도+최근성)
DELETE /history/{id}               # 개별 삭제
DELETE /history                    # 전체 삭제
```

#### 비즈니스 룰
- 무제한 저장
- TOP 5 추천: 빈도수 + 최근성 가중치
- 개별/전체 삭제 지원

---

### 6. guides 도메인

#### 엔티티
```
Situation
├── id: UUID (PK)
├── code: str (unique, e.g., 'BUS_BOARDING')
├── order: int (정렬 순서)
├── is_active: bool

Intent
├── id: UUID (PK)
├── situation_id: UUID (FK -> Situation)
├── code: str
├── order: int

GuideContent
├── id: UUID (PK)
├── intent_id: UUID (FK -> Intent)
├── content_type: enum (INFO, GUIDE, PHRASE, WARNING, CTA, EXTERNAL_LINK)
├── order: int
├── external_url: str (nullable)
├── cta_action: str (nullable)

GuideContentTranslation
├── id: UUID (PK)
├── guide_content_id: UUID (FK -> GuideContent)
├── language: str (ko, en)
├── title: str
├── content: str
├── cta_label: str (nullable)
```

#### API
```
GET    /guides/situations          # 상황 목록
GET    /guides/situations/{code}/intents  # 상황별 의도 목록
GET    /guides/intents/{id}/contents  # 의도별 가이드 콘텐츠 목록
```

#### 비즈니스 룰
- 6가지 콘텐츠 유형: 정보/안내/문장/주의/CTA/외부링크
- 다국어: 번역 테이블 분리 (guide_translations)
- 관리자 페이지 없음 (시드 데이터로 초기화)

---

### 7. situations 도메인

#### 엔티티
```
UserJourney
├── id: UUID (PK)
├── user_id: UUID (FK -> User)
├── route_id: UUID (FK -> Route)
├── current_leg_index: int (현재 구간)
├── status: enum (STARTED, IN_PROGRESS, COMPLETED, CANCELLED)
├── started_at: datetime
├── completed_at: datetime (nullable)

LegProgress
├── id: UUID (PK)
├── user_journey_id: UUID (FK -> UserJourney)
├── leg_index: int
├── status: enum (PENDING, IN_PROGRESS, COMPLETED)
├── started_at: datetime (nullable)
├── completed_at: datetime (nullable)
├── confirmed_by_user: bool
├── gps_lat: float (nullable)
├── gps_lon: float (nullable)
```

#### API
```
POST   /journeys                   # 여정 시작
GET    /journeys/current           # 현재 진행 중인 여정
PATCH  /journeys/{id}/leg/{index}/complete  # 구간 완료 확인
PATCH  /journeys/{id}/leg/{index}/back      # 이전 구간으로
POST   /journeys/{id}/cancel       # 여정 취소
GET    /journeys/{id}              # 여정 상세
```

#### 비즈니스 룰
- 구간 전환: GPS + 사용자 확인 병행
- 상태 저장: 서버 + 클라이언트 동기화
- 이전/홈 버튼 모두 지원

---

### 8. pois 도메인

#### API
```
GET    /pois/nearby                # 경로 주변 POI 검색
GET    /pois/categories            # POI 카테고리 목록
```

#### 비즈니스 룰
- 추천 범위: 전체 경로
- 카테고리: 관광/맛집/카페/쇼핑 4가지
- 데이터 출처: Naver 지역검색만

#### 외부 연동
- Naver 지역검색 API

---

## 📊 진행률

- [x] Phase 0: 요구사항 명확화 ✅ 100%
- [x] Phase 1: 외부 라이브러리 리서치 ✅ 100%
- [x] Phase 2: 도메인 인터뷰 ✅ 100%
- [x] Phase 3: SPEC 작성 ✅ 100%
- [ ] Phase 4: 코드 생성 ⏳ 대기 중

---

## Phase 3 완료 결과

### 생성된 문서

| 파일 | 경로 | 설명 |
|------|------|------|
| SPEC.md | `docs/SPEC.md` | 전체 프로젝트 명세서 |

### SPEC.md 포함 내용

1. **프로젝트 개요**: 외국인 관광객 대상 대중교통 가이드 서비스
2. **기술 스택**: FastAPI, SQLModel, JWT, TMAP, Naver Maps
3. **8개 도메인 상세 스펙**:
   - users (회원)
   - routes (경로 탐색)
   - places (장소 검색)
   - favorites (즐겨찾기)
   - history (검색 히스토리)
   - guides (상황별 가이드)
   - situations/journeys (여정 관리)
   - pois (POI 추천)
4. **외부 API 연동 스펙**: TMAP, Naver Maps
5. **데이터베이스 ERD** (텍스트)
6. **구현 우선순위**: 4단계 + 병렬 그룹

---

## 🎯 다음 액션

1. **Phase 4**: 코드 생성 (TDD)
   - Group A (병렬): users, places, guides
   - Group B: routes
   - Group C (병렬): favorites, history, journeys
   - Group D: pois
   - verification-loop 6단계 통과 필수
