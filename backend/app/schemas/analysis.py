from datetime import datetime
from enum import StrEnum
from uuid import uuid4
from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field
from app.schemas.common import utc_now
class AnalysisStatus(StrEnum):
    CREATED = "created"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
TERMINAL_STATUSES = {
    AnalysisStatus.COMPLETED,
    AnalysisStatus.FAILED,
    AnalysisStatus.CANCELLED,
    AnalysisStatus.TIMEOUT,
}
class AnalysisRequest(BaseModel):
    target_url: AnyHttpUrl
class AnalysisSession(BaseModel):
    model_config = ConfigDict(use_enum_values=False)
    analysis_id: str = Field(default_factory=lambda: str(uuid4()))
    target_url: str
    created_at: datetime = Field(default_factory=utc_now)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    status: AnalysisStatus = AnalysisStatus.CREATED
    message: str = "Analysis session created."
    error: str | None = None
    cancellation_requested: bool = False
    timed_out: bool = False
    metadata: dict[str, str] = Field(default_factory=dict)
class AnalysisResponse(BaseModel):
    analysis_id: str
    target_url: str
    created_at: datetime
    status: AnalysisStatus
    message: str
class AnalysisStatusResponse(AnalysisResponse):
    started_at: datetime | None
    completed_at: datetime | None
    error: str | None
    cancellation_requested: bool
    timed_out: bool
class CancellationResponse(BaseModel):
    analysis_id: str
    status: AnalysisStatus
    message: str
