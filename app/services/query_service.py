import json
from app.agent.router import AgentRouter
from app.api.mcp_server import query_cloudflare_d1
from app.core.logging import Logger
from app.llm.factory import LLMFactory
from app.llm.base import ChatMessage
from app.core.config import settings
from app.agent.memory import memory_store

logging = Logger()


class QueryService:
    def __init__(self):
        self.router = AgentRouter()

    def process_query(self, user_text: str, model_name: str, session_id: str, urls: list = None) -> dict:
        logging.info(
            f"User Input Received: '{user_text}' for session: {session_id}")
        logging.info("Asking agent to route...")

        # 1. Routing Node
        history = memory_store.get_history(session_id=session_id)
        decision = self.router.decide_tool_and_args(user_text, history)
        logging.info(f"Agent Decision: {json.dumps(decision, indent=2)}")

        is_safe = decision.get("is_safe", True)
        in_domain = decision.get("in_domain", True)
        direct_response = decision.get("direct_response")
        tool_name = decision.get("tool")

        # --- MODERATION CHECK ---
        if not is_safe:
            logging.warning("User message flagged as unsafe.")
            msg = direct_response or "Your conversation has been flagged for inappropriate content. I cannot continue this discussion."
            return self._build_rejection(msg, [])

        # --- OUT OF DOMAIN CHECK ---
        if not in_domain:
            logging.warning("User message flagged as out of domain.")
            msg = direct_response or "I am specifically designed to answer questions about Aydie's Avenue, Aditya's portfolio, his music, life story, and projects."
            return self._build_rejection(msg, [])

        # --- DIRECT RESPONSE (No tool needed!) ---
        # Handles greetings, "Who are you?", comparisons, etc.
        if not tool_name and direct_response:
            logging.info(
                "Agent provided a direct response. Bypassing tool execution.")

            # Save to memory and return immediately
            memory_store.add_message(session_id, "user", user_text)
            memory_store.add_message(session_id, "assistant", direct_response)

            return {
                "status": "success",
                "tool_used": "none",
                "ai_response": direct_response,
                "suggested_links": [],
                "data": []
            }

        kwargs = decision.get("kwargs", {})
        raw_data = []

        # 2. Execution Node
        if tool_name == "query_cloudflare_d1":
            logging.info("Executing the tool [query_cloudflare_d1] ...")
            raw_tool_response = query_cloudflare_d1(**kwargs)
            parsed_response = json.loads(raw_tool_response)

            if parsed_response.get("error"):
                logging.error(f"Error using tool [{tool_name}]")
                return self._build_rejection("I encountered an error while accessing the database.", [])

            raw_data = parsed_response.get("data", [])
            logging.info(
                f"Successfully fetched {len(raw_data)} records using tool [{tool_name}]")

        elif tool_name == "search_vectorless_rag":
            logging.info(f"Successfully routed to parked tool [{tool_name}]")
            return self._build_rejection("This question requires searching documents, but my document search feature is currently parked.", [])

        else:
            logging.error("Error deciding the tool.")
            return self._build_rejection("I'm sorry, I couldn't figure out how to find that information.", [])

        # 3. SYNTHESIS NODE (Processed Output)
        logging.info("Synthesizing raw data into a conversational response...")

        synthesis_llm = LLMFactory.create(provider="gemini", model=model_name)

        synthesis_prompt = settings.synthesis_prompt_template.format(
            user_text=user_text,
            raw_data=json.dumps(raw_data, indent=2)
        )

        synth_messages = history.copy()
        synth_messages.append(ChatMessage(
            role="user", content=synthesis_prompt))

        try:
            synthesis_result = synthesis_llm.generate_json(synth_messages)
            logging.info("Successfully formatted final response.")

            ai_response = synthesis_result.get(
                "ai_response", "Here is the information you requested.")
            suggested_links = synthesis_result.get("suggested_links", [])

            # --- HANDLE MIXED QUERIES ---
            # If the AI had a direct response (e.g. "I can't code, but here are the projects")
            # We prepend it to the synthesized database data.
            if direct_response:
                ai_response = f"{direct_response}\n\n{ai_response}"

            memory_store.add_message(session_id, "user", user_text)
            memory_store.add_message(session_id, "assistant", ai_response)

            return {
                "status": "success",
                "tool_used": tool_name,
                "ai_response": ai_response,
                "suggested_links": suggested_links,
                "data": raw_data
            }
        except Exception as e:
            logging.error(f"Error during synthesis step: {str(e)}")
            return self._build_rejection("I found the data, but encountered an error formatting it perfectly.", raw_data)

    def _build_rejection(self, message: str, data: list) -> dict:
        return {
            "status": "rejected",
            "tool_used": "none",
            "ai_response": message,
            "suggested_links": [],
            "data": data
        }
