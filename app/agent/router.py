from app.llm.factory import LLMFactory
from app.llm.base import ChatMessage
from app.constants import TABLE_COLUMNS, PREDEFINED_QUERIES
from app.core.config import settings
from app.core.logging import Logger
logger = Logger(__name__)


class AgentRouter:
    def __init__(self):
        logger.info(f"Entered __init__ of AgentRouter")
        self.llm = LLMFactory.create("gemini")

    def decide_tool_and_args(self, user_query: str) -> dict:
        logger.info(
            f"Entered decide_tool_and_args of AgentRouter with user_query={user_query}")
        """
        Uses the LLM to decide which tool to use and extracts the parameters.
        Returns a dictionary representing the tool execution plan.
        """

        logger.info(
            f"Entered decide_tool_and_args of AgentRouter with user_query={user_query}")
        system_prompt = settings.routing_prompt.format(
            table_columns=TABLE_COLUMNS
        )

        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=user_query)
        ]

        return self.llm.generate_json(messages)
