from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None
    action: str
    target_type: str | None
    target_id: int | None
    detail_json: dict[str, Any] | None
    ip_address: str | None
    user_agent: str | None
    created_at: datetime
    updated_at: datetime
