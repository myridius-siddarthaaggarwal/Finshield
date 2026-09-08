import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
PROJECT_ROOT = BASE_DIR.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "FinShield Risk Assessment Workbench"
    PROJECT_VERSION: str = "1.0.0"
    ENV: str = "development"
    SECRET_KEY: str = "finshield-secret-key-super-secure-change-in-production-2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    PORT: int = 8000

    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/finshield.db"

    # AI Configuration
    ANTHROPIC_API_KEY: str = ""
    LLM_MODEL: str = "claude-3-7-sonnet-20250219"
    LLM_TEMPERATURE: float = 0.1
    CONFIDENCE_THRESHOLD: float = 0.70  # Below 70% routes to unanchored manual assessment

    # Governed Data Layer & Prompts Paths
    DATA_LAYER_DIR: Path = PROJECT_ROOT / "governed_data_layer"
    PROMPTS_DIR: Path = PROJECT_ROOT / "prompts"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000"
    ]

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
