from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict


class ParsedResumeRead(BaseModel):
    resume_id: int
    candidate_id: int
    parsed_json: dict[str, Any]
    raw_text: str | None
    parse_status: str


class AIResumeAnalysisRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    candidate_id: int
    resume_id: int
    summary: str | None
    skills_json: list[Any] | None
    work_experience_summary: str | None
    project_experience_summary: str | None
    education_summary: str | None
    strengths_json: list[Any] | None
    risks_json: list[Any] | None
    interview_questions_json: list[Any] | None
    raw_response: dict[str, Any] | None
    model_provider: str | None
    model_name: str | None
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class JobMatchScoreRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    job_id: int
    candidate_id: int
    application_id: int | None
    total_score: Decimal | None
    level: str | None
    dimension_scores_json: dict[str, Any] | None
    matched_points_json: list[Any] | None
    missing_points_json: list[Any] | None
    risk_points_json: list[Any] | None
    recommendation: str | None
    explanation: str | None
    raw_response: dict[str, Any] | None
    model_provider: str | None
    model_name: str | None
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime
