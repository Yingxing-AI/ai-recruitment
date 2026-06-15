from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class CandidateBase(BaseModel):
    name: str
    phone: str | None = None
    email: str | None = None
    gender: str | None = None
    birth_year: int | None = None
    current_company: str | None = None
    current_title: str | None = None
    years_of_experience: int | None = None
    highest_education: str | None = None
    current_city: str | None = None
    expected_city: str | None = None
    expected_salary_min: Decimal | None = None
    expected_salary_max: Decimal | None = None
    source: str | None = None
    status: str = "active"


class CandidateCreate(CandidateBase):
    tags: list[str] = []


class CandidateUpdate(BaseModel):
    name: str | None = None
    phone: str | None = None
    email: str | None = None
    current_company: str | None = None
    current_title: str | None = None
    years_of_experience: int | None = None
    status: str | None = None


class CandidateRead(CandidateBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
