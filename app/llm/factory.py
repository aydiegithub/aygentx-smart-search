import os
from app.llm.base import BaseLLM
from app.llm.client import OpenAILLM
from app.constants import (GEMINI_MODEL,
                           OPENAI_MODEL,
                           GEMINI_API_KEY,
                           OPENAI_API_KEY,
                           GEMINI_BASE_URL,
                           GEMINI_PROVIDER)

from app.core.logging import Logger
logger = Logger(__name__)


class LLMFactory:
    @staticmethod
    def create(provider: str = GEMINI_PROVIDER, model: str = GEMINI_MODEL) -> BaseLLM:
        logger.info(f"Entered create of LLMFactory with provider={provider}, model={model}")
        logger.info(f"Entering create")
        if provider == "openai":
            return OpenAILLM(
                api_key=OPENAI_API_KEY,
                model_name=model
            )
        elif provider == "gemini":
            return OpenAILLM(
                api_key=GEMINI_API_KEY,
                model_name=model,
                base_url=GEMINI_BASE_URL
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
