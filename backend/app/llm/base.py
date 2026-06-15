from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    provider_name: str

    @abstractmethod
    async def complete_json(self, prompt: str, schema_hint: dict[str, Any] | None = None) -> dict[str, Any]:
        """Return structured JSON from a model response."""
