import os
from app.llm.base import BaseLLM
from app.llm.client import OpenAILLM
from app.core.config import settings

from app.core.logging import Logger
logger = Logger(__name__)


class LLMFactory:
    @staticmethod
    def create(provider: str = settings.gemini_provider, model: str = settings.gemini_model) -> BaseLLM:
        logger.info(
            f"Entered create of LLMFactory with provider={provider}, model={model}")
        if provider == "openai":
            return OpenAILLM(
                api_key=settings.openai_api_key,
                model_name=model
            )
        elif provider == "gemini":
            return OpenAILLM(
                api_key=settings.gemini_api_key,
                model_name=model,
                base_url=settings.gemini_base_url
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
