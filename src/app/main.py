"""FastAPI 애플리케이션 메인

Kkachie 백엔드 - 외국인 여행자를 위한 실시간 번역 및 미션 가이드 앱
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.config import settings
from src.core.exceptions import register_error_handlers
from src.modules.health import router as health_router

# 도메인 라우터
from src.modules.locations import router as locations_router
from src.modules.missions import router as missions_router
from src.modules.phrases import router as phrases_router
from src.modules.profiles import router as profiles_router
from src.modules.routes import router as routes_router
from src.modules.translations import router as translations_router


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
app.include_router(profiles_router)
app.include_router(translations_router)
app.include_router(missions_router)
app.include_router(phrases_router)
app.include_router(routes_router)
app.include_router(locations_router)
