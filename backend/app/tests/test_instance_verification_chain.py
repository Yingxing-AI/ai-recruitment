import asyncio

from fastapi import HTTPException
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
import pytest

import app.api.routes.resumes as resumes_route
from app.api.routes.ai import (
    create_interview_questions,
    match_candidate,
    parse_resume,
    summarize_candidate,
)
from app.api.routes.applications import update_stage
from app.api.routes.candidates import create_candidate as create_candidate_route
from app.api.routes.dashboard import get_dashboard_summary
from app.api.routes.interviews import create_interview
from app.api.routes.jobs import create_job as create_job_route
from app.db.base import Base
from app.models.application import JobApplication
from app.models.audit_log import AuditLog
from app.models.interview import Interview
from app.schemas.application import ApplicationStageUpdate
from app.schemas.candidate import CandidateCreate
from app.schemas.interview import InterviewCreate
from app.schemas.job import JobCreate


def make_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


class FakeUploadFile:
    def __init__(
        self,
        content: bytes,
        filename: str = "resume.txt",
        content_type: str = "text/plain",
    ) -> None:
        self._content = content
        self.filename = filename
        self.content_type = content_type

    async def read(self) -> bytes:
        return self._content


class FakeStorage:
    def __init__(self) -> None:
        self.uploads: list[dict] = []

    def upload_bytes(self, **kwargs) -> None:
        self.uploads.append(kwargs)


def test_instance_verification_chain_runs_through_recruitment_flow(monkeypatch) -> None:
    db = make_session()
    storage = FakeStorage()
    monkeypatch.setattr(resumes_route.settings, "storage_backend", "minio")

    job = create_job_route(
        JobCreate(
            title="后端工程师",
            jd_text="负责后端系统开发",
            requirements_text="Python FastAPI",
            status="open",
        ),
        db=db,
    )
    candidate = create_candidate_route(
        CandidateCreate(name="张三", email="zhangsan@example.com", phone="13800138000"),
        db=db,
    )

    resume = asyncio.run(
        resumes_route.upload_resume(
            candidate_id=candidate.id,
            job_id=job.id,
            raw_text="张三 13800138000 zhangsan@example.com Python FastAPI PostgreSQL 项目经历",
            file=FakeUploadFile(b"resume content", filename="zhangsan.txt"),
            db=db,
            storage=storage,
        )
    )

    parsed = parse_resume(resume.id, db=db)
    analysis = summarize_candidate(resume.id, db=db)
    match = match_candidate(job.id, candidate.id, db=db)
    questions = create_interview_questions(job.id, candidate.id, db=db)

    application = db.scalar(
        select(JobApplication).where(
            JobApplication.job_id == job.id,
            JobApplication.candidate_id == candidate.id,
        )
    )
    assert application is not None

    updated_application = update_stage(
        application.id,
        ApplicationStageUpdate(to_stage="first_interview", reason="通过初筛"),
        db=db,
    )

    interview = create_interview(
        InterviewCreate(
            application_id=application.id,
            job_id=job.id,
            candidate_id=candidate.id,
            round=1,
            interview_type="video",
        ),
        db=db,
    )
    summary = get_dashboard_summary(db=db)
    logs = db.scalars(select(AuditLog)).all()

    assert resume.parse_status == "parsed"
    assert parsed.parse_status == "parsed"
    assert analysis.summary
    assert match.total_score is not None
    assert len(questions.interview_questions_json or []) >= 3
    assert updated_application.current_stage == "first_interview"
    assert interview.status == "scheduled"
    assert summary.job_count == 1
    assert summary.candidate_count == 1
    assert summary.resume_count == 1
    assert summary.interviewing_count == 1
    assert summary.funnel[0].count == 0
    assert len(storage.uploads) == 1
    assert db.scalar(select(Interview)) is not None
    assert len(logs) >= 4


def test_instance_verification_chain_rejects_empty_resume_without_raw_text() -> None:
    db = make_session()

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            resumes_route.upload_resume(
                candidate_id=None,
                job_id=None,
                raw_text=None,
                file=FakeUploadFile(b"", filename="empty.txt"),
                db=db,
                storage=FakeStorage(),
            )
        )

    assert exc_info.value.status_code == 400
