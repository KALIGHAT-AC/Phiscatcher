"""Background execution wrapper around the future investigation boundary."""

import asyncio
import logging

from app.investigation.orchestrator import InvestigationOrchestrator
from app.schemas.analysis import AnalysisStatus
from app.services.analysis_manager import AnalysisManager

logger = logging.getLogger(__name__)


class AnalysisRunner:
    def __init__(self, manager: AnalysisManager, orchestrator: InvestigationOrchestrator, timeout_seconds: float) -> None:
        self.manager = manager
        self.orchestrator = orchestrator
        self.timeout_seconds = timeout_seconds

    async def run(self, analysis_id: str) -> None:
        try:
            async with self.manager.semaphore:
                session = await self.manager.get(analysis_id)
                cancellation = await self.manager.cancellation_event(analysis_id)
                if cancellation.is_set():
                    return
                await self.manager.transition(analysis_id, AnalysisStatus.RUNNING, "Foundation orchestration started.", "analysis_started")
                try:
                    await asyncio.wait_for(self.orchestrator.run(session, cancellation), timeout=self.timeout_seconds)
                except TimeoutError:
                    await self.manager.transition(analysis_id, AnalysisStatus.TIMEOUT, "Analysis exceeded its configured timeout.", "analysis_failed", "Analysis timed out.")
                except asyncio.CancelledError:
                    raise
                except Exception:
                    logger.exception("Analysis %s failed", analysis_id)
                    await self.manager.transition(analysis_id, AnalysisStatus.FAILED, "Analysis lifecycle failed.", "analysis_failed", "Unexpected analysis lifecycle failure.")
                else:
                    current = await self.manager.get(analysis_id)
                    if cancellation.is_set() or current.status == AnalysisStatus.CANCELLED:
                        if current.status != AnalysisStatus.CANCELLED:
                            await self.manager.transition(analysis_id, AnalysisStatus.CANCELLED, "Analysis cancellation was requested.", "analysis_cancelled")
                    else:
                        await self.manager.transition(analysis_id, AnalysisStatus.COMPLETED, "Foundation orchestration completed; investigation components are not configured.", "analysis_completed")
                finally:
                    await self.orchestrator.cleanup(session)
        finally:
            await self.manager.task_finished(analysis_id)
