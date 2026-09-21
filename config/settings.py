"""
Application Configuration and Settings Management.

Loads settings from environment variables and .env file with type validation
and sensible defaults for local development.
"""

from functools import lru_cache
import os
from pathlib import Path
from typing import Optional

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    from pydantic import Field

    class Settings(BaseSettings):
        """Typed application settings using Pydantic."""
        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8",
            extra="ignore"
        )

        # Application
        app_name: str = "E-Commerce IQ"
        app_env: str = "development"
        debug: bool = True
        log_level: str = "INFO"

        # Database
        database_url: str = "sqlite:///data/ecommerce_iq.db"

        # AI / LLM
        llm_provider: str = "gemini"
        gemini_api_key: Optional[str] = None
        gemini_model: str = "gemini-2.0-flash"
        openai_api_key: Optional[str] = None
        openai_model: str = "gpt-4o-mini"

        # UI
        streamlit_server_port: int = 8501
        streamlit_server_address: str = "localhost"

        @property
        def project_root(self) -> Path:
            """Return the absolute path to the project root directory."""
            return Path(__file__).resolve().parent.parent

        @property
        def resolved_database_url(self) -> str:
            """Return database URL with relative SQLite paths resolved to project root."""
            if self.database_url.startswith("sqlite:///"):
                path_str = self.database_url[len("sqlite:///"):]
                p = Path(path_str)
                if not p.is_absolute():
                    return f"sqlite:///{(self.project_root / p).resolve().as_posix()}"
            return self.database_url

except ImportError:
    # Fallback configuration object if pydantic-settings is not yet installed
    class Settings:  # type: ignore[no-redef]
        """Lightweight configuration fallback for pre-dependency environments."""
        def __init__(self) -> None:
            self.app_name = os.getenv("APP_NAME", "E-Commerce IQ")
            self.app_env = os.getenv("APP_ENV", "development")
            self.debug = os.getenv("DEBUG", "True").lower() in ("true", "1")
            self.log_level = os.getenv("LOG_LEVEL", "INFO")
            self.database_url = os.getenv("DATABASE_URL", "sqlite:///data/ecommerce_iq.db")
            self.llm_provider = os.getenv("LLM_PROVIDER", "gemini")
            self.gemini_api_key = os.getenv("GEMINI_API_KEY")
            self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
            self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            self.streamlit_server_port = int(os.getenv("STREAMLIT_SERVER_PORT", "8501"))
            self.streamlit_server_address = os.getenv("STREAMLIT_SERVER_ADDRESS", "localhost")

        @property
        def project_root(self) -> Path:
            """Return the absolute path to the project root directory."""
            return Path(__file__).resolve().parent.parent

        @property
        def resolved_database_url(self) -> str:
            """Return database URL with relative SQLite paths resolved to project root."""
            if self.database_url.startswith("sqlite:///"):
                path_str = self.database_url[len("sqlite:///"):]
                p = Path(path_str)
                if not p.is_absolute():
                    return f"sqlite:///{(self.project_root / p).resolve().as_posix()}"
            return self.database_url


@lru_cache()
def get_settings() -> Settings:
    """
    Return a cached singleton instance of the application settings.
    """
    return Settings()
