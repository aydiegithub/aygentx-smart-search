import json
from app.agent.router import AgentRouter
from app.api.mcp_server import query_cloudflare_d1
from app.core.logging import Logger

logging = Logger()


class QueryService:
    def __init__(self):
        self.router = AgentRouter()

    def process_query(self, user_text: str) -> dict:
        logging.info(f"User Input Received: '{user_text}'")
        logging.info(f"Asking agent to route...")

        decision = self.router.decide_tool_and_args(user_text)
        logging.info(f"Agent Decision: {json.dumps(decision, indent=2)}")

        tool_name = decision.get("tool")
        kwargs = decision.get("kwargs", {})

        # Execution Node
        if tool_name == "query_cloudflare_d1":
            logging.info(f"Executing the tool [query_cloudflare_d1] ...")
            raw_tool_response = query_cloudflare_d1(**kwargs)
            parsed_response = json.loads(raw_tool_response)

            if parsed_response.get("error"):
                logging.error(
                    f"There was error generating response using the tool [{tool_name}]")
                return {
                    "status": "error",
                    "tool_used": tool_name,
                    "data": [],
                    "message": parsed_response["error"]
                }

            logging.info("Formatting final response")
            logging.info(f"Sucessfully used tool [{tool_name}]")
            return {
                "status": "success",
                "tool_used": tool_name,
                "data": parsed_response.get("data", [])
            }

        elif tool_name == "search_vectorless_rag":
            logging.info(f"Sucessfully used tool [{tool_name}]")
            return {
                "status": "pending",
                "tool_used": tool_name,
                "data": [],
                "message": "Vectorless RAG is parked for now."
            }

        else:
            logging.error(f"Error deciding the tool..")
            return {
                "status": "error",
                "tool_used": "unknown",
                "data": [],
                "message": "Agent failed to route to a valid tool."
            }
