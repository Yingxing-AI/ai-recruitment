from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    candidate_id: int
    file_name: str
    file_path: str
    file_type: str | None
    file_size: int | None
    raw_text: str | None
    parse_status: str
    parse_error: str | None
    created_at: datetime
    updated_at: datetime
