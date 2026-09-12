"""FastAPI application construction only; lifecycle work lives in services."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import Settings, get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.investigation.orchestrator import FoundationOrchestrator, InvestigationOrchestrator
from app.services.analysis_manager import AnalysisManager
from app.services.analysis_runner import AnalysisRunner
from app.services.websocket_manager import WebSocketManager


def create_app(settings: Settings | None = None, orchestrator: InvestigationOrchestrator | None = None) -> FastAPI:
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        configure_logging(settings.log_level)
        websocket_manager = WebSocketManager(settings.websocket_event_history_limit)
        manager = AnalysisManager(websocket_manager, settings.session_retention_seconds, settings.max_concurrent_analyses)
        app.state.settings = settings
        app.state.websocket_manager = websocket_manager
        app.state.analysis_manager = manager
        app.state.analysis_runner = AnalysisRunner(manager, orchestrator or FoundationOrchestrator(), settings.analysis_timeout_seconds)
        yield
        await manager.shutdown()

    app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    register_exception_handlers(app)
    app.include_router(api_router)
    return app


app = create_app()
