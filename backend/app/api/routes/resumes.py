import os
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.application import ApplicationStageLog, JobApplication
from app.models.candidate import Candidate
from app.models.file import StoredFile
from app.models.job import Job
from app.models.resume import Resume
from app.schemas.resume import ResumeRead
from app.services.ai_service import upsert_candidate_analysis, upsert_job_match
from app.services.resume_parser_service import extract_text_from_file, parse_resume_text
from app.services.storage_service import ObjectStorageService, get_storage_service

router = APIRouter()


@router.get("", response_model=list[ResumeRead])
def list_resumes(db: Session = Depends(get_db)) -> list[Resume]:
    return list(db.scalars(select(Resume).order_by(Resume.created_at.desc())).all())


@router.post("/upload", response_model=ResumeRead)
async def upload_resume(
    candidate_id: int | None = Form(default=None),
    job_id: int | None = Form(default=None),
    raw_text: str | None = Form(default=None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    storage: ObjectStorageService = Depends(get_storage_service),
) -> Resume:
    suffix = Path(file.filename or "").suffix
    content = await file.read()
    if not content and not (raw_text and raw_text.strip()):
        raise HTTPException(status_code=400, detail="Resume file is empty")

    parse_error = None
    extracted_text = raw_text.strip() if raw_text and raw_text.strip() else None
    if extracted_text is None:
        try:
            extracted_text = extract_text_from_file(
                content,
                file.filename or f"resume{suffix}",
                file.content_type,
            )
        except Exception as exc:
            extracted_text = None
            parse_error = str(exc) or exc.__class__.__name__

    parsed_json = None
    if extracted_text:
        try:
            parsed_json = parse_resume_text(extracted_text)
        except Exception as exc:
            parse_error = str(exc) or exc.__class__.__name__

    parse_status = "parsed" if parsed_json else "failed" if parse_error else "pending"
    candidate = resolve_resume_candidate(
        db=db,
        candidate_id=candidate_id,
        parsed_json=parsed_json,
        fallback_name=Path(file.filename or "未命名候选人").stem,
    )

    stored_name = f"{uuid4().hex}{suffix}"
    object_key = f"resumes/{candidate.id}/{stored_name}"

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
        candidate_id=candidate.id,
        file_name=file.filename or stored_name,
        file_path=file_path,
        file_type=file.content_type,
        file_size=len(content),
        raw_text=extracted_text,
        parsed_json=parsed_json,
        parse_status=parse_status,
        parse_error=parse_error,
    )
    db.add(resume)
    db.flush()

    if job_id is not None:
        application = ensure_application(db=db, job_id=job_id, candidate_id=candidate.id)
    else:
        application = None

    if parsed_json:
        upsert_candidate_analysis(db, candidate, resume)
        if job_id is not None:
            job = db.get(Job, job_id)
            if job:
                upsert_job_match(
                    db,
                    job,
                    candidate,
                    resume,
                    application_id=application.id if application else None,
                )

    db.commit()
    db.refresh(resume)
    return resume


def resolve_resume_candidate(
    db: Session,
    candidate_id: int | None,
    parsed_json: dict | None,
    fallback_name: str,
) -> Candidate:
    if candidate_id is not None:
        candidate = db.get(Candidate, candidate_id)
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        update_candidate_from_resume(candidate, parsed_json)
        return candidate

    candidate = find_candidate_by_contacts(db, parsed_json)
    if candidate:
        update_candidate_from_resume(candidate, parsed_json)
        return candidate

    name = get_parsed_value(parsed_json, "name") or fallback_name or "未命名候选人"
    candidate = Candidate(
        name=name[:128],
        phone=get_parsed_value(parsed_json, "phone"),
        email=get_parsed_value(parsed_json, "email"),
        current_title=get_parsed_value(parsed_json, "current_title"),
        years_of_experience=get_parsed_int(parsed_json, "years_of_experience"),
        highest_education=get_parsed_value(parsed_json, "highest_education"),
        current_city=get_parsed_value(parsed_json, "current_city"),
        source="resume_import",
    )
    db.add(candidate)
    db.flush()
    return candidate


def find_candidate_by_contacts(db: Session, parsed_json: dict | None) -> Candidate | None:
    email = get_parsed_value(parsed_json, "email")
    phone = get_parsed_value(parsed_json, "phone")
    if email:
        candidate = db.scalar(select(Candidate).where(Candidate.email == email))
        if candidate:
            return candidate
    if phone:
        return db.scalar(select(Candidate).where(Candidate.phone == phone))
    return None


def update_candidate_from_resume(candidate: Candidate, parsed_json: dict | None) -> None:
    for field in ["phone", "email", "current_title", "highest_education", "current_city"]:
        value = get_parsed_value(parsed_json, field)
        if value and not getattr(candidate, field):
            setattr(candidate, field, value)
    years_of_experience = get_parsed_int(parsed_json, "years_of_experience")
    if years_of_experience is not None and candidate.years_of_experience is None:
        candidate.years_of_experience = years_of_experience


def ensure_application(db: Session, job_id: int, candidate_id: int) -> JobApplication:
    if not db.get(Job, job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    existing = db.scalar(
        select(JobApplication).where(
            JobApplication.job_id == job_id,
            JobApplication.candidate_id == candidate_id,
        )
    )
    if existing:
        return existing
    application = JobApplication(job_id=job_id, candidate_id=candidate_id, source="resume_import")
    db.add(application)
    db.flush()
    db.add(
        ApplicationStageLog(
            application_id=application.id,
            from_stage=None,
            to_stage=application.current_stage,
            reason="简历导入自动创建",
        )
    )
    return application


def get_parsed_value(parsed_json: dict | None, key: str) -> str | None:
    if not parsed_json:
        return None
    value = parsed_json.get(key)
    return value.strip() if isinstance(value, str) and value.strip() else None


def get_parsed_int(parsed_json: dict | None, key: str) -> int | None:
    if not parsed_json:
        return None
    value = parsed_json.get(key)
    return value if isinstance(value, int) else None


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
