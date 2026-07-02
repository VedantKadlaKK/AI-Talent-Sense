from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Talent Sense API"
    app_version: str = "0.1.0"

    database_url: str = "sqlite:///./talent_sense.db"

    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    grok_api_key: str | None = None
    grok_api_url: str = "https://api.x.ai/v1/chat/completions"
    grok_model: str = "grok-2-latest"

    use_mock_ai: bool = True

    # NEW
    github_token: str | None = None
    use_mock_talent_sources: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
