from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

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
