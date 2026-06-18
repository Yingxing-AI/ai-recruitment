from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.routes.applications import create_application as create_application_route
from app.api.routes.candidates import create_candidate as create_candidate_route
from app.api.routes.dashboard import get_dashboard_summary
from app.api.routes.jobs import create_job as create_job_route
from app.db.base import Base
from app.models.resume import Resume
from app.schemas.application import ApplicationCreate
from app.schemas.candidate import CandidateCreate
from app.schemas.job import JobCreate


def make_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)()


def test_dashboard_summary_counts_pipeline_and_core_entities() -> None:
    db = make_session()
    job = create_job_route(JobCreate(title="后端工程师", jd_text="负责后端系统开发", status="open"), db=db)
    other_job = create_job_route(JobCreate(title="前端工程师", jd_text="负责前端系统开发", status="open"), db=db)

    stages = ["screening", "first_interview", "second_interview", "final_interview", "offer", "hired"]
    for index, stage in enumerate(stages, start=1):
        candidate = create_candidate_route(
            CandidateCreate(name=f"候选人{index}", email=f"user{index}@example.com"),
            db=db,
        )
        application = create_application_route(
            ApplicationCreate(
                job_id=job.id if index <= 4 else other_job.id,
                candidate_id=candidate.id,
                source="manual",
            ),
            db=db,
        )
        application.current_stage = stage
        db.commit()
        db.add(
            Resume(
                candidate_id=candidate.id,
                file_name=f"resume-{index}.txt",
                file_path=f"resumes/{candidate.id}/resume-{index}.txt",
                raw_text=f"候选人{index}",
                parsed_json={"name": f"候选人{index}"},
                parse_status="parsed",
            )
        )

    summary = get_dashboard_summary(db=db)

    assert summary.job_count == 2
    assert summary.candidate_count == 6
    assert summary.resume_count == 6
    assert summary.interviewing_count == 3
    assert summary.offer_count == 1
    assert summary.hired_count == 1
    assert [item.stage for item in summary.funnel] == [
        "screening",
        "first_interview",
        "second_interview",
        "final_interview",
        "offer",
        "hired",
    ]
