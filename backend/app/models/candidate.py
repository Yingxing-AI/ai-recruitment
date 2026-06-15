from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Candidate(Base, TimestampMixin):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), index=True)
    phone: Mapped[str | None] = mapped_column(String(32), index=True)
    email: Mapped[str | None] = mapped_column(String(255), index=True)
    gender: Mapped[str | None] = mapped_column(String(32))
    birth_year: Mapped[int | None] = mapped_column(Integer)
    current_company: Mapped[str | None] = mapped_column(String(255))
    current_title: Mapped[str | None] = mapped_column(String(255))
    years_of_experience: Mapped[int | None] = mapped_column(Integer)
    highest_education: Mapped[str | None] = mapped_column(String(128))
    current_city: Mapped[str | None] = mapped_column(String(128))
    expected_city: Mapped[str | None] = mapped_column(String(128))
    expected_salary_min: Mapped[float | None] = mapped_column(Numeric(12, 2))
    expected_salary_max: Mapped[float | None] = mapped_column(Numeric(12, 2))
    source: Mapped[str | None] = mapped_column(String(128), index=True)
    status: Mapped[str] = mapped_column(String(32), default="active", index=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    resumes = relationship("Resume", back_populates="candidate")
    tags = relationship("CandidateTag", back_populates="candidate", cascade="all, delete-orphan")
    notes = relationship("CandidateNote", back_populates="candidate", cascade="all, delete-orphan")
    applications = relationship("JobApplication", back_populates="candidate")


class CandidateTag(Base):
    __tablename__ = "candidate_tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), index=True)
    tag: Mapped[str] = mapped_column(String(64), index=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    candidate = relationship("Candidate", back_populates="tags")


class CandidateNote(Base, TimestampMixin):
    __tablename__ = "candidate_notes"

    id: Mapped[int] = mapped_column(primary_key=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), index=True)
    content: Mapped[str] = mapped_column(Text)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    candidate = relationship("Candidate", back_populates="notes")
