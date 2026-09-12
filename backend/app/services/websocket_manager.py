"""Analysis-specific WebSocket connection and event-history management."""

import asyncio
import logging
from collections import defaultdict, deque

from fastapi import WebSocket

from app.schemas.events import AnalysisEvent

logger = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self, history_limit: int) -> None:
        self._connections: dict[str, set[WebSocket]] = defaultdict(set)
        self._history: dict[str, deque[AnalysisEvent]] = defaultdict(lambda: deque(maxlen=history_limit))
        self._lock = asyncio.Lock()

    async def connect(self, analysis_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections[analysis_id].add(websocket)
            history = list(self._history[analysis_id])
        for event in history:
            await websocket.send_json(event.model_dump(mode="json"))
        logger.info("WebSocket connected for analysis %s", analysis_id)

    async def disconnect(self, analysis_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            clients = self._connections.get(analysis_id)
            if clients:
                clients.discard(websocket)
                if not clients:
                    self._connections.pop(analysis_id, None)
        logger.info("WebSocket disconnected for analysis %s", analysis_id)

    async def broadcast(self, event: AnalysisEvent) -> None:
        async with self._lock:
            self._history[event.analysis_id].append(event)
            clients = list(self._connections.get(event.analysis_id, set()))
        stale: list[WebSocket] = []
        for client in clients:
            try:
                await client.send_json(event.model_dump(mode="json"))
            except Exception:  # WebSocket errors are connection-local.
                stale.append(client)
        for client in stale:
            await self.disconnect(event.analysis_id, client)

    async def close_all(self) -> None:
        async with self._lock:
            clients = [client for group in self._connections.values() for client in group]
            self._connections.clear()
        for client in clients:
            try:
                await client.close()
            except Exception:
                pass
