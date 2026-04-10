import os
from pathlib import Path

directories = [
    "app/api",
    "app/agent",
    "app/retrievers/sql",
    "app/retrievers/rag",
    "app/llm",
    "app/prompts",
    "app/services",
    "app/models/pydantic",
    "app/models/domain",
    "app/db",
    "app/core",
    "app/utils",
    "tests/unit",
    "tests/integration",
    "data",
    "config"
]

files = [
    "app/api/dependencies.py",
    "app/api/endpoints.py",
    "app/api/server.py",
    "app/agent/router.py",
    "app/agent/state.py",
    "app/retrievers/sql/d1_executor.py",
    "app/retrievers/rag/keyword_search.py",
    "app/retrievers/rag/document_parser.py",
    "app/retrievers/base.py",
    "app/llm/openrouter.py",
    "app/llm/base.py",
    "app/llm/clients.py",
    "app/prompts/router_prompts.yaml",
    "app/prompts/response_prompts.yaml",
    "app/services/query_service.py",
    "app/db/connection.py",
    "app/core/config.py",
    "app/core/logging.py",
    "app/core/errors.py",
    "app/utils/helpers.py",
    "app/main.py",
    "tests/conftest.py",
    "config/settings.yaml",
    "pyproject.toml",
    "Dockerfile",
    "README.md",
    ".env.example"
]

def create_structure():
    base_path = Path(".")
    
    # Create directories and __init__.py files for Python packages
    for dir_path in directories:
        full_path = base_path / dir_path
        full_path.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py in app and tests directories
        if full_path.parts[0] in ("app", "tests"):
            init_file = full_path / "__init__.py"
            init_file.touch(exist_ok=True)
            
        # Ensure parent directories also have __init__.py
        parent = full_path.parent
        while parent != base_path and parent.parts[0] in ("app", "tests"):
            init_file = parent / "__init__.py"
            init_file.touch(exist_ok=True)
            parent = parent.parent

    # Create files
    for file_path in files:
        full_path = base_path / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.touch(exist_ok=True)

    print("Project structure created successfully!")

if __name__ == "__main__":
    create_structure()
