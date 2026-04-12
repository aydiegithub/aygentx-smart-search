from openai import OpenAI
import json
from app.llm.base import BaseLLM, ChatMessage
from typing import List, Dict, Any

from app.core.logging import Logger
logger = Logger(__name__)


class OpenAILLM(BaseLLM):
    def __init__(self, api_key: str, model_name: str, base_url: str = None):
        logger.info(
            f"Entered __init__ of OpenAILLM with api_key=***REDACTED***, model_name={model_name}, base_url={base_url}")
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model_name = model_name

    def generate(self, messages: List[ChatMessage]) -> str:
        logger.info(f"Entered generate of OpenAILLM with messages={messages}")
        logger.info(f"Entered generate of OpenAILLM with messages={messages}")
        logger.info(f"Entering generate")
        formatted_messages = [
            {"role": m.role, "content": m.content} for m in messages
        ]
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=formatted_messages
        )
        return response.choices[0].message.content

    def generate_json(self, messages: List[ChatMessage]) -> Dict[str, Any]:
        logger.info(
            f"Entered generate_json of OpenAILLM with messages={messages}")
        logger.info(
            f"Entered generate_json of OpenAILLM with messages={messages}")
        logger.info(f"Entering generate_json")
        formatted_messages = [
            {"role": m.role, "content": m.content} for m in messages
        ]

        # formatted_messages.insert(
        # 0, {"role": "system", "content": "You must respond in valid JSON format."})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=formatted_messages,
            response_format={"type": "json_object"}
        )

        json_string = response.choices[0].message.content

        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse JSON from model output: {json_string}") from e
