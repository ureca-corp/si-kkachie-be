from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.config import settings
from src.core.exceptions import register_error_handlers
from src.modules.health.controller import router as health_router
from src.modules.users.controller import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 수명 주기 관리"""
    # Startup
    # 마이그레이션은 서버 시작 전에 수동으로 실행:
    # uv run alembic upgrade head
    yield
    # Shutdown


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

# 예외 핸들러 등록
register_error_handlers(app)

# 라우터 등록
app.include_router(health_router)
app.include_router(users_router, prefix="/api")
