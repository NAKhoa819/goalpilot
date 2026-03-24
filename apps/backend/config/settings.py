import os
from pathlib import Path

from dotenv import load_dotenv


def _find_env_path() -> Path | None:
    current = Path(__file__).resolve()
    for base in [current.parent, *current.parents]:
        candidate = base / ".env"
        if candidate.exists():
            return candidate
    return None


ROOT_ENV_PATH = _find_env_path()

# Load shared root .env for the monorepo when it exists.
if ROOT_ENV_PATH is not None:
    load_dotenv(ROOT_ENV_PATH)

# Active provider toggle: must be "bedrock" or "backup"
ACTIVE_LLM_PROVIDER = os.getenv("ACTIVE_LLM_PROVIDER", "backup")

# Backup Engine details (when ACTIVE_LLM_PROVIDER is "backup")
BACKUP_PROVIDER = os.getenv("BACKUP_PROVIDER", "groq") # e.g., "groq", "gemini", or "mock"
BACKUP_MODEL_ID = os.getenv("BACKUP_MODEL_ID", "llama-3.3-70b-versatile") # e.g., "llama-3.1-8b-instant"

# Primary Engine details
BEDROCK_MODEL = os.getenv("BEDROCK_MODEL", "bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0")

# SQL Server connection
DB_SERVER = os.getenv("DB_SERVER", "localhost\\SQLEXPRESS")
DB_NAME = os.getenv("DB_NAME", "swinhackathon_db")
DB_DRIVER = os.getenv("DB_DRIVER", "{ODBC Driver 17 for SQL Server}")
DB_TRUSTED_CONNECTION = os.getenv("DB_TRUSTED_CONNECTION", "yes")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_TRUST_SERVER_CERTIFICATE = os.getenv("DB_TRUST_SERVER_CERTIFICATE", "yes")
DB_ENCRYPT = os.getenv("DB_ENCRYPT", "no")
