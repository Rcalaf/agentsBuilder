"""Runtime configuration, read from environment variables prefixed AGENTSBUILDER_ (or from .env)."""

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="AGENTSBUILDER_", extra="ignore")

    database_url: str = "postgresql://agentsbuilder:agentsbuilder@localhost:5433/agentsbuilder"

    # Any OpenAI-compatible server (Ollama, vLLM, ...). Swapping servers is a config change.
    llm_base_url: str = "http://localhost:11434/v1"
    llm_api_key: SecretStr = SecretStr("not-needed")
    chat_model: str = ""
    embedding_model: str = "bge-m3"

    default_tenant_id: str = "dev"


@lru_cache
def get_settings() -> Settings:
    return Settings()
