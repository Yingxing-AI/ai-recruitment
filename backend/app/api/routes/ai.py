from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.ai_analysis import AIResumeAnalysis, JobMatchScore
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.resume import Resume
from app.schemas.ai import AIResumeAnalysisRead, JobMatchScoreRead, ParsedResumeRead
from app.services.ai_service import (
    build_candidate_summary,
    generate_interview_questions,
    score_job_match,
)
from app.services.resume_parser_service import parse_resume_text

router = APIRouter()


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
    result = build_candidate_summary(candidate, resume)
    analysis = get_or_create_analysis(db, resume)
    analysis.summary = result["summary"]
    analysis.skills_json = result["skills"]
    analysis.work_experience_summary = result["work_experience_summary"]
    analysis.project_experience_summary = result["project_experience_summary"]
    analysis.education_summary = result["education_summary"]
    analysis.strengths_json = result["strengths"]
    analysis.risks_json = result["risks"]
    analysis.raw_response = result
    analysis.model_provider = "rules"
    analysis.model_name = settings.llm_model
    analysis.status = "completed"
    analysis.error_message = None
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
    result = score_job_match(job, candidate, resume)

    match_score = db.scalar(
        select(JobMatchScore).where(
            JobMatchScore.job_id == job.id,
            JobMatchScore.candidate_id == candidate.id,
        )
    )
    if not match_score:
        match_score = JobMatchScore(job_id=job.id, candidate_id=candidate.id)
        db.add(match_score)

    match_score.total_score = result["total_score"]
    match_score.level = result["level"]
    match_score.dimension_scores_json = result["dimension_scores"]
    match_score.matched_points_json = result["matched_points"]
    match_score.missing_points_json = result["missing_points"]
    match_score.risk_points_json = result["risk_points"]
    match_score.recommendation = result["recommendation"]
    match_score.explanation = result["explanation"]
    match_score.raw_response = result
    match_score.model_provider = "rules"
    match_score.model_name = settings.llm_model
    match_score.status = "completed"
    match_score.error_message = None
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
    questions = generate_interview_questions(job, candidate, resume)
    analysis = get_or_create_analysis(db, resume)
    if not analysis.summary:
        result = build_candidate_summary(candidate, resume)
        analysis.summary = result["summary"]
        analysis.skills_json = result["skills"]
        analysis.strengths_json = result["strengths"]
        analysis.risks_json = result["risks"]
        analysis.raw_response = result
    analysis.interview_questions_json = questions
    analysis.model_provider = "rules"
    analysis.model_name = settings.llm_model
    analysis.status = "completed"
    analysis.error_message = None
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


def get_or_create_analysis(db: Session, resume: Resume) -> AIResumeAnalysis:
    analysis = db.scalar(select(AIResumeAnalysis).where(AIResumeAnalysis.resume_id == resume.id))
    if analysis:
        return analysis
    analysis = AIResumeAnalysis(
        candidate_id=resume.candidate_id,
        resume_id=resume.id,
        status="pending",
    )
    db.add(analysis)
    db.flush()
    return analysis
