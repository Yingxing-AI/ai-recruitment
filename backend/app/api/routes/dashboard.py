from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.application import JobApplication
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.resume import Resume
from app.schemas.dashboard import DashboardFunnelItem, DashboardSummaryRead

router = APIRouter()

FUNNEL_STAGES: list[tuple[str, str]] = [
    ("screening", "初筛"),
    ("first_interview", "一面"),
    ("second_interview", "二面"),
    ("final_interview", "终面"),
    ("offer", "Offer"),
    ("hired", "录用"),
]


@router.get("/summary", response_model=DashboardSummaryRead)
def get_dashboard_summary(db: Session = Depends(get_db)) -> DashboardSummaryRead:
    stage_count_rows = db.execute(
        select(JobApplication.current_stage, func.count(JobApplication.id))
        .group_by(JobApplication.current_stage)
        .order_by(JobApplication.current_stage)
    ).all()
    stage_counts = {stage: count for stage, count in stage_count_rows}

    interviewing_count = db.scalar(
        select(func.count(func.distinct(JobApplication.candidate_id))).where(
            JobApplication.current_stage.in_(("first_interview", "second_interview", "final_interview"))
        )
    )
    offer_count = db.scalar(
        select(func.count(func.distinct(JobApplication.candidate_id))).where(
            JobApplication.current_stage == "offer"
        )
    )
    hired_count = db.scalar(
        select(func.count(func.distinct(JobApplication.candidate_id))).where(
            JobApplication.current_stage == "hired"
        )
    )

    return DashboardSummaryRead(
        job_count=db.scalar(select(func.count()).select_from(Job)) or 0,
        candidate_count=db.scalar(select(func.count()).select_from(Candidate)) or 0,
        resume_count=db.scalar(select(func.count()).select_from(Resume)) or 0,
        interviewing_count=interviewing_count or 0,
        offer_count=offer_count or 0,
        hired_count=hired_count or 0,
        funnel=[
            DashboardFunnelItem(stage=stage, label=label, count=stage_counts.get(stage, 0))
            for stage, label in FUNNEL_STAGES
        ],
    )
