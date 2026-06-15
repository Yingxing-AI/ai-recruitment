from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InterviewCreate(BaseModel):
    application_id: int
    job_id: int
    candidate_id: int
    round: int = 1
    interview_type: str = "video"
    scheduled_start_at: datetime | None = None
    scheduled_end_at: datetime | None = None
    location: str | None = None
    meeting_link: str | None = None
    interviewer_ids: list[int] = []


class InterviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    application_id: int
    job_id: int
    candidate_id: int
    round: int
    interview_type: str
    scheduled_start_at: datetime | None
    scheduled_end_at: datetime | None
    location: str | None
    meeting_link: str | None
    status: str
    created_at: datetime
    updated_at: datetime
