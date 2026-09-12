"""WebSocket lifecycle event schema."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.analysis import AnalysisStatus
from app.schemas.common import utc_now


class AnalysisEvent(BaseModel):
    event_type: str
    analysis_id: str
    timestamp: datetime = Field(default_factory=utc_now)
    status: AnalysisStatus | None = None
    message: str
    payload: dict[str, str] | None = None
