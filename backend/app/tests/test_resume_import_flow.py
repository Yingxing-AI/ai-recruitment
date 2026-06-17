import asyncio

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

import app.api.routes.resumes as resumes_route
from app.api.routes.resumes import ensure_application, resolve_resume_candidate
from app.db.base import Base
from app.models.ai_analysis import AIResumeAnalysis, JobMatchScore
from app.models.application import ApplicationStageLog, JobApplication
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.resume import Resume
from app.services.ai_service import upsert_candidate_analysis, upsert_job_match


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


def test_resolve_resume_candidate_creates_candidate_from_parsed_contacts() -> None:
    db = make_session()

    candidate = resolve_resume_candidate(
        db=db,
        candidate_id=None,
        parsed_json={
            "name": "张三",
            "phone": "13800138000",
            "email": "zhangsan@example.com",
            "current_title": "后端工程师",
            "years_of_experience": 5,
            "highest_education": "本科",
            "current_city": "上海",
        },
        fallback_name="resume",
    )

    assert candidate.id is not None
    assert candidate.name == "张三"
    assert candidate.email == "zhangsan@example.com"
    assert candidate.source == "resume_import"
    assert candidate.current_title == "后端工程师"
    assert candidate.years_of_experience == 5


def test_resolve_resume_candidate_reuses_existing_candidate_by_email() -> None:
    db = make_session()
    existing = Candidate(name="张三", email="zhangsan@example.com")
    db.add(existing)
    db.flush()

    candidate = resolve_resume_candidate(
        db=db,
        candidate_id=None,
        parsed_json={
            "name": "张三",
            "email": "zhangsan@example.com",
            "current_title": "后端工程师",
        },
        fallback_name="resume",
    )

    assert candidate.id == existing.id
    assert candidate.current_title == "后端工程师"


def test_ensure_application_creates_application_and_initial_stage_log() -> None:
    db = make_session()
    candidate = Candidate(name="张三")
    job = Job(title="后端工程师", jd_text="负责后端系统开发")
    db.add_all([candidate, job])
    db.flush()

    ensure_application(db=db, job_id=job.id, candidate_id=candidate.id)
    ensure_application(db=db, job_id=job.id, candidate_id=candidate.id)

    applications = db.scalars(select(JobApplication)).all()
    logs = db.scalars(select(ApplicationStageLog)).all()
    assert len(applications) == 1
    assert applications[0].source == "resume_import"
    assert len(logs) == 1
    assert logs[0].to_stage == "screening"


def test_upsert_ai_outputs_for_imported_resume_and_job_match() -> None:
    db = make_session()
    candidate = Candidate(name="张三", current_title="后端工程师", years_of_experience=5)
    job = Job(
        title="后端工程师",
        jd_text="负责 Python FastAPI Redis 后端系统开发",
        requirements_text="熟悉 Python、FastAPI、Redis",
    )
    db.add_all([candidate, job])
    db.flush()
    resume = Resume(
        candidate_id=candidate.id,
        file_name="resume.txt",
        file_path="resumes/resume.txt",
        raw_text="张三 13800138000 zhangsan@example.com Python FastAPI Redis 项目经历",
        parsed_json={
            "name": "张三",
            "phone": "13800138000",
            "email": "zhangsan@example.com",
            "skills": ["Python", "FastAPI", "Redis"],
            "projects": ["后端平台项目"],
            "work_experience": ["负责后端系统开发"],
            "education": ["本科"],
        },
        parse_status="parsed",
    )
    db.add(resume)
    db.flush()
    application = ensure_application(db=db, job_id=job.id, candidate_id=candidate.id)

    upsert_candidate_analysis(db, candidate, resume)
    upsert_job_match(db, job, candidate, resume, application_id=application.id)

    analysis = db.scalar(select(AIResumeAnalysis))
    match = db.scalar(select(JobMatchScore))
    assert analysis is not None
    assert analysis.status == "completed"
    assert analysis.summary is not None
    assert match is not None
    assert match.status == "completed"
    assert match.application_id == application.id
    assert match.total_score is not None


def test_upload_resume_rejects_empty_file_without_raw_text() -> None:
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
    assert exc_info.value.detail == "Resume file is empty"
    assert db.scalars(select(Resume)).all() == []


def test_upload_resume_records_parse_error_when_extraction_fails(monkeypatch) -> None:
    db = make_session()
    storage = FakeStorage()
    monkeypatch.setattr(resumes_route.settings, "storage_backend", "minio")

    def raise_parse_error(content: bytes, file_name: str, content_type: str | None = None) -> str:
        raise ValueError("unsupported resume format")

    monkeypatch.setattr(resumes_route, "extract_text_from_file", raise_parse_error)

    resume = asyncio.run(
        resumes_route.upload_resume(
            candidate_id=None,
            job_id=None,
            raw_text=None,
            file=FakeUploadFile(
                b"not a real pdf",
                filename="broken.pdf",
                content_type="application/pdf",
            ),
            db=db,
            storage=storage,
        )
    )

    assert resume.parse_status == "failed"
    assert resume.parse_error == "unsupported resume format"
    assert resume.raw_text is None
    assert resume.parsed_json is None
    assert resume.candidate.name == "broken"
    assert len(storage.uploads) == 1


def test_upload_resume_validates_candidate_reference_before_storage(monkeypatch) -> None:
    db = make_session()
    storage = FakeStorage()
    monkeypatch.setattr(resumes_route.settings, "storage_backend", "minio")

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            resumes_route.upload_resume(
                candidate_id=999,
                job_id=None,
                raw_text="张三 zhangsan@example.com Python",
                file=FakeUploadFile(b"resume content"),
                db=db,
                storage=storage,
            )
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Candidate not found"
    assert storage.uploads == []


def test_upload_resume_validates_job_reference(monkeypatch) -> None:
    db = make_session()
    storage = FakeStorage()
    monkeypatch.setattr(resumes_route.settings, "storage_backend", "minio")

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(
            resumes_route.upload_resume(
                candidate_id=None,
                job_id=999,
                raw_text="张三 zhangsan@example.com Python",
                file=FakeUploadFile(b"resume content"),
                db=db,
                storage=storage,
            )
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Job not found"
    assert db.scalars(select(JobApplication)).all() == []
