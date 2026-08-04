from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.sessions import router as sessions_router
from app.api.routes.workspaces import router as workspaces_router
from app.websocket.routes import router as websocket_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Antigravity Desktop Bridge",
        version="0.1.0",
        description="POC bridge for remote control of an authorized desktop runtime.",
    )
    app.include_router(health_router)
    app.include_router(workspaces_router, prefix="/v1")
    app.include_router(sessions_router, prefix="/v1")
    app.include_router(websocket_router)
    return app


app = create_app()
