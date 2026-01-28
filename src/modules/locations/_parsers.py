"""Naver API 응답 파싱

공유 모듈: 여러 기능에서 사용하는 파싱 로직
"""

import re


def parse_reverse_geocode_response(
    data: dict,
    lat: float,
    lng: float,
) -> tuple[str, str, str]:
    """Naver Reverse Geocoding 응답 파싱

    Args:
        data: Naver API 응답
        lat: 요청한 위도
        lng: 요청한 경도

    Returns:
        (name, address, road_address) 튜플
    """
    results = data.get("results", [])

    road_address = ""
    address = ""
    building_name = ""

    for result in results:
        region = result.get("region", {})
        land = result.get("land", {})

        if result.get("name") == "roadaddr":
            road_address = _build_road_address(region, land)
            building_name = land.get("addition0", {}).get("value", "")
        elif result.get("name") == "addr":
            address = _build_jibun_address(region, land)

    name = building_name or _extract_location_name(road_address)

    return name, address, road_address


def parse_place_item(item: dict) -> dict:
    """Naver Local Search 응답 아이템 파싱

    Args:
        item: Naver API 응답의 items 배열 요소

    Returns:
        파싱된 장소 정보 dict
    """
    # mapx/mapy: KATECH 좌표 (1/10000000 도 단위)
    place_lng = int(item.get("mapx", 0)) / 10000000
    place_lat = int(item.get("mapy", 0)) / 10000000

    # HTML 태그 제거 (<b> 검색어 강조)
    name = _strip_html_tags(item.get("title", ""))

    return {
        "id": _generate_place_id(item),
        "name": name,
        "category": item.get("category", ""),
        "address": item.get("address", ""),
        "road_address": item.get("roadAddress", ""),
        "lat": place_lat,
        "lng": place_lng,
    }


def _build_road_address(region: dict, land: dict) -> str:
    """도로명 주소 조합: 시도 + 시군구 + 읍면동 + 도로명 + 번호"""
    parts = [
        region.get(area, {}).get("name", "")
        for area in ["area1", "area2", "area3"]
    ]
    parts = [p for p in parts if p]

    if land.get("name"):
        parts.append(land["name"])
    if land.get("number1"):
        parts.append(land["number1"])

    return " ".join(parts)


def _build_jibun_address(region: dict, land: dict) -> str:
    """지번 주소 조합: 시도 + 시군구 + 읍면동 + 리 + 번지"""
    parts = [
        region.get(area, {}).get("name", "")
        for area in ["area1", "area2", "area3", "area4"]
    ]
    parts = [p for p in parts if p]

    if land.get("number1"):
        jibun = land["number1"]
        if land.get("number2"):
            jibun += f"-{land['number2']}"
        parts.append(jibun)

    return " ".join(parts)


def _extract_location_name(road_address: str) -> str:
    """도로명에서 장소명 추출 (도로명 + 번호)"""
    parts = road_address.split()
    return " ".join(parts[-2:]) if len(parts) >= 2 else road_address


def _strip_html_tags(text: str) -> str:
    """HTML 태그 제거"""
    return re.sub(r"<[^>]+>", "", text)


def _generate_place_id(item: dict) -> str:
    """장소 고유 ID 생성"""
    # link에서 ID 추출 또는 좌표 기반 생성
    link = item.get("link", "")
    if "id=" in link:
        return f"naver_{link.split('id=')[-1].split('&')[0]}"
    return f"naver_{item.get('mapx', '')}_{item.get('mapy', '')}"
