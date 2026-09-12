import asyncio
import logging
from app.core.exceptions import AnalysisNotCancellableError, AnalysisNotFoundError
from app.schemas.analysis import TERMINAL_STATUSES, AnalysisSession, AnalysisStatus
from app.schemas.common import utc_now
from app.schemas.events import AnalysisEvent
from app.services.websocket_manager import WebSocketManager
logger = logging.getLogger(__name__)
class AnalysisManager:
    def __init__(self, websocket_manager: WebSocketManager, retention_seconds: float, max_concurrent: int) -> None:
        self.websocket_manager = websocket_manager
        self.retention_seconds = retention_seconds
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self._sessions: dict[str, AnalysisSession] = {}
        self._cancellations: dict[str, asyncio.Event] = {}
        self._tasks: dict[str, asyncio.Task[None]] = {}
        self._lock = asyncio.Lock()
    def _require(self, analysis_id: str) -> tuple[AnalysisSession, asyncio.Event]:
        session = self._sessions.get(analysis_id)
        event = self._cancellations.get(analysis_id)
        if session is None or event is None:
            raise AnalysisNotFoundError("Analysis ID was not found.")
        return session, event
    async def create(self, target_url: str) -> AnalysisSession:
        await self.cleanup()
        session = AnalysisSession(target_url=target_url)
        async with self._lock:
            self._sessions[session.analysis_id] = session
            self._cancellations[session.analysis_id] = asyncio.Event()
        await self.transition(
            session.analysis_id,
            AnalysisStatus.QUEUED,
            "Analysis queued for foundation orchestration.",
            "status_changed",
        )
        logger.info("Analysis created: %s", session.analysis_id)
        return session
    async def get(self, analysis_id: str) -> AnalysisSession:
        async with self._lock:
            session = self._sessions.get(analysis_id)
            if session is None:
                raise AnalysisNotFoundError("Analysis ID was not found.")
            return session.model_copy(deep=True)
    async def cancellation_event(self, analysis_id: str) -> asyncio.Event:
        async with self._lock:
            _, event = self._require(analysis_id)
            return event
    async def transition(
        self,
        analysis_id: str,
        status: AnalysisStatus,
        message: str,
        event_type: str = "status_changed",
        error: str | None = None,
    ) -> AnalysisSession:
        async with self._lock:
            session = self._sessions.get(analysis_id)
            if session is None:
                raise AnalysisNotFoundError("Analysis ID was not found.")
            if session.status in TERMINAL_STATUSES and session.status != status:
                return session.model_copy(deep=True)
            session.status = status
            session.message = message
            session.error = error
            if status == AnalysisStatus.RUNNING and session.started_at is None:
                session.started_at = utc_now()
            if status in TERMINAL_STATUSES and session.completed_at is None:
                session.completed_at = utc_now()
            copy = session.model_copy(deep=True)
        await self.websocket_manager.broadcast(
            AnalysisEvent(event_type=event_type, analysis_id=analysis_id, status=status, message=message)
        )
        logger.info("Analysis %s transitioned to %s", analysis_id, status)
        return copy
    async def request_cancellation(self, analysis_id: str) -> AnalysisSession:
        async with self._lock:
            session, event = self._require(analysis_id)
            if session.status in TERMINAL_STATUSES:
                raise AnalysisNotCancellableError("This analysis has already reached a terminal state.")
            session.cancellation_requested = True
            event.set()
        return await self.transition(
            analysis_id,
            AnalysisStatus.CANCELLED,
            "Analysis cancellation was requested.",
            "analysis_cancelled",
        )
    async def register_task(self, analysis_id: str, task: asyncio.Task[None]) -> None:
        async with self._lock:
            self._tasks[analysis_id] = task
    async def task_finished(self, analysis_id: str) -> None:
        async with self._lock:
            self._tasks.pop(analysis_id, None)
    async def cleanup(self) -> None:
        cutoff = utc_now().timestamp() - self.retention_seconds
        async with self._lock:
            expired = [
                aid
                for aid, session in self._sessions.items()
                if session.status in TERMINAL_STATUSES
                and session.completed_at
                and session.completed_at.timestamp() <= cutoff
                and aid not in self._tasks
            ]
            for aid in expired:
                self._sessions.pop(aid, None)
                self._cancellations.pop(aid, None)
    async def shutdown(self) -> None:
        async with self._lock:
            tasks = list(self._tasks.values())
            for event in self._cancellations.values():
                event.set()
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        await self.websocket_manager.close_all()
