from datetime import datetime

from sqlalchemy import select

import app.db.base  # noqa: F401
from app.db.base import Base
from app.db.session import SessionLocal
from app.db.session import engine
from app.models.ai_analysis import AIResumeAnalysis, JobMatchScore
from app.models.application import ApplicationStageLog, JobApplication
from app.models.candidate import Candidate, CandidateTag
from app.models.file import StoredFile
from app.models.job import Job
from app.models.resume import Resume
from app.services.ai_service import build_candidate_summary, generate_interview_questions, score_job_match
from app.services.resume_parser_service import parse_resume_text
from app.services.storage_service import get_storage_service


JOBS = [
    {
        "title": "高级后端工程师",
        "location": "上海",
        "headcount": 2,
        "employment_type": "full_time",
        "jd_text": "负责招聘系统后端服务、数据模型和 API 设计。",
        "requirements_text": "熟悉 Python、FastAPI、PostgreSQL，有企业系统开发经验。",
        "status": "open",
    },
    {
        "title": "前端工程师",
        "location": "杭州",
        "headcount": 1,
        "employment_type": "full_time",
        "jd_text": "负责招聘管理工作台的前端体验和业务页面开发。",
        "requirements_text": "熟悉 React、TypeScript、Ant Design，重视交互细节。",
        "status": "open",
    },
    {
        "title": "招聘运营专员",
        "location": "北京",
        "headcount": 1,
        "employment_type": "full_time",
        "jd_text": "负责职位发布、候选人跟进、面试协调和招聘数据维护。",
        "requirements_text": "熟悉招聘流程，有良好的沟通和推进能力。",
        "status": "draft",
    },
]

CANDIDATES = [
    {
        "name": "张晨",
        "phone": "13800000001",
        "email": "zhangchen@example.com",
        "current_company": "云杉科技",
        "current_title": "后端工程师",
        "years_of_experience": 6,
        "current_city": "上海",
        "source": "referral",
        "status": "active",
        "tags": ["Python", "FastAPI"],
    },
    {
        "name": "李悦",
        "phone": "13800000002",
        "email": "liyue@example.com",
        "current_company": "星河互动",
        "current_title": "前端工程师",
        "years_of_experience": 4,
        "current_city": "杭州",
        "source": "job_board",
        "status": "active",
        "tags": ["React", "TypeScript"],
    },
    {
        "name": "王昊",
        "phone": "13800000003",
        "email": "wanghao@example.com",
        "current_company": "北辰咨询",
        "current_title": "招聘专员",
        "years_of_experience": 3,
        "current_city": "北京",
        "source": "headhunter",
        "status": "active",
        "tags": ["招聘运营"],
    },
    {
        "name": "赵琳",
        "phone": "13800000004",
        "email": "zhaolin@example.com",
        "current_company": "青木数据",
        "current_title": "高级后端工程师",
        "years_of_experience": 8,
        "current_city": "深圳",
        "source": "inbound",
        "status": "active",
        "tags": ["PostgreSQL", "架构"],
    },
]

APPLICATIONS = [
    ("高级后端工程师", "张晨", "screening", "referral"),
    ("前端工程师", "李悦", "first_interview", "job_board"),
    ("招聘运营专员", "王昊", "contacting", "headhunter"),
    ("高级后端工程师", "赵琳", "offer", "inbound"),
]


def get_or_create_job(db, payload: dict) -> Job:
    job = db.scalar(select(Job).where(Job.title == payload["title"]))
    if job:
        return job
    job = Job(**payload)
    db.add(job)
    db.flush()
    return job


def get_or_create_candidate(db, payload: dict) -> Candidate:
    tags = payload.pop("tags")
    candidate = db.scalar(select(Candidate).where(Candidate.email == payload["email"]))
    if candidate:
        return candidate
    candidate = Candidate(**payload)
    db.add(candidate)
    db.flush()
    for tag in tags:
        db.add(CandidateTag(candidate_id=candidate.id, tag=tag))
    return candidate


def get_or_create_application(
    db,
    *,
    job: Job,
    candidate: Candidate,
    stage: str,
    source: str,
) -> JobApplication:
    application = db.scalar(
        select(JobApplication).where(
            JobApplication.job_id == job.id,
            JobApplication.candidate_id == candidate.id,
        )
    )
    if application:
        return application
    application = JobApplication(
        job_id=job.id,
        candidate_id=candidate.id,
        current_stage=stage,
        status="active",
        source=source,
    )
    db.add(application)
    db.flush()
    db.add(
        ApplicationStageLog(
            application_id=application.id,
            from_stage=None,
            to_stage=stage,
            reason="seed data",
        )
    )
    return application


