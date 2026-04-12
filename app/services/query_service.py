import json
from app.agent.router import AgentRouter
from app.api.mcp_server import query_cloudflare_d1
from app.core.logging import Logger
from app.llm.factory import LLMFactory
from app.llm.base import ChatMessage
from app.core.config import settings

logging = Logger()


class QueryService:
    def __init__(self):
        self.router = AgentRouter()

    def process_query(self, user_text: str, model_name: str, urls: list = None) -> dict:
        logging.info(f"User Input Received: '{user_text}'")
        logging.info("Asking agent to route...")

        # 1. Routing Node
        decision = self.router.decide_tool_and_args(user_text)
        logging.info(f"Agent Decision: {json.dumps(decision, indent=2)}")

        tool_name = decision.get("tool")
        kwargs = decision.get("kwargs", {})

        # 2. Execution Node
        if tool_name == "query_cloudflare_d1":
            logging.info("Executing the tool [query_cloudflare_d1] ...")
            raw_tool_response = query_cloudflare_d1(**kwargs)
            parsed_response = json.loads(raw_tool_response)

            if parsed_response.get("error"):
                logging.error(
                    f"There was an error generating response using the tool [{tool_name}]")
                return {
                    "status": "error",
                    "tool_used": tool_name,
                    "ai_response": "I encountered an error while accessing the database.",
                    "suggested_links": [],
                    "data": [],
                    "message": parsed_response["error"]
                }

            raw_data = parsed_response.get("data", [])
            logging.info(
                f"Successfully fetched {len(raw_data)} records using tool [{tool_name}]")

            # 3. SYNTHESIS NODE (Processed Output)
            logging.info(
                "Synthesizing raw data into a conversational response...")

            # Create the specific LLM requested by the user API call
            synthesis_llm = LLMFactory.create(
                provider="gemini", model=model_name)

            synthesis_prompt = settings.synthesis_prompt_template.format(
                user_text=user_text,
                raw_data=json.dumps(raw_data, indent=2)
            )

            try:
                # Generate the final conversational JSON
                synthesis_result = synthesis_llm.generate_json([
                    ChatMessage(role="user", content=synthesis_prompt)
                ])
                logging.info("Successfully formatted final response.")

                return {
                    "status": "success",
                    "tool_used": tool_name,
                    "ai_response": synthesis_result.get("ai_response", "Here is the information you requested."),
                    "suggested_links": synthesis_result.get("suggested_links", []),
                    "data": raw_data
                }
            except Exception as e:
                logging.error(f"Error during synthesis step: {str(e)}")
                return {
                    "status": "partial_success",
                    "tool_used": tool_name,
                    "ai_response": "I found the data, but encountered an error formatting it perfectly.",
                    "suggested_links": [],
                    "data": raw_data,
                    "message": str(e)
                }

        # Handle the parked RAG tool
        elif tool_name == "search_vectorless_rag":
            logging.info(f"Successfully routed to parked tool [{tool_name}]")
            return {
                "status": "pending",
                "tool_used": tool_name,
                "ai_response": "This question requires searching documents, but my document search feature is currently parked.",
                "suggested_links": [],
                "data": [],
                "message": "Vectorless RAG is parked for now."
            }

        # Fallback error
        else:
            logging.error("Error deciding the tool.")
            return {
                "status": "error",
                "tool_used": "unknown",
                "ai_response": "I'm sorry, I couldn't figure out how to find that information.",
                "suggested_links": [],
                "data": [],
                "message": "Agent failed to route to a valid tool."
            }
