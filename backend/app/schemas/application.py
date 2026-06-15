from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ApplicationCreate(BaseModel):
    job_id: int
    candidate_id: int
    source: str | None = None
    owner_user_id: int | None = None


class ApplicationStageUpdate(BaseModel):
    to_stage: str
    reason: str | None = None
    operator_id: int | None = None


class ApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    candidate_id: int
    current_stage: str
    status: str
    source: str | None
    owner_user_id: int | None
    applied_at: datetime
    created_at: datetime
    updated_at: datetime
