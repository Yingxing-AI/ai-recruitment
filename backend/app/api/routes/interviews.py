from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.application import JobApplication
from app.models.candidate import Candidate
from app.models.interview import Interview, InterviewInterviewer
from app.models.job import Job
from app.schemas.interview import InterviewCreate, InterviewRead

router = APIRouter()


@router.get("", response_model=list[InterviewRead])
def list_interviews(db: Session = Depends(get_db)) -> list[Interview]:
    return list(db.scalars(select(Interview).order_by(Interview.created_at.desc())).all())


@router.post("", response_model=InterviewRead)
def create_interview(payload: InterviewCreate, db: Session = Depends(get_db)) -> Interview:
    application = db.get(JobApplication, payload.application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if not db.get(Job, payload.job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    if not db.get(Candidate, payload.candidate_id):
        raise HTTPException(status_code=404, detail="Candidate not found")
    if application.job_id != payload.job_id or application.candidate_id != payload.candidate_id:
        raise HTTPException(status_code=400, detail="Interview does not match application")
    data = payload.model_dump(exclude={"interviewer_ids"})
    interview = Interview(**data)
    db.add(interview)
    db.flush()
    for user_id in payload.interviewer_ids:
        db.add(InterviewInterviewer(interview_id=interview.id, user_id=user_id))
    db.commit()
    db.refresh(interview)
    return interview
