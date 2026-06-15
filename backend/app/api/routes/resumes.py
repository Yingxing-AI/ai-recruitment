import os
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.candidate import Candidate
from app.models.file import StoredFile
from app.models.resume import Resume
from app.schemas.resume import ResumeRead
from app.services.resume_parser_service import extract_text_from_file, parse_resume_text
from app.services.storage_service import ObjectStorageService, get_storage_service

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
    storage: ObjectStorageService = Depends(get_storage_service),
) -> Resume:
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")

    suffix = Path(file.filename or "").suffix
    content = await file.read()
    stored_name = f"{uuid4().hex}{suffix}"
    object_key = f"resumes/{candidate_id}/{stored_name}"
    extracted_text = raw_text or extract_text_from_file(
        content,
        file.filename or stored_name,
        file.content_type,
    )
    parsed_json = parse_resume_text(extracted_text) if extracted_text else None

    if settings.storage_backend == "minio":
        storage.upload_bytes(
            object_key=object_key,
            content=content,
            content_type=file.content_type,
        )
        file_path = object_key
        storage_type = "minio"
    else:
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        local_path = upload_dir / stored_name
        local_path.write_bytes(content)
        file_path = os.fspath(local_path)
        storage_type = "local"

    db.add(
        StoredFile(
            file_name=file.filename or stored_name,
            file_path=file_path,
            file_type=file.content_type,
            file_size=len(content),
            storage_type=storage_type,
        )
    )

    resume = Resume(
        candidate_id=candidate_id,
        file_name=file.filename or stored_name,
        file_path=file_path,
        file_type=file.content_type,
        file_size=len(content),
        raw_text=extracted_text,
        parsed_json=parsed_json,
        parse_status="parsed" if extracted_text else "pending",
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.get("/{resume_id}/download-url")
def get_resume_download_url(
    resume_id: int,
    db: Session = Depends(get_db),
    storage: ObjectStorageService = Depends(get_storage_service),
) -> dict[str, str]:
    resume = db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if settings.storage_backend != "minio":
        raise HTTPException(status_code=400, detail="Presigned URL is only available for MinIO")
    return {"url": storage.create_presigned_url(resume.file_path)}
