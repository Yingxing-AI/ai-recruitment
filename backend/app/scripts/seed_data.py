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
from app.models.interview import Interview
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
    {
        "name": "周航",
        "phone": "13800000005",
        "email": "zhouhang@example.com",
        "current_company": "云图网络",
        "current_title": "全栈工程师",
        "years_of_experience": 5,
        "current_city": "杭州",
        "source": "internal_referral",
        "status": "active",
        "tags": ["React", "FastAPI", "Docker"],
    },
    {
        "name": "陈静",
        "phone": "13800000006",
        "email": "chenjing@example.com",
        "current_company": "北斗科技",
        "current_title": "招聘运营专员",
        "years_of_experience": 4,
        "current_city": "北京",
        "source": "job_board",
        "status": "active",
        "tags": ["招聘运营", "候选人沟通"],
    },
]

APPLICATIONS = [
    ("高级后端工程师", "张晨", "screening", "referral"),
    ("前端工程师", "李悦", "first_interview", "job_board"),
    ("招聘运营专员", "王昊", "second_interview", "headhunter"),
    ("高级后端工程师", "赵琳", "final_interview", "inbound"),
    ("前端工程师", "周航", "offer", "internal_referral"),
    ("招聘运营专员", "陈静", "hired", "job_board"),
]

SAMPLE_RESUMES = [
    {
        "candidate": "张晨",
        "job": "高级后端工程师",
        "file_name": "sample-backend-resume.txt",
        "text": """姓名：张晨
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
""",
    },
    {
        "candidate": "李悦",
        "job": "前端工程师",
        "file_name": "sample-frontend-resume.txt",
        "text": """姓名：李悦
电话：13800000002
邮箱：liyue@example.com
教育经历
2016-2020 浙江大学 计算机科学与技术 本科
工作经历
2020-2022 星河互动 前端工程师，负责招聘系统和企业后台管理台建设。
2022-至今 星河互动 高级前端工程师，负责 React、TypeScript、Ant Design 组件体系和性能优化。
技能
React、TypeScript、Ant Design、Vite、状态管理、前端工程化
项目经历
招聘中台：搭建表单配置、列表查询和权限相关前端流程，提升运营效率。
可视化工作台：设计招聘漏斗和数据看板，支持业务方快速查看转化。
""",
    },
    {
        "candidate": "王昊",
        "job": "招聘运营专员",
        "file_name": "sample-recruiting-resume.txt",
        "text": """姓名：王昊
电话：13800000003
邮箱：wanghao@example.com
教育经历
2015-2019 北京师范大学 人力资源管理 本科
工作经历
2019-2021 北辰咨询 招聘专员，负责候选人筛选、面试安排和 Offer 跟进。
2021-至今 北辰咨询 招聘运营，负责职位发布、数据汇总和招聘流程推进。
技能
招聘运营、候选人沟通、面试协调、数据整理、流程管理
项目经历
校招项目：协同业务面试官完成批量简历筛选、面试排期和 Offer 签约。
内部招聘看板：梳理招聘阶段和漏斗数据，帮助团队识别卡点。
""",
    },
    {
        "candidate": "赵琳",
        "job": "高级后端工程师",
        "file_name": "sample-senior-backend-resume.txt",
        "text": """姓名：赵琳
电话：13800000004
邮箱：zhaolin@example.com
教育经历
2012-2016 电子科技大学 软件工程 本科
工作经历
2016-2020 青木数据 后端工程师，负责数据平台 API 和权限系统。
2020-至今 青木数据 高级后端工程师，负责高并发服务、PostgreSQL 优化和消息队列治理。
技能
Python、FastAPI、PostgreSQL、Redis、消息队列、Docker、架构设计
项目经历
数据服务平台：完成核心 API 重构和缓存策略优化，降低接口响应时延。
任务调度平台：设计幂等执行和失败重试方案，提升稳定性。
""",
    },
]

