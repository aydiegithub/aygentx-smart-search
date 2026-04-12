from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import List, Dict, Any

from app.core.logging import Logger
logger = Logger(__name__)


class ChatMessage(BaseModel):
    role: str
    content: str


class BaseLLM(ABC):
    @abstractmethod
    def generate(self, messages: List[ChatMessage]) -> str:
        logger.info(f"Entered generate of BaseLLM with messages={messages}")
        logger.info(f"Entered generate of BaseLLM with messages={messages}")
        logger.info(f"Entering generate")
        pass

    @abstractmethod
    def generate_json(self, messages: List[ChatMessage]) -> Dict[str, Any]:
        logger.info(f"Entered generate_json of BaseLLM with messages={messages}")
        logger.info(f"Entered generate_json of BaseLLM with messages={messages}")
        logger.info(f"Entering generate_json")
        pass
