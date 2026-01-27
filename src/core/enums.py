"""공통 Enum 정의 (DDD_CLASS_DIAGRAM.md 기반)"""

from enum import Enum


class TranslationType(str, Enum):
    """번역 유형"""

    TEXT = "text"  # 텍스트 번역
    VOICE = "voice"  # 음성 번역 (STT + 번역 + TTS)


class MissionType(str, Enum):
    """미션 종류"""

    TAXI = "taxi"  # 택시 이용
    PAYMENT = "payment"  # 결제
    CHECKIN = "checkin"  # 체크인


class MissionStatus(str, Enum):
    """미션 진행 상태"""

    NOT_STARTED = "not_started"  # 시작 전
    IN_PROGRESS = "in_progress"  # 진행 중
    ENDED = "ended"  # 종료됨


class MissionResult(str, Enum):
    """미션 결과 (종료 시 선택)"""

    RESOLVED = "resolved"  # 해결됨
    PARTIALLY_RESOLVED = "partially_resolved"  # 부분 해결
    UNRESOLVED = "unresolved"  # 미해결


class PhraseCategory(str, Enum):
    """추천 문장 카테고리"""

    GREETING = "greeting"  # 인사
    REQUEST = "request"  # 요청
    CONFIRMATION = "confirmation"  # 확인
    THANKS = "thanks"  # 감사
    APOLOGY = "apology"  # 사과
    EMERGENCY = "emergency"  # 긴급 상황


class PreferredLanguage(str, Enum):
    """사용자 선호 언어"""

    KO = "ko"  # 한국어
    EN = "en"  # 영어


class RouteOption(str, Enum):
    """경로 옵션"""

    TRAOPTIMAL = "traoptimal"  # 실시간 최적
    TRAFAST = "trafast"  # 실시간 빠른길
    TRACOMFORT = "tracomfort"  # 실시간 편한길
    TRAAVOIDTOLL = "traavoidtoll"  # 무료 우선
    TRAAVOIDCARONLY = "traavoidcaronly"  # 자동차 전용도로 회피
