import os
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.candidate import Candidate
from app.models.resume import Resume
from app.schemas.resume import ResumeRead

router = APIRouter()


@router.get("", response_model=list[ResumeRead])
def list_resumes(db: Session = Depends(get_db)) -> list[Resume]:
    return list(db.scalars(select(Resume).order_by(Resume.created_at.desc())).all())


@router.post("/upload", response_model=ResumeRead)
async def upload_resume(
    candidate_id: int = Form(...),
    raw_text: str | None = Form(default=None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Resume:
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "").suffix
    stored_name = f"{uuid4().hex}{suffix}"
    file_path = upload_dir / stored_name
    content = await file.read()
    file_path.write_bytes(content)

    resume = Resume(
        candidate_id=candidate_id,
        file_name=file.filename or stored_name,
        file_path=os.fspath(file_path),
        file_type=file.content_type,
        file_size=len(content),
        raw_text=raw_text,
        parse_status="parsed" if raw_text else "pending",
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume
