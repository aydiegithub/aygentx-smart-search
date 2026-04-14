from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as agent_router
from app.api.voice_endpoints import router as voice_router
from app.core.config import settings
from app.core.logging import Logger
from app.api.rag_endpoints import router as rag_router

logger = Logger(__name__)


def create_app() -> FastAPI:
    logger.info(f"Entered create_app")
    app = FastAPI(
        title=settings.project_name,
        description=settings.project_description,
        version=settings.project_version
    )

    allowed_origins = ["*"]
    if settings.development_env == "prod":
        allowed_origins = ["https://aydie.com", "https://www.aydie.com"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(agent_router, prefix="/api/v1")
    app.include_router(rag_router, prefix="/api/v1")
    app.include_router(voice_router, prefix="/api/v1")

    @app.get("/health")
    def health_check():
        logger.info(f"Entered health_check")
        return {"status": "healthy", "agent": "AygentX is awake!"}

    return app


app = create_app()
