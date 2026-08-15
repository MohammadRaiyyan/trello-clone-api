from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MIN: int
    VERIFY_REFRESH_TOKEN_EXPIRE_HR: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    DEBUG: bool
    APP_NAME: str
    APP_VERSION: str
    RESEND_API_KEY: str
    EMAIL_FROM: str
    FRONTEND_URL: str
    INVITATION_EXPIRE_HOURS: int

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()  # pyright: ignore[reportCallIssue]