def create_sample_resume(db, candidate: Candidate) -> None:
    file_name = "sample-backend-resume.txt"
    existing = db.scalar(
        select(Resume).where(Resume.candidate_id == candidate.id, Resume.file_name == file_name)
    )

    resume_text = """姓名：张晨
电话：13800000001
邮箱：zhangchen@example.com
教育经历
2014-2018 上海交通大学 软件工程 本科
工作经历
2018-2022 云杉科技 后端工程师，负责企业级业务系统、权限服务和数据同步平台。
2022-至今 云杉科技 高级后端工程师，负责 FastAPI 微服务、PostgreSQL 数据建模、Redis 缓存优化和 Docker 部署。
技能
Python、FastAPI、PostgreSQL、Redis、Docker、微服务、架构
项目经历
AI 招聘流程管理平台：负责候选人、职位、简历上传和招聘流程核心模块，优化接口响应和数据一致性。
数据同步平台：设计任务调度、失败重试和审计日志机制，支撑多业务线数据同步。
"""
    content = resume_text.encode("utf-8")
    object_key = f"resumes/{candidate.id}/seed-sample-backend-resume.txt"
    storage = get_storage_service()
    storage.upload_bytes(object_key=object_key, content=content, content_type="text/plain")
    parsed_json = parse_resume_text(resume_text)

    stored_file = db.scalar(
        select(StoredFile).where(StoredFile.file_name == file_name, StoredFile.file_path == object_key)
    )
    if not stored_file:
        db.add(
            StoredFile(
                file_name=file_name,
                file_path=object_key,
                file_type="text/plain",
                file_size=len(content),
                storage_type="minio",
            )
        )

    if existing:
        existing.file_path = object_key
        existing.file_type = "text/plain"
        existing.file_size = len(content)
        existing.raw_text = resume_text
        existing.parsed_json = parsed_json
        existing.parse_status = "parsed"
        existing.parse_error = None
    else:
        db.add(
            Resume(
                candidate_id=candidate.id,
                file_name=file_name,
                file_path=object_key,
                file_type="text/plain",
                file_size=len(content),
                raw_text=resume_text,
                parsed_json=parsed_json,
                parse_status="parsed",
            )
        )


def get_sample_resume(db, candidate: Candidate) -> Resume | None:
    return db.scalar(
        select(Resume).where(
            Resume.candidate_id == candidate.id,
            Resume.file_name == "sample-backend-resume.txt",
        )
    )


def create_sample_ai_outputs(db, *, job: Job, candidate: Candidate, resume: Resume) -> None:
    summary = build_candidate_summary(candidate, resume)
    analysis = db.scalar(select(AIResumeAnalysis).where(AIResumeAnalysis.resume_id == resume.id))
    if not analysis:
        analysis = AIResumeAnalysis(candidate_id=candidate.id, resume_id=resume.id)
        db.add(analysis)
    analysis.summary = summary["summary"]
    analysis.skills_json = summary["skills"]
    analysis.work_experience_summary = summary["work_experience_summary"]
    analysis.project_experience_summary = summary["project_experience_summary"]
    analysis.education_summary = summary["education_summary"]
    analysis.strengths_json = summary["strengths"]
    analysis.risks_json = summary["risks"]
    analysis.interview_questions_json = generate_interview_questions(job, candidate, resume)
    analysis.raw_response = summary
    analysis.model_provider = "rules"
    analysis.model_name = "mock-recruitment"
    analysis.status = "completed"

    score = score_job_match(job, candidate, resume)
    match = db.scalar(
        select(JobMatchScore).where(
            JobMatchScore.job_id == job.id,
            JobMatchScore.candidate_id == candidate.id,
        )
    )
    if not match:
        match = JobMatchScore(job_id=job.id, candidate_id=candidate.id)
        db.add(match)
    match.total_score = score["total_score"]
    match.level = score["level"]
    match.dimension_scores_json = score["dimension_scores"]
    match.matched_points_json = score["matched_points"]
    match.missing_points_json = score["missing_points"]
    match.risk_points_json = score["risk_points"]
    match.recommendation = score["recommendation"]
    match.explanation = score["explanation"]
    match.raw_response = score
    match.model_provider = "rules"
    match.model_name = "mock-recruitment"
    match.status = "completed"


def main() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        jobs = {payload["title"]: get_or_create_job(db, payload.copy()) for payload in JOBS}
        candidates = {
            payload["name"]: get_or_create_candidate(db, payload.copy()) for payload in CANDIDATES
        }
        for job_title, candidate_name, stage, source in APPLICATIONS:
            get_or_create_application(
                db,
                job=jobs[job_title],
                candidate=candidates[candidate_name],
                stage=stage,
                source=source,
            )
        create_sample_resume(db, candidates["张晨"])
        resume = get_sample_resume(db, candidates["张晨"])
        if resume:
            create_sample_ai_outputs(
                db,
                job=jobs["高级后端工程师"],
                candidate=candidates["张晨"],
                resume=resume,
            )
        db.commit()
        print(f"Seed data ready at {datetime.utcnow().isoformat()}Z")
    finally:
        db.close()


if __name__ == "__main__":
    main()
