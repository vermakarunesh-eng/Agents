from app.config import get_settings


class LLMClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    def complete(self, prompt: str) -> str:
        if self.settings.llm_provider.lower() == "mock" or not self.settings.openai_api_key:
            return self._mock_complete(prompt)
        return self._mock_complete(prompt)

    @staticmethod
    def _mock_complete(prompt: str) -> str:
        first_line = prompt.strip().splitlines()[0] if prompt.strip() else "Policy analysis"
        return f"Mock analysis generated for: {first_line[:120]}"