VIRTUAL_INSTANCES = [
    {
        "candidate": {
            "name": "孙萌",
            "phone": "13800000007",
            "email": "sunmeng@example.com",
            "current_company": "星图科技",
            "current_title": "后端工程师",
            "years_of_experience": 4,
            "current_city": "上海",
            "source": "referral",
            "status": "active",
            "tags": ["Python", "Redis"],
        },
        "job": "高级后端工程师",
        "stage": "screening",
        "source": "referral",
        "file_name": "virtual-backend-01.txt",
        "text": """姓名：孙萌
电话：13800000007
邮箱：sunmeng@example.com
工作经历
2021-至今 星图科技 后端工程师，负责招聘系统接口、缓存和任务调度。
技能
Python、FastAPI、Redis、PostgreSQL、Docker
项目经历
招聘后台：实现职位和候选人相关 API，完成日志留痕与数据查询。
""",
    },
    {
        "candidate": {
            "name": "周宁",
            "phone": "13800000008",
            "email": "zhouning@example.com",
            "current_company": "云谷互联",
            "current_title": "前端工程师",
            "years_of_experience": 5,
            "current_city": "杭州",
            "source": "job_board",
            "status": "active",
            "tags": ["React", "TypeScript"],
        },
        "job": "前端工程师",
        "stage": "first_interview",
        "source": "job_board",
        "file_name": "virtual-frontend-01.txt",
        "text": """姓名：周宁
电话：13800000008
邮箱：zhouning@example.com
工作经历
2020-至今 云谷互联 前端工程师，负责管理后台、表格和表单体验优化。
技能
React、TypeScript、Ant Design、Vite
项目经历
招聘运营台：搭建仪表盘与流程页面，提升运营效率。
""",
    },
    {
        "candidate": {
            "name": "吴桐",
            "phone": "13800000009",
            "email": "wutong@example.com",
            "current_company": "北辰咨询",
            "current_title": "招聘运营专员",
            "years_of_experience": 3,
            "current_city": "北京",
            "source": "headhunter",
            "status": "active",
            "tags": ["招聘运营", "候选人沟通"],
        },
        "job": "招聘运营专员",
        "stage": "screening",
        "source": "headhunter",
        "file_name": "virtual-ops-01.txt",
        "text": """姓名：吴桐
电话：13800000009
邮箱：wutong@example.com
工作经历
2022-至今 北辰咨询 招聘运营专员，负责简历筛选、面试排期和 Offer 沟通。
技能
招聘运营、沟通协调、流程推进、数据整理
项目经历
校招支持：完成批量面试排期和候选人跟进。
""",
    },
    {
        "candidate": {
            "name": "郑浩",
            "phone": "13800000010",
            "email": "zhenghao@example.com",
            "current_company": "青木数据",
            "current_title": "高级后端工程师",
            "years_of_experience": 7,
            "current_city": "深圳",
            "source": "inbound",
            "status": "active",
            "tags": ["PostgreSQL", "架构"],
        },
        "job": "高级后端工程师",
        "stage": "second_interview",
        "source": "inbound",
        "file_name": "virtual-backend-02.txt",
        "text": """姓名：郑浩
电话：13800000010
邮箱：zhenghao@example.com
工作经历
2018-至今 青木数据 高级后端工程师，负责高并发服务与数据库优化。
技能
Python、FastAPI、PostgreSQL、Redis、消息队列、Docker
项目经历
数据中台：重构服务边界并优化接口性能。
""",
    },
    {
        "candidate": {
            "name": "黄思雨",
            "phone": "13800000011",
            "email": "huangsiyu@example.com",
            "current_company": "星河互动",
            "current_title": "前端工程师",
            "years_of_experience": 4,
            "current_city": "杭州",
            "source": "internal_referral",
            "status": "active",
            "tags": ["React", "Ant Design"],
        },
        "job": "前端工程师",
        "stage": "offer",
        "source": "internal_referral",
        "file_name": "virtual-frontend-02.txt",
        "text": """姓名：黄思雨
电话：13800000011
邮箱：huangsiyu@example.com
工作经历
2020-至今 星河互动 前端工程师，负责数据看板与业务后台。
技能
React、TypeScript、Ant Design、性能优化
项目经历
招聘仪表盘：实现统计卡片和漏斗图表。
""",
    },
    {
        "candidate": {
            "name": "许航",
            "phone": "13800000012",
            "email": "xuhang@example.com",
            "current_company": "北斗科技",
            "current_title": "招聘运营专员",
            "years_of_experience": 5,
            "current_city": "北京",
            "source": "job_board",
            "status": "active",
            "tags": ["流程管理", "数据整理"],
        },
        "job": "招聘运营专员",
        "stage": "hired",
        "source": "job_board",
        "file_name": "virtual-ops-02.txt",
        "text": """姓名：许航
电话：13800000012
邮箱：xuhang@example.com
工作经历
2019-至今 北斗科技 招聘运营专员，负责职位发布、面试协调和招聘数据分析。
技能
招聘运营、数据分析、沟通协调、流程管理
项目经历
招聘数据台账：沉淀阶段数据与候选人流转信息。
""",
    },
    {
        "candidate": {
            "name": "梁晨",
            "phone": "13800000013",
            "email": "liangchen@example.com",
            "current_company": "云杉科技",
            "current_title": "后端工程师",
            "years_of_experience": 5,
            "current_city": "上海",
            "source": "referral",
            "status": "active",
            "tags": ["FastAPI", "Docker"],
        },
        "job": "高级后端工程师",
        "stage": "first_interview",
        "source": "referral",
        "file_name": "virtual-backend-03.txt",
        "text": """姓名：梁晨
电话：13800000013
邮箱：liangchen@example.com
工作经历
2020-至今 云杉科技 后端工程师，负责招聘业务接口和任务调度。
技能
Python、FastAPI、Redis、Docker
项目经历
招聘流程自动化：支持简历导入和阶段流转。
""",
    },
    {
        "candidate": {
            "name": "林然",
            "phone": "13800000014",
            "email": "linran@example.com",
            "current_company": "智链网络",
            "current_title": "前端工程师",
            "years_of_experience": 3,
            "current_city": "广州",
            "source": "job_board",
            "status": "active",
            "tags": ["TypeScript", "Vite"],
        },
        "job": "前端工程师",
        "stage": "screening",
        "source": "job_board",
        "file_name": "virtual-frontend-03.txt",
        "text": """姓名：林然
电话：13800000014
邮箱：linran@example.com
工作经历
2022-至今 智链网络 前端工程师，负责内部管理台和表单页面。
技能
React、TypeScript、Vite、Ant Design
项目经历
人事工作台：优化表格筛选和表单提交体验。
""",
    },
    {
        "candidate": {
            "name": "蒋雪",
            "phone": "13800000015",
            "email": "jiangxue@example.com",
            "current_company": "启航咨询",
            "current_title": "招聘运营专员",
            "years_of_experience": 4,
            "current_city": "深圳",
            "source": "headhunter",
            "status": "active",
            "tags": ["招聘", "数据汇总"],
        },
        "job": "招聘运营专员",
        "stage": "final_interview",
        "source": "headhunter",
        "file_name": "virtual-ops-03.txt",
        "text": """姓名：蒋雪
电话：13800000015
邮箱：jiangxue@example.com
工作经历
2021-至今 启航咨询 招聘运营专员，负责候选人维护与面试协调。
技能
招聘运营、流程跟进、沟通协调、数据统计
项目经历
招聘效率项目：梳理漏斗阶段和卡点。
""",
    },
    {
        "candidate": {
            "name": "罗杰",
            "phone": "13800000016",
            "email": "luojie@example.com",
            "current_company": "星图科技",
            "current_title": "高级后端工程师",
            "years_of_experience": 9,
            "current_city": "北京",
            "source": "inbound",
            "status": "active",
            "tags": ["架构", "PostgreSQL", "Redis"],
        },
        "job": "高级后端工程师",
        "stage": "offer",
        "source": "inbound",
        "file_name": "virtual-backend-04.txt",
        "text": """姓名：罗杰
电话：13800000016
邮箱：luojie@example.com
工作经历
2015-至今 星图科技 高级后端工程师，负责核心平台架构和数据库治理。
技能
Python、FastAPI、PostgreSQL、Redis、架构设计
项目经历
招聘平台核心服务：保障高并发下的稳定性与可维护性。
""",
    },
    {
        "candidate": {
            "name": "邵雨",
            "phone": "13800000017",
            "email": "shaoyu@example.com",
            "current_company": "云谷互联",
            "current_title": "前端工程师",
            "years_of_experience": 6,
            "current_city": "杭州",
            "source": "referral",
            "status": "active",
            "tags": ["React", "状态管理"],
        },
        "job": "前端工程师",
        "stage": "second_interview",
        "source": "referral",
        "file_name": "virtual-frontend-04.txt",
        "text": """姓名：邵雨
电话：13800000017
邮箱：shaoyu@example.com
工作经历
2019-至今 云谷互联 前端工程师，负责企业中台和看板页面。
技能
React、TypeScript、Ant Design、Zustand
项目经历
招聘仪表盘：搭建数据展示和交互筛选。
""",
    },
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


def create_sample_resume(db, candidate: Candidate, *, file_name: str, resume_text: str) -> None:
    existing = db.scalar(
        select(Resume).where(Resume.candidate_id == candidate.id, Resume.file_name == file_name)
    )
    content = resume_text.encode("utf-8")
    object_key = f"resumes/{candidate.id}/seed-{file_name}"
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


def get_sample_application(db, job: Job, candidate: Candidate) -> JobApplication | None:
    return db.scalar(
        select(JobApplication).where(
            JobApplication.job_id == job.id,
            JobApplication.candidate_id == candidate.id,
        )
    )


def get_or_create_interview(
    db,
    *,
    application: JobApplication,
    round_number: int,
    interview_type: str,
) -> None:
    interview = db.scalar(
        select(Interview).where(
            Interview.application_id == application.id,
            Interview.round == round_number,
        )
    )
    if interview:
        return
    db.add(
        Interview(
            application_id=application.id,
            job_id=application.job_id,
            candidate_id=application.candidate_id,
            round=round_number,
            interview_type=interview_type,
            status="scheduled",
        )
    )


def get_sample_resume(db, candidate: Candidate, *, file_name: str) -> Resume | None:
    return db.scalar(
        select(Resume).where(
            Resume.candidate_id == candidate.id,
            Resume.file_name == file_name,
        )
    )


def create_virtual_instance(db, instance: dict, jobs: dict[str, Job], candidates: dict[str, Candidate]) -> None:
    candidate = get_or_create_candidate(db, instance["candidate"].copy())
    candidates[candidate.name] = candidate
    job = jobs[instance["job"]]
    get_or_create_application(
        db,
        job=job,
        candidate=candidate,
        stage=instance["stage"],
        source=instance["source"],
    )
    create_sample_resume(
        db,
        candidate,
        file_name=instance["file_name"],
        resume_text=instance["text"],
    )
    resume = get_sample_resume(db, candidate, file_name=instance["file_name"])
    if resume:
        create_sample_ai_outputs(
            db,
            job=job,
            candidate=candidate,
            resume=resume,
        )

    interview_stage_map = {
        "first_interview": (1, "video"),
        "second_interview": (2, "video"),
        "final_interview": (3, "onsite"),
    }
    interview_plan = interview_stage_map.get(instance["stage"])
    if interview_plan:
        application = get_sample_application(db, job, candidate)
        if application:
            get_or_create_interview(
                db,
                application=application,
                round_number=interview_plan[0],
                interview_type=interview_plan[1],
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
        for sample in SAMPLE_RESUMES:
            create_sample_resume(
                db,
                candidates[sample["candidate"]],
                file_name=sample["file_name"],
                resume_text=sample["text"],
            )
            resume = get_sample_resume(
                db,
                candidates[sample["candidate"]],
                file_name=sample["file_name"],
            )
            if resume:
                create_sample_ai_outputs(
                    db,
                    job=jobs[sample["job"]],
                    candidate=candidates[sample["candidate"]],
                    resume=resume,
                )

        for instance in VIRTUAL_INSTANCES:
            create_virtual_instance(db, instance, jobs, candidates)

        interview_plan = [
            ("李悦", "前端工程师", 1, "video"),
            ("王昊", "招聘运营专员", 1, "onsite"),
            ("赵琳", "高级后端工程师", 2, "video"),
        ]
        for candidate_name, job_title, round_number, interview_type in interview_plan:
            application = get_sample_application(db, jobs[job_title], candidates[candidate_name])
            if application:
                get_or_create_interview(
                    db,
                    application=application,
                    round_number=round_number,
                    interview_type=interview_type,
                )
        db.commit()
        print(f"Seed data ready at {datetime.utcnow().isoformat()}Z")
    finally:
        db.close()


if __name__ == "__main__":
    main()
