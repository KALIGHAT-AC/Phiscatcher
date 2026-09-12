"""Interface between lifecycle management and future investigation components."""

import asyncio
from abc import ABC, abstractmethod

from app.schemas.analysis import AnalysisSession


class InvestigationOrchestrator(ABC):
    """A future implementation may prepare, run, cancel, and clean up resources."""

    @abstractmethod
    async def run(self, session: AnalysisSession, cancellation_event: asyncio.Event) -> None:
        """Run an investigation without fabricating findings."""

    async def cancel(self, session: AnalysisSession) -> None:
        """Request safe stop of future browser/capture resources."""

    async def cleanup(self, session: AnalysisSession) -> None:
        """Release future resources for this session."""


class FoundationOrchestrator(InvestigationOrchestrator):
    """Deliberately empty implementation used until investigation is added."""

    async def run(self, session: AnalysisSession, cancellation_event: asyncio.Event) -> None:
        # Yield once so background scheduling and WebSocket subscription remain observable.
        await asyncio.sleep(0)
        if cancellation_event.is_set():
            return
