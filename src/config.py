from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    github_token: str | None = None
    github_api_url: str = "https://api.github.com/graphql"
    request_timeout_seconds: float = 8.0
    cache_ttl_seconds: int = 14_400
    stale_ttl_seconds: int = 86_400
    mock_fallback: bool = True

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

