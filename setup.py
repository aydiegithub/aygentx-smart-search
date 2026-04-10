from setuptools import setup, find_packages

setup(
    name="app",
    version="0.1.0",
    description="AI-powered MCP server routing between SQL and Vectorless RAG using OpenRouter and Cloudflare D1",
    packages=find_packages(include=["app", "app.*"]),
    install_requires=[
        "fastapi",
        "uvicorn",
        "pydantic",
        "pydantic-settings",
        "python-dotenv",
        "httpx",
        "pyyaml",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pytest-asyncio",
            "black",
            "flake8",
            "isort",
        ],
    },
)
