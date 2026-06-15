from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class AIResumeAnalysis(Base, TimestampMixin):
    __tablename__ = "ai_resume_analyses"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), index=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"), index=True)
    summary: Mapped[str | None] = mapped_column(Text)
    skills_json: Mapped[list | None] = mapped_column(JSON)
    work_experience_summary: Mapped[str | None] = mapped_column(Text)
    project_experience_summary: Mapped[str | None] = mapped_column(Text)
    education_summary: Mapped[str | None] = mapped_column(Text)
    strengths_json: Mapped[list | None] = mapped_column(JSON)
    risks_json: Mapped[list | None] = mapped_column(JSON)
    interview_questions_json: Mapped[list | None] = mapped_column(JSON)
    raw_response: Mapped[dict | None] = mapped_column(JSON)
    model_provider: Mapped[str | None] = mapped_column(String(64))
    model_name: Mapped[str | None] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    error_message: Mapped[str | None] = mapped_column(Text)


class JobMatchScore(Base, TimestampMixin):
    __tablename__ = "job_match_scores"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), index=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), index=True)
    application_id: Mapped[int | None] = mapped_column(ForeignKey("job_applications.id"), index=True)
    total_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    level: Mapped[str | None] = mapped_column(String(64))
    dimension_scores_json: Mapped[dict | None] = mapped_column(JSON)
    matched_points_json: Mapped[list | None] = mapped_column(JSON)
    missing_points_json: Mapped[list | None] = mapped_column(JSON)
    risk_points_json: Mapped[list | None] = mapped_column(JSON)
    recommendation: Mapped[str | None] = mapped_column(Text)
    explanation: Mapped[str | None] = mapped_column(Text)
    raw_response: Mapped[dict | None] = mapped_column(JSON)
    model_provider: Mapped[str | None] = mapped_column(String(64))
    model_name: Mapped[str | None] = mapped_column(String(128))
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    error_message: Mapped[str | None] = mapped_column(Text)


class AITask(Base, TimestampMixin):
    __tablename__ = "ai_tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_type: Mapped[str] = mapped_column(String(64), index=True)
    target_type: Mapped[str] = mapped_column(String(64), index=True)
    target_id: Mapped[int] = mapped_column(Integer, index=True)
    status: Mapped[str] = mapped_column(String(32), default="pending", index=True)
    input_json: Mapped[dict | None] = mapped_column(JSON)
    output_json: Mapped[dict | None] = mapped_column(JSON)
    error_message: Mapped[str | None] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    started_at: Mapped[datetime | None] = mapped_column(DateTime)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)
