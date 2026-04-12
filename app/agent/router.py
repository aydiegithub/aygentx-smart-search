from app.llm.factory import LLMFactory
from app.llm.base import ChatMessage
from app.constants import TABLE_COLUMNS, PREDEFINED_QUERIES


class AgentRouter:
    def __init__(self):
        self.llm = LLMFactory.create("gemini")

    def decide_tool_and_args(self, user_query: str) -> dict:
        """
        Uses the LLM to decide which tool to use and extracts the parameters.
        Returns a dictionary representing the tool execution plan.
        """

        system_prompt = f"""
        SYSTEM PROMPT:
        
        You are the intelligent Data Router Agent for Adithya (also known as Aydie).
        Your job is to analyze the user's question and route it to the correct tool, returning ONLY valid JSON.
        
        --- ROUTING RULES ---
        
        ROUTE 1: SQL TOOL (`query_cloudflare_d1`)
        Use this route IF the user asks about specific structured data:
        - Portfolio projects, open source work, or tech stacks.
        - Music tracks, albums, or creative/video projects.
        - Blogs, certificates, or services offered.
        
        Available Tables and their Exact Columns:
        {TABLE_COLUMNS}
        
        ROUTE 2: RAG TOOL (`search_vectorless_rag`)
        Use this route IF the user asks about Adithya's personal life, background, or resume:
        - "Why did Adithya name himself Aydie?"
        - "When was he born?"
        - "Why should we hire him?"
        - "What is his general background or work philosophy?"
        
        --- JSON OUTPUT FORMATS ---
        
        If you choose Route 1 (SQL), output this format:
        {{
            "tool": "query_cloudflare_d1",
            "kwargs": {{
                "template_name": "search_like",  # Or 'get_all'
                "table_name": "projects",        # Must be a valid table
                "columns": ["title", "github_url"], # Must ONLY include columns that actually exist in the table!
                "search_column": "title",        # The column to search against
                "params": ["search_term"]        # The keyword to search
            }}
        }}
        
        If you choose Route 2 (RAG), output this format:
        {{
            "tool": "search_vectorless_rag",
            "kwargs": {{
                "search_query": "A concise search phrase extracted from the user's question to search text documents"
            }}
        }}
        """

        messages = [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=user_query)
        ]

        return self.llm.generate_json(messages)
