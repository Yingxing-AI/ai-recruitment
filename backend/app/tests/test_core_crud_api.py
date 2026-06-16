import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.api.routes.applications import (
    create_application as create_application_route,
    update_stage,
)
from app.api.routes.candidates import (
    create_candidate as create_candidate_route,
    get_candidate,
    list_candidates,
    update_candidate,
)
from app.api.routes.interviews import create_interview
from app.api.routes.jobs import create_job as create_job_route
from app.api.routes.jobs import get_job, list_jobs, update_job
from app.db.base import Base
from app.models.application import ApplicationStageLog
from app.models.candidate import CandidateTag
from app.schemas.application import ApplicationCreate, ApplicationStageUpdate
from app.schemas.candidate import CandidateCreate, CandidateUpdate
from app.schemas.interview import InterviewCreate
from app.schemas.job import JobCreate, JobUpdate


@pytest.fixture()
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


def create_job(db: Session, title: str = "后端工程师"):
    return create_job_route(
        JobCreate(
            title=title,
            location="上海",
            headcount=2,
            jd_text="负责后端系统开发",
            requirements_text="熟悉 Python 和 FastAPI",
            status="open",
        ),
        db=db,
    )


def create_candidate(db: Session, name: str = "张三"):
    return create_candidate_route(
        CandidateCreate(
            name=name,
            email="zhangsan@example.com",
            phone="13800138000",
            current_company="示例科技",
            current_title="后端工程师",
            tags=["Python", "FastAPI"],
        ),
        db=db,
    )


def create_application(db: Session, job_id: int, candidate_id: int):
    return create_application_route(
        ApplicationCreate(job_id=job_id, candidate_id=candidate_id, source="manual"),
        db=db,
    )


def test_jobs_crud_and_status_filter(db_session: Session) -> None:
    job = create_job(db_session)

    assert get_job(job.id, db=db_session).title == "后端工程师"

    updated = update_job(job.id, JobUpdate(status="closed"), db=db_session)
    assert updated.status == "closed"

    closed_jobs = list_jobs(status="closed", db=db_session)
    assert [item.id for item in closed_jobs] == [job.id]

    with pytest.raises(HTTPException) as exc_info:
        get_job(999, db=db_session)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Job not found"


def test_candidates_crud_keyword_filter_and_tags(db_session: Session) -> None:
    candidate = create_candidate(db_session)

    assert get_candidate(candidate.id, db=db_session).email == "zhangsan@example.com"

    updated = update_candidate(
        candidate.id,
        CandidateUpdate(current_title="高级后端工程师"),
        db=db_session,
    )
    assert updated.current_title == "高级后端工程师"

    results = list_candidates(keyword="示例科技", db=db_session)
    assert [item.id for item in results] == [candidate.id]

    tags = db_session.scalars(
        select(CandidateTag).where(CandidateTag.candidate_id == candidate.id)
    ).all()
    assert [tag.tag for tag in tags] == ["Python", "FastAPI"]


def test_application_create_and_stage_update(db_session: Session) -> None:
    job = create_job(db_session)
    candidate = create_candidate(db_session)
    application = create_application(db_session, job.id, candidate.id)

    assert application.current_stage == "screening"
    assert application.source == "manual"

    updated = update_stage(
        application.id,
        ApplicationStageUpdate(to_stage="interview", reason="通过初筛"),
        db=db_session,
    )
    assert updated.current_stage == "interview"

    logs = db_session.scalars(select(ApplicationStageLog)).all()
    assert len(logs) == 1
    assert logs[0].from_stage == "screening"
    assert logs[0].to_stage == "interview"


def test_application_create_validates_references(db_session: Session) -> None:
    with pytest.raises(HTTPException) as exc_info:
        create_application_route(
            ApplicationCreate(job_id=999, candidate_id=999, source="manual"),
            db=db_session,
        )
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Job not found"


def test_interview_create_and_application_match_validation(db_session: Session) -> None:
    job = create_job(db_session)
    candidate = create_candidate(db_session)
    application = create_application(db_session, job.id, candidate.id)

    interview = create_interview(
        InterviewCreate(
            application_id=application.id,
            job_id=job.id,
            candidate_id=candidate.id,
            round=1,
            interview_type="onsite",
            location="上海会议室 A",
        ),
        db=db_session,
    )
    assert interview.status == "scheduled"
    assert interview.location == "上海会议室 A"

    other_job = create_job(db_session, title="前端工程师")
    with pytest.raises(HTTPException) as exc_info:
        create_interview(
            InterviewCreate(
                application_id=application.id,
                job_id=other_job.id,
                candidate_id=candidate.id,
            ),
            db=db_session,
        )
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Interview does not match application"
