from app.services.workflow_service import interpret_workflow_instruction


def test_interpret_workflow_instruction_detects_resume_parse() -> None:
    result = interpret_workflow_instruction("帮我解析这份简历", resume_id=12)

    assert result["intent"] == "resume_parse"
    assert result["can_execute"] is True
    assert result["recommended_action"] == "POST /api/v1/ai/resumes/12/parse"
    assert "解析" in result["matched_keywords"]
    assert "简历" in result["matched_keywords"]


def test_interpret_workflow_instruction_reports_missing_inputs() -> None:
    result = interpret_workflow_instruction("请帮我做岗位匹配", job_id=7)

    assert result["intent"] == "job_match"
    assert result["can_execute"] is False
    assert result["missing_inputs"] == ["candidate_id"]
    assert result["execution_hint"] == "缺少必要输入：candidate_id。"


def test_interpret_workflow_instruction_handles_unknown_intent() -> None:
    result = interpret_workflow_instruction("帮我看看这个系统还能优化什么")

    assert result["intent"] == "unknown"
    assert result["can_execute"] is False
    assert result["confidence"] == 0.0
    assert result["matched_keywords"] == []
