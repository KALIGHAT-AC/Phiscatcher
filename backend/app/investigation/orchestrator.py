import asyncio
from abc import ABC, abstractmethod
from app.schemas.analysis import AnalysisSession
class InvestigationOrchestrator(ABC):
    @abstractmethod
    async def run(self, session: AnalysisSession, cancellation_event: asyncio.Event) -> None: ...
    async def cancel(self, session: AnalysisSession) -> None:
        pass
    async def cleanup(self, session: AnalysisSession) -> None:
        pass
class FoundationOrchestrator(InvestigationOrchestrator):
    async def run(self, session: AnalysisSession, cancellation_event: asyncio.Event) -> None:
        await asyncio.sleep(0)
        if cancellation_event.is_set():
            return
