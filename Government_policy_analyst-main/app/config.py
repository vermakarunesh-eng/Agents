from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    llm_provider: str = "mock"
    model_name: str = "mock-policy-analyst"
    openai_api_key: str = ""
    database_url: str = "sqlite:///./policy_agent.db"
    reports_dir: Path = Path("app/data/reports")
    memory_dir: Path = Path("app/data/memory")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()

