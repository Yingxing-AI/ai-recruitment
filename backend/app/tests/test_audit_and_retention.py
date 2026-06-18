from datetime import datetime, timedelta

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.api.routes.applications import create_application as create_application_route
from app.api.routes.candidates import create_candidate as create_candidate_route
from app.api.routes.interviews import create_interview
from app.api.routes.jobs import create_job as create_job_route
from app.db.base import Base
from app.models.ai_analysis import AIResumeAnalysis, JobMatchScore
from app.models.audit_log import AuditLog
from app.schemas.application import ApplicationCreate
from app.schemas.candidate import CandidateCreate
from app.schemas.interview import InterviewCreate
from app.schemas.job import JobCreate
from app.services.retention_service import apply_data_retention


def make_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_business_flow_writes_audit_logs() -> None:
    db = make_session()
    job = create_job_route(
        JobCreate(title="后端工程师", jd_text="负责后端系统开发", status="open"),
        db=db,
    )
    candidate = create_candidate_route(
        CandidateCreate(name="张三", email="zhangsan@example.com", tags=["Python"]),
        db=db,
    )
    application = create_application_route(
        ApplicationCreate(job_id=job.id, candidate_id=candidate.id, source="manual"),
        db=db,
    )
    create_interview(
        InterviewCreate(application_id=application.id, job_id=job.id, candidate_id=candidate.id),
        db=db,
    )

    logs = db.scalars(select(AuditLog).order_by(AuditLog.created_at.asc())).all()
    assert [log.action for log in logs] == [
        "job.create",
        "candidate.create",
        "application.create",
        "interview.create",
    ]


def test_retention_redacts_ai_artifacts_and_deletes_audit_logs() -> None:
    db = make_session()
    old_timestamp = datetime.utcnow() - timedelta(days=365)
    analysis = AIResumeAnalysis(
        candidate_id=1,
        resume_id=1,
        summary="summary",
        raw_response={"sensitive": True},
        status="completed",
    )
    match = JobMatchScore(
        job_id=1,
        candidate_id=1,
        total_score=88,
        raw_response={"sensitive": True},
        status="completed",
    )
    log = AuditLog(action="job.create", target_type="job", target_id=1, detail_json={"title": "后端工程师"})
    db.add_all([analysis, match, log])
    db.flush()
    analysis.created_at = old_timestamp
    analysis.updated_at = old_timestamp
    match.created_at = old_timestamp
    match.updated_at = old_timestamp
    log.created_at = old_timestamp
    log.updated_at = old_timestamp
    db.commit()

    result = apply_data_retention(db, audit_log_days=180, ai_artifact_days=90, dry_run=False)

    assert result["audit_logs_expired"] == 1
    assert result["ai_analyses_redacted"] == 1
    assert result["job_matches_redacted"] == 1
    assert db.scalars(select(AuditLog)).all() == []
    remaining_analysis = db.scalar(select(AIResumeAnalysis))
    remaining_match = db.scalar(select(JobMatchScore))
    assert remaining_analysis is not None and remaining_analysis.raw_response is None
    assert remaining_match is not None and remaining_match.raw_response is None
