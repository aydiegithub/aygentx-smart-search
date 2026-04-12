from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as agent_router
from app.constants import TITLE, DESCRIPTION, VERSION, APP_ENV


def create_app() -> FastAPI:
    app = FastAPI(
        title=TITLE,
        description=DESCRIPTION,
        version=VERSION
    )

    allowed_origins = ["*"]
    if APP_ENV == "prod":
        allowed_origins = ["https://aydie.com", ["https://www.aydie.com"]]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(agent_router, prefix="/api/v1")

    @app.get("/health")
    def health_check():
        return {"status": "healthy", "agent": "AygentX is awake!"}

    return app


app = create_app()
