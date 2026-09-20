"""
Pluggable LLM Client Interface.

Supports multiple LLM backends (Google Gemini, OpenAI, or local models)
with unified request/response handling and structured output schemas.
"""

from typing import Any, Dict, Optional


class LLMClient:
    """
    Abstract interface for Large Language Model communication.
    Implementation will be activated in Phase 5.
    """

    def __init__(self, provider: str = "gemini", api_key: Optional[str] = None) -> None:
        self.provider = provider
        self.api_key = api_key

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Generate textual completion from the configured LLM backend."""
        raise NotImplementedError("LLM client generation will be implemented in Phase 5.")

    def generate_structured(
        self,
        prompt: str,
        response_schema: Any,
        system_instruction: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate structured JSON conforming to a Pydantic or schema definition."""
        raise NotImplementedError("Structured generation will be implemented in Phase 5.")
