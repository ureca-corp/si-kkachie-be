"""translations 도메인 예외

클린 아키텍처: Domain Layer에서 발생하는 비즈니스 규칙 위반 예외
AppError를 상속받아 전역 예외 핸들러에서 자동 처리됨
"""

from src.core.exceptions import AppError
from src.core.response import Status


class InvalidCategoryError(AppError):
    """유효하지 않은 카테고리 조합"""

    status = Status.INVALID_CATEGORY
    message = "유효하지 않은 카테고리 조합이에요"
    status_code = 400


class InvalidSubCategoryError(AppError):
    """유효하지 않은 서브 카테고리"""

    status = Status.INVALID_SUB_CATEGORY
    message = "유효하지 않은 서브 카테고리예요"
    status_code = 400


class ThreadNotFoundError(AppError):
    """스레드를 찾을 수 없음"""

    status = Status.THREAD_NOT_FOUND
    message = "스레드를 찾을 수 없어요"
    status_code = 404


class ThreadAccessDeniedError(AppError):
    """스레드 접근 권한 없음 (다른 사용자의 스레드)"""

    status = Status.THREAD_NOT_FOUND  # 보안상 404로 응답
    message = "스레드를 찾을 수 없어요"
    status_code = 404


class TranslationNotFoundError(AppError):
    """번역 기록을 찾을 수 없음"""

    status = Status.TRANSLATION_NOT_FOUND
    message = "번역 기록을 찾을 수 없어요"
    status_code = 404
