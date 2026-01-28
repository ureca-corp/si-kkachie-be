"""routes 유틸리티

거리/시간 포맷팅 함수
"""


def format_distance(meters: int) -> str:
    """거리를 읽기 쉬운 형식으로 변환"""
    if meters < 1000:
        return f"{meters}m"
    km = meters / 1000
    return f"{km:.1f}km"


def format_duration(seconds: int) -> str:
    """시간을 읽기 쉬운 형식으로 변환"""
    minutes = seconds // 60
    if minutes < 60:
        return f"약 {minutes}분"
    hours = minutes // 60
    remaining_minutes = minutes % 60
    if remaining_minutes == 0:
        return f"약 {hours}시간"
    return f"약 {hours}시간 {remaining_minutes}분"
