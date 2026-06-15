from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.application import ApplicationStageLog, JobApplication
from app.schemas.application import ApplicationCreate, ApplicationRead, ApplicationStageUpdate

router = APIRouter()


@router.get("", response_model=list[ApplicationRead])
def list_applications(db: Session = Depends(get_db)) -> list[JobApplication]:
    return list(db.scalars(select(JobApplication).order_by(JobApplication.created_at.desc())).all())


@router.post("", response_model=ApplicationRead)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db)) -> JobApplication:
    application = JobApplication(**payload.model_dump())
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.post("/{application_id}/stage", response_model=ApplicationRead)
def update_stage(
    application_id: int,
    payload: ApplicationStageUpdate,
    db: Session = Depends(get_db),
) -> JobApplication:
    application = db.get(JobApplication, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    previous_stage = application.current_stage
    application.current_stage = payload.to_stage
    db.add(
        ApplicationStageLog(
            application_id=application.id,
            from_stage=previous_stage,
            to_stage=payload.to_stage,
            reason=payload.reason,
            operator_id=payload.operator_id,
        )
    )
    db.commit()
    db.refresh(application)
    return application
