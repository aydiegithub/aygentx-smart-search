from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from app.constants import TITLE
from app.constants import (CLOUDFLARE_ACCOUNT_ID,
                           CLOUDFLARE_DATABASE_ID,
                           CLOUDFLARE_API_TOEKN,
                           CLOUDFLARE_BASE_URL,
                           GEMINI_API_KEY,
                           OPENAI_API_KEY,
                           GEMINI_BASE_URL,
                           GEMINI_MODEL,
                           OPENAI_MODEL,
                           OPENAI_PROVIDER,
                           GEMINI_PROVIDER)


class Settings(BaseSettings):
    project_name: str = TITLE
    api_secret_key: str = "default-dev-key"

    # Cloudflare D1 Credentials
    cloudflare_account_id: str = CLOUDFLARE_ACCOUNT_ID
    cloudflare_database_id: str = CLOUDFLARE_DATABASE_ID
    cloudflare_api_token: str = CLOUDFLARE_API_TOEKN
    cloudflare_base_url: str = CLOUDFLARE_BASE_URL

    #  LLM Credentials
    gemini_api_key: str = GEMINI_API_KEY
    gemini_base_url: str = GEMINI_BASE_URL
    gemini_model: str = GEMINI_MODEL
    gemini_provider: str = GEMINI_PROVIDER

    openai_api_key: str = OPENAI_API_KEY  # optional if switching later
    openai_model: str = OPENAI_MODEL  # optional if switching later
    openai_provider: str = OPENAI_PROVIDER  # optional if switching later

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> Settings:
    """ 
    Create a cached instance of the settings so we don't re-read the .env file every time we need a variable.
    """
    return Settings()


settings = get_settings()
