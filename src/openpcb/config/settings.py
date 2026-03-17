from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Runtime settings for the OpenPCB application.

    Values are loaded in this order (highest priority first):
    1. Environment variables
    2. .env file
    3. Default values defined in this class
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ------------------------------------------------------------------
    # App metadata
    # ------------------------------------------------------------------
    app_name: str = Field(default="openpcb")
    app_env: str = Field(default="dev")
    debug: bool = Field(default=False)

    # ------------------------------------------------------------------
    # Project paths
    # ------------------------------------------------------------------
    project_root: Path = Field(default_factory=lambda: Path.cwd())
    data_dir: Path = Field(default_factory=lambda: Path("data"))
    prompts_dir: Path = Field(default_factory=lambda: Path("src/openpcb/prompts"))

    # ------------------------------------------------------------------
    # LLM settings
    # ------------------------------------------------------------------
    llm_provider: str = Field(default="openai")
    llm_model: str = Field(default="gpt-4.1-mini")
    llm_api_key: str = Field(default="")
    llm_base_url: str | None = Field(default=None)
    llm_timeout_seconds: float = Field(default=60.0)
    llm_temperature: float = Field(default=0.2)
    llm_max_retries: int = Field(default=2)

    # ------------------------------------------------------------------
    # Agent settings
    # ------------------------------------------------------------------
    agent_max_clarification_rounds: int = Field(default=3)
    agent_enable_memory: bool = Field(default=False)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------
    @property
    def resolved_data_dir(self) -> Path:
        """
        Return an absolute path for the data directory.
        """
        if self.data_dir.is_absolute():
            return self.data_dir
        return self.project_root / self.data_dir

    @property
    def resolved_prompts_dir(self) -> Path:
        """
        Return an absolute path for the prompts directory.
        """
        if self.prompts_dir.is_absolute():
            return self.prompts_dir
        return self.project_root / self.prompts_dir

    @property
    def has_llm_api_key(self) -> bool:
        """
        Whether an API key is configured.
        """
        return bool(self.llm_api_key.strip())


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return a cached Settings instance.

    This ensures the application uses one consistent settings object
    during a process lifetime.
    """
    return Settings()