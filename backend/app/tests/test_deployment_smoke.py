from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.api.routes.applications import create_application as create_application_route
from app.api.routes.candidates import create_candidate as create_candidate_route
from app.api.routes.interviews import create_interview
from app.api.routes.jobs import create_job as create_job_route
from app.db.base import Base
from app.models.audit_log import AuditLog
from app.schemas.application import ApplicationCreate
from app.schemas.candidate import CandidateCreate
from app.schemas.interview import InterviewCreate
from app.schemas.job import JobCreate
from app.services.workflow_service import interpret_workflow_instruction


def make_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_smoke_flow_covers_core_recruitment_paths() -> None:
    db = make_session()
    job = create_job_route(JobCreate(title="后端工程师", jd_text="负责后端系统开发", status="open"), db=db)
    candidate = create_candidate_route(CandidateCreate(name="张三", email="zhangsan@example.com"), db=db)
    application = create_application_route(
        ApplicationCreate(job_id=job.id, candidate_id=candidate.id, source="manual"),
        db=db,
    )
    interview = create_interview(
        InterviewCreate(application_id=application.id, job_id=job.id, candidate_id=candidate.id),
        db=db,
    )

    workflow = interpret_workflow_instruction("帮我为候选人做岗位匹配", job_id=job.id, candidate_id=candidate.id)
    logs = db.scalars(select(AuditLog)).all()

    assert job.id and candidate.id and application.id and interview.id
    assert workflow["can_execute"] is True
    assert len(logs) >= 4
