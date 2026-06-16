import re
from typing import Any

from sqlalchemy import select

from app.core.config import settings
from app.llm.base import LLMProvider
from app.llm.providers.mock import MockLLMProvider
from app.models.ai_analysis import AIResumeAnalysis, JobMatchScore
from app.models.candidate import Candidate
from app.models.job import Job
from app.models.resume import Resume
from app.services.resume_parser_service import SKILL_KEYWORDS


def get_llm_provider() -> LLMProvider:
    if settings.llm_provider == "mock":
        return MockLLMProvider()
    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")


def upsert_candidate_analysis(db, candidate: Candidate, resume: Resume) -> AIResumeAnalysis:
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
    return analysis


def upsert_job_match(
    db,
    job: Job,
    candidate: Candidate,
    resume: Resume,
    application_id: int | None = None,
) -> JobMatchScore:
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

    match_score.application_id = application_id
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
    return match_score


def upsert_interview_questions(
    db,
    job: Job,
    candidate: Candidate,
    resume: Resume,
) -> AIResumeAnalysis:
    questions = generate_interview_questions(job, candidate, resume)
    analysis = get_or_create_analysis(db, resume)
    if not analysis.summary:
        upsert_candidate_analysis(db, candidate, resume)
    analysis.interview_questions_json = questions
    analysis.model_provider = "rules"
    analysis.model_name = settings.llm_model
    analysis.status = "completed"
    analysis.error_message = None
    return analysis


def get_or_create_analysis(db, resume: Resume) -> AIResumeAnalysis:
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


def build_candidate_summary(candidate: Candidate, resume: Resume) -> dict[str, Any]:
    parsed = resume.parsed_json or {}
    skills = parsed.get("skills") or []
    work = parsed.get("work_experience") or []
    education = parsed.get("education") or []
    projects = parsed.get("projects") or []
    years = candidate.years_of_experience
    title = candidate.current_title or "候选人"

    strengths = []
    if skills:
        strengths.append(f"技能覆盖：{', '.join(skills[:6])}")
    if years and years >= 5:
        strengths.append(f"具备 {years} 年相关经验")
    if projects:
        strengths.append("有项目经历可追问落地细节")
    if not strengths:
        strengths.append("基础信息完整，可进入初步沟通")

    risks = []
    if not skills:
        risks.append("简历中技能信息不充分")
    if not work:
        risks.append("工作经历结构化信息较少")
    if not education:
        risks.append("教育背景未明确")

    interview_level = "建议初试"
    if len(skills) >= 4 and (years or 0) >= 5 and projects:
        interview_level = "建议优先面试"
    elif len(risks) >= 2:
        interview_level = "建议补充信息后面试"

    summary = (
        f"{candidate.name} 当前定位为{title}，"
        f"{f'约 {years} 年经验，' if years else ''}"
        f"核心技能包括 {', '.join(skills[:5]) if skills else '暂未明确'}。"
    )
    return {
        "summary": summary,
        "skills": skills,
        "work_experience_summary": summarize_lines(work),
        "project_experience_summary": summarize_lines(projects),
        "education_summary": summarize_lines(education),
        "strengths": strengths,
        "risks": risks,
        "interview_level": interview_level,
    }


