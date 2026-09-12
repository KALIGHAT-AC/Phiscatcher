from fastapi import APIRouter
from app.api import analysis, health, websocket
api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(analysis.router)
api_router.include_router(websocket.router)
