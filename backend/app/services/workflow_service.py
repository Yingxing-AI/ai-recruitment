from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WorkflowRule:
    intent: str
    keywords: tuple[str, ...]
    required_terms: tuple[str, ...]
    required_inputs: tuple[str, ...]
    action_template: str
    suggested_steps: tuple[str, ...]


WORKFLOW_RULES: tuple[WorkflowRule, ...] = (
    WorkflowRule(
        intent="resume_parse",
        keywords=("解析简历", "简历解析", "提取简历", "解析文本", "parse resume"),
        required_terms=("简历", "解析"),
        required_inputs=("resume_id",),
        action_template="POST /api/v1/ai/resumes/{resume_id}/parse",
        suggested_steps=(
            "确认已上传简历",
            "补全 resume_id 后执行解析",
            "解析后可继续生成候选人总结",
        ),
    ),
    WorkflowRule(
        intent="candidate_summary",
        keywords=("生成总结", "候选人总结", "简历总结", "总结候选人", "summarize"),
        required_terms=("总结",),
        required_inputs=("resume_id",),
        action_template="POST /api/v1/ai/resumes/{resume_id}/summary",
        suggested_steps=(
            "先完成简历解析",
            "确认 resume_id",
            "生成候选人摘要和优势风险",
        ),
    ),
    WorkflowRule(
        intent="job_match",
        keywords=("匹配", "评分", "推荐", "岗位匹配", "job match"),
        required_terms=("匹配",),
        required_inputs=("job_id", "candidate_id"),
        action_template="POST /api/v1/ai/jobs/{job_id}/candidates/{candidate_id}/match",
        suggested_steps=(
            "选择职位",
            "选择候选人",
            "生成岗位匹配评分与推荐结论",
        ),
    ),
    WorkflowRule(
        intent="interview_questions",
        keywords=("面试题", "面试问题", "追问", "interview questions"),
        required_terms=("面试",),
        required_inputs=("job_id", "candidate_id"),
        action_template="POST /api/v1/ai/jobs/{job_id}/candidates/{candidate_id}/interview-questions",
        suggested_steps=(
            "选择职位",
            "选择候选人",
            "生成结构化面试追问清单",
        ),
    ),
)


def interpret_workflow_instruction(
    instruction: str,
    *,
    job_id: int | None = None,
    candidate_id: int | None = None,
    resume_id: int | None = None,
) -> dict[str, object]:
    normalized = (instruction or "").strip().lower()
    if not normalized:
        return build_unknown_result(
            instruction=instruction,
            reason="请先输入一段自然语言指令。",
            job_id=job_id,
            candidate_id=candidate_id,
            resume_id=resume_id,
        )

    matched_rule = None
    matched_keywords: list[str] = []
    for rule in WORKFLOW_RULES:
        hits = [keyword for keyword in rule.keywords if keyword.lower() in normalized]
        has_required_terms = all(term.lower() in normalized for term in rule.required_terms)
        if hits or has_required_terms:
            matched_rule = rule
            matched_keywords = hits or [term for term in rule.required_terms if term.lower() in normalized]
            break

    if not matched_rule:
        return build_unknown_result(
            instruction=instruction,
            reason="未识别到可执行的招聘工作流。",
            job_id=job_id,
            candidate_id=candidate_id,
            resume_id=resume_id,
        )

    available_inputs = {
        "job_id": job_id,
        "candidate_id": candidate_id,
        "resume_id": resume_id,
    }
    missing_inputs = [name for name in matched_rule.required_inputs if available_inputs.get(name) is None]
    confidence = min(0.95, 0.55 + 0.12 * len(matched_keywords))
    can_execute = not missing_inputs
    return {
        "instruction": instruction,
        "intent": matched_rule.intent,
        "confidence": round(confidence, 2),
        "matched_keywords": matched_keywords,
        "required_inputs": list(matched_rule.required_inputs),
        "missing_inputs": missing_inputs,
        "recommended_action": build_action(matched_rule.action_template, job_id, candidate_id, resume_id),
        "suggested_steps": list(matched_rule.suggested_steps),
        "execution_hint": build_execution_hint(matched_rule.intent, missing_inputs),
        "can_execute": can_execute,
        "job_id": job_id,
        "candidate_id": candidate_id,
        "resume_id": resume_id,
    }


def build_unknown_result(
    *,
    instruction: str,
    reason: str,
    job_id: int | None,
    candidate_id: int | None,
    resume_id: int | None,
) -> dict[str, object]:
    return {
        "instruction": instruction,
        "intent": "unknown",
        "confidence": 0.0,
        "matched_keywords": [],
        "required_inputs": [],
        "missing_inputs": [],
        "recommended_action": "请补充更明确的招聘任务描述，例如“解析简历并生成总结”或“为候选人做岗位匹配”",
        "suggested_steps": [
            "说明你想处理的对象",
            "补充职位、候选人或简历编号",
            "重新发起工作流解析",
        ],
        "execution_hint": reason,
        "can_execute": False,
        "job_id": job_id,
        "candidate_id": candidate_id,
        "resume_id": resume_id,
    }


def build_action(
    template: str,
    job_id: int | None,
    candidate_id: int | None,
    resume_id: int | None,
) -> str:
    values = {
        "job_id": job_id if job_id is not None else "{job_id}",
        "candidate_id": candidate_id if candidate_id is not None else "{candidate_id}",
        "resume_id": resume_id if resume_id is not None else "{resume_id}",
    }
    return template.format(**values)


def build_execution_hint(intent: str, missing_inputs: list[str]) -> str:
    if missing_inputs:
        return f"缺少必要输入：{', '.join(missing_inputs)}。"
    if intent == "resume_parse":
        return "可直接执行简历解析。"
    if intent == "candidate_summary":
        return "建议先确认简历已解析，再生成候选人总结。"
    if intent == "job_match":
        return "可直接执行岗位匹配评分。"
    if intent == "interview_questions":
        return "可直接生成面试问题。"
    return "请先补充上下文后再执行。"
