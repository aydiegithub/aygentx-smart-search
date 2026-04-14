import json
from mcp.server.fastmcp import FastMCP
from typing import List, Optional
from app.constants import (SCHEMA_PATH,
                           PREDEFINED_QUERIES,
                           TABLE_COLUMNS)
from app.constants import (RAG_NODE_SELECTION_PROMPT,
                           GEMINI_PROVIDER,
                           GEMINI_MODEL)
from app.db.connection import D1Connection
from app.core.logging import Logger
from app.llm.factory import LLMFactory
from app.llm.base import ChatMessage

logging = Logger(__name__)

# Initializing the MCP Server
mcp = FastMCP("DataRouterAgent")

# Resource


@mcp.resource("schema://cloudflare_d1")
def d1_schema() -> str:
    """
    Exposes the dynamically loaded schema and exact table structure to the AI.
    """
    schema_info = {
        "tables": {table: list(columns) for table, columns in TABLE_COLUMNS.items()}
    }
    return json.dumps(schema_info, indent=2)


# Prompt
@mcp.prompt("data_routing_prompt")
def routing_prompt() -> str:
    return """You are a Data Router Agent. 
    If the user asks for database records, use the `query_cloudflare_d1` tool.
    If they provide a partial name or might have misspelled something, use the `search_like` template.
    Always review the `schema://cloudflare_d1` resource first to ensure you only select columns that actually exist in the requested table."""


# Tools
@mcp.tool()
def query_cloudflare_d1(
    template_name: str,
    table_name: str,
    columns: list,
    search_column: Optional[str] = None,
    params: Optional[list] = None  # <--- Change 'str' to 'list' here!
) -> str:
    """Queries the Cloudflare D1 database using strict templates."""
    logging.info(
        f"Entered query_cloudflare_d1 with template_name={template_name}, table_name={table_name}, columns={columns}, search_column={search_column}, params={params}")

    # 1. Validate Table Exists
    if table_name not in TABLE_COLUMNS:
        logging.error(f"Unauthorized or unknown table: {table_name}")
        return json.dumps({"error": f"Unauthorized or unknown table: {table_name}"})

    # Get the valid columns for THIS specific table
    valid_columns_for_table = TABLE_COLUMNS[table_name]

    # Validate requested columns belong to this table
    for col in columns:
        if col not in valid_columns_for_table:
            logging.error(
                f"Column '{col}' does not exist in table '{table_name}'")
            return json.dumps({
                "error": f"Column '{col}' does not exist in table '{table_name}'"
            })

    # Validate template exists
    if template_name not in PREDEFINED_QUERIES:
        logging.error(f"Unknown template: {template_name}")
        return json.dumps({"error": f"Unknown template: {template_name}"})

    # Validate search column belongs to this table
    if search_column and search_column not in valid_columns_for_table:
        logging.error(
            f"Search column '{search_column}' does not exist in table '{table_name}'")
        return json.dumps({"error": f"Search column '{search_column}' does not exist in table '{table_name}'"})

    # Construct Query
    safe_columns = ", ".join(columns)
    sql_template = PREDEFINED_QUERIES[template_name]

    # Format the template safely
    final_sql = sql_template.format(
        columns=safe_columns,
        table=table_name,
        search_column=search_column or "id"
    )
    logging.info(f"Executing formatted SQL: {final_sql}")

    try:
        db = D1Connection()
        results = db.query(final_sql, params=params or [])
        logging.info(
            f"Query execution successful, retrieved {len(results) if isinstance(results, list) else 0} results")
        return json.dumps({"status": "success", "data": results})
    except Exception as e:
        logging.error(f"Error querying D1 Database: {str(e)}", exc_info=True)
        return json.dumps({"error": str(e)})


@mcp.tool()
def search_vectorless_rag(query: str) -> str:
    """Searches the hierarchical RAG tree for the best matching knowledge chunk."""
    db = D1Connection()

    # Fetch the lightweight table of contents
    nodes = db.query("SELECT id, parent_id, title FROM rag_nodes", [])

    if not nodes:
        return json.dumps({
            "error": "The personal knowledge base is currently empty."
        })

    toc = json.dumps(nodes, indent=2)

    # Ask the LLM to pick the best node ID
    llm = LLMFactory.create(provider=GEMINI_PROVIDER,
                            model=GEMINI_MODEL)
    prompt = RAG_NODE_SELECTION_PROMPT.format(
        user_query=query,
        table_of_contents=toc
    )

    try:
        selection_result = llm.generate_json(
            [ChatMessage(role="user", content=prompt)])
        selection_id = selection_result.get("selected_node_id", "none")
    except Exception as e:
        logging.error(f"Error in RAG node selection: {e}")
        return json.dumps({"error": "Failed to determine the right knowledge node."})

    if selection_id == "none" or not selection_id:
        return json.dumps({"data": [{"info": "No relevant information found in the personal knowledge base."}]})

    data = db.query(
        "SELECT title, content FROM rag_nodes WHERE id = ?", [selection_id])

    # Fallback: If it picked a parent branch instead of a leaf, grab all its children's content
    if data and not data[0].get("content"):
        child_data = db.query(
            "SELECT title, content FROM rag_nodes WHERE parent_id = ? AND content IS NOT NULL", [selection_id])

        if child_data:
            data = child_data

    return json.dumps({"data": data})