def score_job_match(job: Job, candidate: Candidate, resume: Resume) -> dict[str, Any]:
    parsed = resume.parsed_json or {}
    resume_text = " ".join(
        [
            resume.raw_text or "",
            " ".join(parsed.get("skills") or []),
            " ".join(parsed.get("work_experience") or []),
            " ".join(parsed.get("projects") or []),
        ]
    ).lower()
    job_text = " ".join([job.jd_text or "", job.requirements_text or "", job.title or ""])
    required_keywords = extract_requirement_keywords(job_text)
    matched = [keyword for keyword in required_keywords if keyword.lower() in resume_text]
    missing = [keyword for keyword in required_keywords if keyword not in matched]

    skill_score = 100 if not required_keywords else round(len(matched) / len(required_keywords) * 100, 2)
    experience_score = score_experience(job, candidate)
    education_score = score_education(job, parsed)
    project_score = 85 if parsed.get("projects") else 55
    total = round(skill_score * 0.45 + experience_score * 0.25 + education_score * 0.15 + project_score * 0.15, 2)
    risks = []
    if missing:
        risks.append(f"缺少或未体现：{', '.join(missing[:6])}")
    if experience_score < 70:
        risks.append("工作年限与职位要求存在差距")
    if not parsed.get("work_experience"):
        risks.append("工作经历提取不足，需要人工复核")

    level = "高匹配" if total >= 80 else "中匹配" if total >= 60 else "低匹配"
    recommendation = "推荐进入面试" if total >= 75 else "建议补充沟通" if total >= 55 else "暂不优先推荐"
    explanation = (
        f"规则评分 {total} 分，技能匹配 {len(matched)}/{len(required_keywords) or 1}，"
        f"经验分 {experience_score}，项目分 {project_score}。"
    )
    return {
        "total_score": total,
        "level": level,
        "dimension_scores": {
            "skills": skill_score,
            "experience": experience_score,
            "education": education_score,
            "projects": project_score,
        },
        "matched_points": matched,
        "missing_points": missing,
        "risk_points": risks,
        "recommendation": recommendation,
        "explanation": explanation,
    }


def generate_interview_questions(job: Job, candidate: Candidate, resume: Resume) -> list[dict[str, Any]]:
    parsed = resume.parsed_json or {}
    skills = parsed.get("skills") or []
    projects = parsed.get("projects") or []
    technical = [
        {
            "type": "technical",
            "question": f"请结合实际项目说明你如何使用 {skill} 解决复杂问题。",
            "focus": skill,
        }
        for skill in skills[:5]
    ]
    if not technical:
        technical.append(
            {
                "type": "technical",
                "question": f"请说明你对 {job.title} 所需核心技术栈的理解和实践经验。",
                "focus": "核心技能",
            }
        )

    project_questions = [
        {
            "type": "project",
            "question": f"请展开介绍这个经历中的目标、职责、难点和结果：{project[:80]}",
            "focus": "项目复盘",
        }
        for project in projects[:3]
    ]
    if not project_questions:
        project_questions.append(
            {
                "type": "project",
                "question": "请介绍一个最能体现你能力的项目，包括你的职责、关键决策和业务结果。",
                "focus": "项目深度",
            }
        )

    behavior = [
        {
            "type": "behavior",
            "question": "请举例说明你在跨团队协作中遇到分歧时如何推进结果。",
            "focus": "沟通协作",
        },
        {
            "type": "behavior",
            "question": f"你为什么考虑 {job.title} 方向？未来 1-2 年希望在哪些能力上成长？",
            "focus": "动机稳定性",
        },
    ]
    return technical + project_questions + behavior


def summarize_lines(lines: list[str], max_items: int = 3) -> str:
    if not lines:
        return "未在简历中明确体现"
    return "；".join(lines[:max_items])


def extract_requirement_keywords(text: str) -> list[str]:
    found = [skill for skill in SKILL_KEYWORDS if skill.lower() in text.lower()]
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9+#.-]{1,24}|[\u4e00-\u9fa5]{2,8}", text)
    for token in tokens:
        if token in {"负责", "熟悉", "优先", "经验", "能力", "职位", "要求"}:
            continue
        if token in SKILL_KEYWORDS and token not in found:
            found.append(token)
    return found[:12]


def score_experience(job: Job, candidate: Candidate) -> int:
    years = candidate.years_of_experience
    if years is None:
        return 60
    if job.experience_min and years < job.experience_min:
        return max(40, 70 - (job.experience_min - years) * 10)
    if job.experience_max and years > job.experience_max + 5:
        return 80
    return 90 if years >= (job.experience_min or 0) else 75


def score_education(job: Job, parsed: dict[str, Any]) -> int:
    requirement = job.education_requirement
    education_text = " ".join(parsed.get("education") or [])
    if not requirement:
        return 80 if education_text else 65
    if requirement in education_text:
        return 90
    if "本科" in requirement and any(item in education_text for item in ["本科", "硕士", "博士"]):
        return 85
    if "硕士" in requirement and any(item in education_text for item in ["硕士", "博士"]):
        return 85
    return 60
