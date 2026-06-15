from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class JobBase(BaseModel):
    title: str
    department_id: int | None = None
    location: str | None = None
    headcount: int = 1
    employment_type: str | None = None
    salary_min: Decimal | None = None
    salary_max: Decimal | None = None
    experience_min: int | None = None
    experience_max: int | None = None
    education_requirement: str | None = None
    jd_text: str
    requirements_text: str | None = None
    status: str = "draft"
    owner_user_id: int | None = None


class JobCreate(JobBase):
    pass


class JobUpdate(BaseModel):
    title: str | None = None
    location: str | None = None
    headcount: int | None = None
    jd_text: str | None = None
    requirements_text: str | None = None
    status: str | None = None


class JobRead(JobBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
