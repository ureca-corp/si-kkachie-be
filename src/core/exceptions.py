from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.core.response import ApiResponse, Status


def _format_validation_errors(errors: list) -> str:
    """Pydantic validation errors를 읽기 쉬운 메시지로 변환"""
    messages = []
    for error in errors:
        loc = ".".join(str(part) for part in error["loc"] if part != "body")
        msg = error["msg"]
        messages.append(f"{loc}: {msg}")
    return " | ".join(messages)


class AppError(Exception):
    """애플리케이션 기본 예외"""

    status: Status = Status.INTERNAL_ERROR
    message: str = "잠시 후 다시 시도해주세요"
    status_code: int = 500

    def __init__(self, message: str | None = None, status: Status | None = None):
        if message:
            self.message = message
        if status:
            self.status = status
        super().__init__(self.message)


class NotFoundError(AppError):
    """리소스를 찾을 수 없음"""

    status = Status.RESOURCE_NOT_FOUND
    message = "찾으시는 정보가 없어요"
    status_code = 404


class RouteNotFoundError(AppError):
    """경로를 찾을 수 없음"""

    status = Status.ROUTE_NOT_FOUND
    message = "경로를 찾을 수 없어요"
    status_code = 404


class UnauthorizedError(AppError):
    """인증 실패"""

    status = Status.USER_AUTHENTICATION_FAILED
    message = "로그인이 필요해요"
    status_code = 401


class ForbiddenError(AppError):
    """권한 없음"""

    status = Status.PERMISSION_DENIED
    message = "이 기능을 사용할 수 없어요"
    status_code = 403


class ConflictError(AppError):
    """리소스 충돌"""

    status = Status.RESOURCE_ALREADY_EXISTS
    message = "이미 등록된 정보예요"
    status_code = 409


class ValidationError(AppError):
    """유효성 검사 실패"""

    status = Status.VALIDATION_FAILED
    message = "입력 내용을 확인해주세요"
    status_code = 422


class TokenExpiredError(AppError):
    """토큰 만료"""

    status = Status.TOKEN_EXPIRED
    message = "다시 로그인해주세요"
    status_code = 401


class TokenInvalidError(AppError):
    """유효하지 않은 토큰"""

    status = Status.TOKEN_INVALID
    message = "보안 정책으로 로그아웃되었어요"
    status_code = 401


class DatabaseError(AppError):
    """데이터베이스 오류"""

    status = Status.DATABASE_ERROR
    message = "잠시 후 다시 시도해주세요"
    status_code = 503


class ExternalServiceError(AppError):
    """외부 서비스 오류"""

    status = Status.EXTERNAL_SERVICE_ERROR
    message = "외부 서비스 연결에 문제가 있어요"
    status_code = 502


def register_error_handlers(app: FastAPI) -> None:
    """FastAPI 앱에 예외 핸들러 등록"""
    from fastapi.exceptions import RequestValidationError

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        message = _format_validation_errors(exc.errors())
        return JSONResponse(
            status_code=422,
            content=ApiResponse(
                status=Status.VALIDATION_FAILED,
                message=message,
                data=None,
            ).model_dump(),
        )

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=ApiResponse(
                status=exc.status,
                message=exc.message,
                data=None,
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content=ApiResponse(
                status=Status.INTERNAL_ERROR,
                message="잠시 후 다시 시도해주세요",
                data=None,
            ).model_dump(),
        )
