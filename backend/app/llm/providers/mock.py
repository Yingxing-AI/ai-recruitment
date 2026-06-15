from typing import Any

from app.llm.base import LLMProvider


class MockLLMProvider(LLMProvider):
    provider_name = "mock"

    async def complete_json(self, prompt: str, schema_hint: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "summary": "这是一个占位 AI 分析结果，用于 MVP 联调。",
            "skills": ["沟通能力", "项目经验", "业务理解"],
            "risks": ["需要接入真实大模型后重新分析"],
            "prompt_length": len(prompt),
        }
