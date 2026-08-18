from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_SECRET_KEY: str = "change-me"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    DATABASE_URL: str = "postgresql+asyncpg://daragent:daragent@localhost:5432/daragent"

    REDIS_URL: str = "redis://localhost:6379/0"

    JWT_SECRET_KEY: str = "change-me-jwt"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    JWT_ALGORITHM: str = "HS256"

    STORAGE_PROVIDER: str = "minio"
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "daragent"
    MINIO_SECURE: bool = False

    YANDEX_DISK_OAUTH_TOKEN: str = ""
    YANDEX_DISK_BASE_PATH: str = "/daragent"

    YOOKASSA_SHOP_ID: str = ""
    YOOKASSA_SECRET_KEY: str = ""
    YOOKASSA_WEBHOOK_SECRET: str = ""
    YOOKASSA_RETURN_URL: str = "http://localhost:8000/api/v1/payments/callback"

    GROK_API_KEY: str = ""
    GROK_MODEL: str = "grok-2-latest"

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@daragent.ru"
    SMTP_USE_TLS: bool = True

    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_PROXY: str | None = None

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080"]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
