from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.ai_analysis import AIResumeAnalysis, JobMatchScore
from app.models.application import JobApplication
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.resume import Resume
from app.schemas.ai import (
    AIResumeAnalysisRead,
    AIWorkflowInterpretRead,
    AIWorkflowInterpretRequest,
    JobMatchScoreRead,
    ParsedResumeRead,
)
from app.services.audit_service import log_audit_event
from app.services.ai_service import (
    upsert_candidate_analysis,
    upsert_interview_questions,
    upsert_job_match,
)
from app.services.resume_parser_service import parse_resume_text
from app.services.workflow_service import interpret_workflow_instruction

router = APIRouter()


@router.post("/workflows/interpret", response_model=AIWorkflowInterpretRead)
def interpret_workflow(
    payload: AIWorkflowInterpretRequest,
    db: Session = Depends(get_db),
) -> AIWorkflowInterpretRead:
    result = interpret_workflow_instruction(
        payload.instruction,
        job_id=payload.job_id,
        candidate_id=payload.candidate_id,
        resume_id=payload.resume_id,
    )
    log_audit_event(
        db,
        action="workflow.interpret",
        target_type="workflow",
        detail=result,
    )
    db.commit()
    return AIWorkflowInterpretRead(**result)


@router.post("/resumes/{resume_id}/parse", response_model=ParsedResumeRead)
def parse_resume(resume_id: int, db: Session = Depends(get_db)) -> ParsedResumeRead:
    resume = get_resume(db, resume_id)
    if not resume.raw_text:
        raise HTTPException(status_code=400, detail="Resume text is empty; upload a PDF/DOCX or raw text first")

    parsed = parse_resume_text(resume.raw_text)
    resume.parsed_json = parsed
    resume.parse_status = "parsed"
    resume.parse_error = None

    candidate = db.get(Candidate, resume.candidate_id)
    if candidate:
        if parsed.get("name") and not candidate.name:
            candidate.name = parsed["name"]
        if parsed.get("phone") and not candidate.phone:
            candidate.phone = parsed["phone"]
        if parsed.get("email") and not candidate.email:
            candidate.email = parsed["email"]

    log_audit_event(
        db,
        action="resume.parse",
        target_type="resume",
        target_id=resume.id,
        detail={"resume_id": resume.id, "candidate_id": resume.candidate_id},
    )
    db.commit()
    db.refresh(resume)
    return ParsedResumeRead(
        resume_id=resume.id,
        candidate_id=resume.candidate_id,
        parsed_json=resume.parsed_json or {},
        raw_text=resume.raw_text,
        parse_status=resume.parse_status,
    )


@router.post("/resumes/{resume_id}/summary", response_model=AIResumeAnalysisRead)
def summarize_candidate(resume_id: int, db: Session = Depends(get_db)) -> AIResumeAnalysis:
    resume = ensure_parsed_resume(db, resume_id)
    candidate = get_candidate(db, resume.candidate_id)
    analysis = upsert_candidate_analysis(db, candidate, resume)
    log_audit_event(
        db,
        action="candidate.summary",
        target_type="resume",
        target_id=resume.id,
        detail={"resume_id": resume.id, "candidate_id": candidate.id},
    )
    db.commit()
    db.refresh(analysis)
    return analysis


@router.post(
    "/jobs/{job_id}/candidates/{candidate_id}/match",
    response_model=JobMatchScoreRead,
)
def match_candidate(job_id: int, candidate_id: int, db: Session = Depends(get_db)) -> JobMatchScore:
    job = get_job(db, job_id)
    candidate = get_candidate(db, candidate_id)
    resume = get_latest_parsed_resume(db, candidate.id)
    application = db.scalar(
        select(JobApplication).where(
            JobApplication.job_id == job.id,
            JobApplication.candidate_id == candidate.id,
        )
    )
    match_score = upsert_job_match(
        db,
        job,
        candidate,
        resume,
        application_id=application.id if application else None,
    )
    log_audit_event(
        db,
        action="job.match",
        target_type="job",
        target_id=job.id,
        detail={"job_id": job.id, "candidate_id": candidate.id, "application_id": application.id if application else None},
    )
    db.commit()
    db.refresh(match_score)
    return match_score


@router.post(
    "/jobs/{job_id}/candidates/{candidate_id}/interview-questions",
    response_model=AIResumeAnalysisRead,
)
def create_interview_questions(
    job_id: int,
    candidate_id: int,
    db: Session = Depends(get_db),
) -> AIResumeAnalysis:
    job = get_job(db, job_id)
    candidate = get_candidate(db, candidate_id)
    resume = get_latest_parsed_resume(db, candidate.id)
    analysis = upsert_interview_questions(db, job, candidate, resume)
    log_audit_event(
        db,
        action="interview.questions",
        target_type="candidate",
        target_id=candidate.id,
        detail={"job_id": job.id, "candidate_id": candidate.id},
    )
    db.commit()
    db.refresh(analysis)
    return analysis


@router.get("/analyses", response_model=list[AIResumeAnalysisRead])
def list_analyses(candidate_id: int | None = None, db: Session = Depends(get_db)) -> list[AIResumeAnalysis]:
    stmt = select(AIResumeAnalysis).order_by(AIResumeAnalysis.updated_at.desc())
    if candidate_id:
        stmt = stmt.where(AIResumeAnalysis.candidate_id == candidate_id)
    return list(db.scalars(stmt).all())


@router.get("/matches", response_model=list[JobMatchScoreRead])
def list_matches(
    job_id: int | None = None,
    candidate_id: int | None = None,
    db: Session = Depends(get_db),
) -> list[JobMatchScore]:
    stmt = select(JobMatchScore).order_by(JobMatchScore.updated_at.desc())
    if job_id:
        stmt = stmt.where(JobMatchScore.job_id == job_id)
    if candidate_id:
        stmt = stmt.where(JobMatchScore.candidate_id == candidate_id)
    return list(db.scalars(stmt).all())


def get_resume(db: Session, resume_id: int) -> Resume:
    resume = db.get(Resume, resume_id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume


def ensure_parsed_resume(db: Session, resume_id: int) -> Resume:
    resume = get_resume(db, resume_id)
    if not resume.parsed_json:
        if not resume.raw_text:
            raise HTTPException(status_code=400, detail="Resume text is empty")
        resume.parsed_json = parse_resume_text(resume.raw_text)
        resume.parse_status = "parsed"
        resume.parse_error = None
        db.flush()
    return resume


def get_latest_parsed_resume(db: Session, candidate_id: int) -> Resume:
    resume = db.scalar(
        select(Resume)
        .where(Resume.candidate_id == candidate_id)
        .order_by(Resume.updated_at.desc())
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Candidate has no resume")
    if not resume.parsed_json:
        if not resume.raw_text:
            raise HTTPException(status_code=400, detail="Candidate resume text is empty")
        resume.parsed_json = parse_resume_text(resume.raw_text)
        resume.parse_status = "parsed"
        resume.parse_error = None
        db.flush()
    return resume


def get_candidate(db: Session, candidate_id: int) -> Candidate:
    candidate = db.get(Candidate, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate


def get_job(db: Session, job_id: int) -> Job:
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
