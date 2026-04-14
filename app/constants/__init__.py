import os
import yaml
from dotenv import load_dotenv

load_dotenv()

TITLE: str = "AygentX Smart Search"
DESCRIPTION: str = (
    "AygentX Smart Search is a custom MCP-powered AI agent built for Aydie's Avenue. "
    "It intelligently retrieves and responds to any query related to the brand, its ecosystem, "
    "and the journey of its founder, Aditya Dinesh K. "
    "From structured information to deep contextual insights, the system is designed to handle "
    "everything—from standard lookups to unconventional, complex, and exploratory queries—"
    "delivering precise, meaningful, and dynamic responses in real time."
)
VERSION: str = "1.0.0-beta.1"

# "local" writes logs to a file, "prod" logs only to console to avoid AWS SAM errors
APP_ENV: str = "local"  # "prod"


GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

CLOUDFLARE_DATABASE_ID: str = os.getenv("CLOUDFLARE_DATABASE_ID")
CLOUDFLARE_ACCOUNT_ID: str = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOEKN: str = os.getenv("CLOUDFLARE_API_TOEKN")

API_SECRET_KEY: str = "default-dev-key"

GEMINI_MODEL: str = "gemini-3.1-flash-lite-preview"
GEMINI_LIVE_MODEL: str = "gemini-2.5-flash-native-audio-latest"
RAG_REASONING_MODEL: str = "gemini-2.5-pro"

OPENAI_MODEL: str = "gpt-4o-mini"

GEMINI_PROVIDER: str = "gemini"
OPENAI_PROVIDER: str = "openai"

GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
CLOUDFLARE_BASE_URL: str = "https://api.cloudflare.com/client/v4/accounts/{account_id}/d1/database/{database_id}/query"

SCHEMA_PATH: str = "app/models/schema.yml"

with open(SCHEMA_PATH, "r") as f:
    schema_data = yaml.safe_load(f)

PREDEFINED_QUERIES: dict = schema_data.get("queries", {})
TABLE_COLUMNS = {}
for table_name, table_data in schema_data.get("tables", {}).items():
    TABLE_COLUMNS[table_name] = set(table_data.get("columns", {}).keys())

PROMPTS_PATH: str = "app/prompts/prompts.yaml"
with open(PROMPTS_PATH, "r", encoding="utf-8") as file:
    _prompts = yaml.safe_load(file)

# Export the prompts
ROUTING_PROMPT_TEMPLATE = _prompts.get("routing_prompt", "")
SYNTHESIS_PROMPT_TEMPLATE = _prompts.get("synthesis_prompt", "")
RAG_INNGESTION_PROMPT = _prompts.get("rag_ingestion_prompt")
RAG_NODE_SELECTION_PROMPT = _prompts.get("rag_node_selection_prompt")
VOICE_AGENT_PROMPT = _prompts.get("voice_agent_prompt")

DOWNLOAD_FILE_NAME: str = "-knowledge_backup.json"

MAX_HISTORY: int = 15

# AUDIO
MIME_TYPE: str = "audio/pcm;rate=16000"
