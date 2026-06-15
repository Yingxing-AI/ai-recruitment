from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Interview(Base, TimestampMixin):
    __tablename__ = "interviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("job_applications.id"), index=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), index=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), index=True)
    round: Mapped[int] = mapped_column(Integer, default=1)
    interview_type: Mapped[str] = mapped_column(String(64), default="video")
    scheduled_start_at: Mapped[datetime | None] = mapped_column(DateTime)
    scheduled_end_at: Mapped[datetime | None] = mapped_column(DateTime)
    location: Mapped[str | None] = mapped_column(String(255))
    meeting_link: Mapped[str | None] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(32), default="scheduled", index=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    application = relationship("JobApplication", back_populates="interviews")
    interviewers = relationship("InterviewInterviewer", cascade="all, delete-orphan")
    feedbacks = relationship("InterviewFeedback", cascade="all, delete-orphan")


class InterviewInterviewer(Base):
    __tablename__ = "interview_interviewers"

    id: Mapped[int] = mapped_column(primary_key=True)
    interview_id: Mapped[int] = mapped_column(ForeignKey("interviews.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class InterviewFeedback(Base, TimestampMixin):
    __tablename__ = "interview_feedbacks"

    id: Mapped[int] = mapped_column(primary_key=True)
    interview_id: Mapped[int] = mapped_column(ForeignKey("interviews.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    rating: Mapped[int | None] = mapped_column(Integer)
    result: Mapped[str | None] = mapped_column(String(64))
    strengths: Mapped[str | None] = mapped_column(Text)
    weaknesses: Mapped[str | None] = mapped_column(Text)
    comments: Mapped[str | None] = mapped_column(Text)
    hire_recommendation: Mapped[str | None] = mapped_column(String(64))
