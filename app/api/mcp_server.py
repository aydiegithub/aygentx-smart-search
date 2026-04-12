import json
from mcp.server.fastmcp import FastMCP
from typing import List, Optional
from app.constants import (SCHEMA_PATH,
                           PREDEFINED_QUERIES,
                           TABLE_COLUMNS)

from app.db.connection import D1Connection

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

    # 1. Validate Table Exists
    if table_name not in TABLE_COLUMNS:
        return json.dumps({"error": f"Unauthorized or unknown table: {table_name}"})

    # Get the valid columns for THIS specific table
    valid_columns_for_table = TABLE_COLUMNS[table_name]

    # Validate requested columns belong to this table
    for col in columns:
        if col not in valid_columns_for_table:
            return json.dumps({
                "error": f"Column '{col}' does not exist in table '{table_name}'"
            })

    # Validate template exists
    if template_name not in PREDEFINED_QUERIES:
        return json.dumps({"error": f"Unknown template: {template_name}"})

    # Validate search column belongs to this table
    if search_column and search_column not in valid_columns_for_table:
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

    try:
        db = D1Connection()
        results = db.query(final_sql, params=params or [])
        return json.dumps({"status": "success", "data": results})
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
def search_vectorless_rag(search_query: str) -> str:
    """Searches the local knowledge base using keyword matching."""
    mock_results = [{"file": "policy.txt",
                     "snippet": f"Here is info about {search_query}..."}]
    return json.dumps({"status": "success", "data": mock_results})
