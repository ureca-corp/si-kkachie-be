from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Transit Guide API"
    DEBUG: bool = False
    VERSION: str = "0.1.0"

    # Database
    DATABASE_URL: str = "sqlite:///./app.db"

    # Auth - 기본값 JWT
    AUTH_BACKEND: str = "jwt"  # "jwt" | "firebase" | "supabase"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1시간
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30일

    # External API - TMAP
    TMAP_APP_KEY: str | None = None

    # External API - Naver Maps
    NAVER_CLIENT_ID: str | None = None
    NAVER_CLIENT_SECRET: str | None = None

    # Firebase (AUTH_BACKEND=firebase일 때만)
    FIREBASE_CREDENTIALS: str | None = None

    # Supabase (AUTH_BACKEND=supabase일 때만)
    SUPABASE_URL: str | None = None
    SUPABASE_KEY: str | None = None

    # Storage
    STORAGE_BACKEND: str | None = None  # "s3" | "r2" | "supabase" | None

    # AWS S3
    S3_BUCKET: str | None = None
    S3_REGION: str | None = None
    S3_ACCESS_KEY: str | None = None
    S3_SECRET_KEY: str | None = None

    # Cloudflare R2
    R2_BUCKET: str | None = None
    R2_ACCOUNT_ID: str | None = None
    R2_ACCESS_KEY: str | None = None
    R2_SECRET_KEY: str | None = None

    # Supabase Storage
    SUPABASE_STORAGE_BUCKET: str | None = None

    # Cache
    CACHE_BACKEND: str | None = None  # "redis" | "upstash" | None

    # Redis
    REDIS_URL: str | None = None  # redis://localhost:6379/0

    # Upstash Redis
    UPSTASH_REDIS_URL: str | None = None
    UPSTASH_REDIS_TOKEN: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
