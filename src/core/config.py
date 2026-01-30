from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Kkachie API"
    DEBUG: bool = False
    VERSION: str = "0.1.0"

    # Database
    DATABASE_URL: str = "sqlite:///./app.db"

    # Supabase
    SUPABASE_URL: str | None = None
    SUPABASE_KEY: str | None = None  # anon key
    SUPABASE_SERVICE_KEY: str | None = None  # 백엔드 전용
    SUPABASE_JWKS_URL: str | None = None  # JWT 검증용
    SUPABASE_STORAGE_BUCKET: str = "profiles"

    # Naver Cloud Platform (Maps, Directions, Reverse Geocoding)
    NAVER_CLIENT_ID: str | None = None
    NAVER_CLIENT_SECRET: str | None = None

    # Naver Developers (Local Search API)
    NAVER_SEARCH_CLIENT_ID: str | None = None
    NAVER_SEARCH_CLIENT_SECRET: str | None = None

    # Google Cloud (Speech-to-Text, Text-to-Speech, Translation)
    # GOOGLE_APPLICATION_CREDENTIALS 환경변수로 서비스 계정 키 경로 설정 필요
    GOOGLE_CLOUD_PROJECT: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # .env에 있는 사용하지 않는 변수 무시
    )


settings = Settings()
