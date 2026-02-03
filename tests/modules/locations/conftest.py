"""locations 도메인 테스트 픽스처"""

import pytest


@pytest.fixture
def reverse_geocode_response() -> dict:
    """Mock Naver Reverse Geocoding API response (서울시청)"""
    return {
        "status": {"code": 0, "name": "ok", "message": "done"},
        "results": [
            {
                "name": "roadaddr",
                "region": {
                    "area1": {"name": "서울특별시"},
                    "area2": {"name": "중구"},
                    "area3": {"name": "태평로1가"},
                },
                "land": {
                    "name": "세종대로",
                    "number1": "110",
                    "addition0": {"type": "building", "value": "서울시청"},
                },
            },
            {
                "name": "addr",
                "region": {
                    "area1": {"name": "서울특별시"},
                    "area2": {"name": "중구"},
                    "area3": {"name": "태평로1가"},
                    "area4": {"name": ""},
                },
                "land": {"number1": "31", "number2": ""},
            },
        ],
    }


@pytest.fixture
def reverse_geocode_not_found_response() -> dict:
    """Mock Naver Reverse Geocoding API response - 결과 없음"""
    return {
        "status": {"code": 3, "name": "no result", "message": "no result"},
        "results": [],
    }


@pytest.fixture
def place_search_response() -> dict:
    """Mock Naver Local Search API response"""
    return {
        "lastBuildDate": "Mon, 27 Jan 2025 10:00:00 +0900",
        "total": 5,
        "start": 1,
        "display": 5,
        "items": [
            {
                "title": "<b>강남</b>역",
                "link": "https://map.naver.com/v5/entry/place/21149144",
                "category": "지하철역",
                "description": "",
                "telephone": "",
                "address": "서울특별시 강남구 역삼동 858",
                "roadAddress": "서울특별시 강남구 강남대로 396",
                "mapx": "1270276144",
                "mapy": "374979890",
            },
            {
                "title": "<b>강남</b>역 스타벅스",
                "link": "https://map.naver.com/v5/entry/place/12345678",
                "category": "카페",
                "description": "",
                "telephone": "02-1234-5678",
                "address": "서울특별시 강남구 역삼동 100",
                "roadAddress": "서울특별시 강남구 테헤란로 100",
                "mapx": "1270280000",
                "mapy": "374982000",
            },
        ],
    }


@pytest.fixture
def place_search_empty_response() -> dict:
    """Mock Naver Local Search API response - 결과 없음"""
    return {
        "lastBuildDate": "Mon, 27 Jan 2025 10:00:00 +0900",
        "total": 0,
        "start": 1,
        "display": 0,
        "items": [],
    }


@pytest.fixture
def category_search_response() -> dict:
    """Mock Kakao Category Search API response"""
    return {
        "total_count": 45,
        "is_end": False,
        "places": [
            {
                "id": "8569385",
                "name": "스타벅스 강남역점",
                "category": "카페",
                "address": "서울 강남구 역삼동 858",
                "road_address": "서울 강남구 강남대로 396",
                "phone": "02-555-1234",
                "lat": 37.4979,
                "lng": 127.0276,
                "distance_m": 150,
                "place_url": "http://place.map.kakao.com/8569385",
            },
            {
                "id": "12345678",
                "name": "투썸플레이스 강남점",
                "category": "카페",
                "address": "서울 강남구 역삼동 100",
                "road_address": "서울 강남구 테헤란로 100",
                "phone": "02-555-5678",
                "lat": 37.4985,
                "lng": 127.0280,
                "distance_m": 300,
                "place_url": "http://place.map.kakao.com/12345678",
            },
        ],
    }


@pytest.fixture
def category_search_empty_response() -> dict:
    """Mock Kakao Category Search API response - 결과 없음"""
    return {
        "total_count": 0,
        "is_end": True,
        "places": [],
    }
