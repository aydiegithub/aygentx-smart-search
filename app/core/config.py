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
                           GEMINI_PROVIDER,
                           TITLE,
                           DESCRIPTION,
                           VERSION,
                           APP_ENV,
                           ROUTING_PROMPT_TEMPLATE,
                           SYNTHESIS_PROMPT_TEMPLATE,
                           DOWNLOAD_FILE_NAME)


from typing import Optional
from app.core.logging import Logger
logger = Logger(__name__)


class Settings(BaseSettings):
    project_name: str = TITLE
    project_description: str = DESCRIPTION
    project_version: str = VERSION
    api_secret_key: str = "default-dev-key"
    development_env: str = APP_ENV

    # Cloudflare D1 Credentials
    cloudflare_account_id: str = CLOUDFLARE_ACCOUNT_ID
    cloudflare_database_id: str = CLOUDFLARE_DATABASE_ID
    cloudflare_api_token: str = CLOUDFLARE_API_TOEKN
    cloudflare_base_url: str = CLOUDFLARE_BASE_URL

    #  LLM Credentials
    gemini_api_key: str = GEMINI_API_KEY
    gemini_base_url: Optional[str] = GEMINI_BASE_URL
    gemini_model: str = GEMINI_MODEL
    gemini_provider: str = GEMINI_PROVIDER

    # optional if switching later
    openai_api_key: Optional[str] = OPENAI_API_KEY
    openai_model: Optional[str] = OPENAI_MODEL  # optional if switching later
    # optional if switching later
    openai_provider: Optional[str] = OPENAI_PROVIDER

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    routing_prompt: str = ROUTING_PROMPT_TEMPLATE
    synthesis_prompt_template: str = SYNTHESIS_PROMPT_TEMPLATE

    download_file_name: str = DOWNLOAD_FILE_NAME


@lru_cache
def get_settings() -> Settings:
    logger.info(f"Entered get_settings")
    """ 
    Create a cached instance of the settings so we don't re-read the .env file every time we need a variable.
    """
    return Settings()


settings = get_settings()
