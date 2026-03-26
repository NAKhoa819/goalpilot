import os
from pathlib import Path

from dotenv import dotenv_values, load_dotenv


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

# SageMaker car price model
SAGEMAKER_REGION = os.getenv("SAGEMAKER_REGION", "us-west-2")
SAGEMAKER_CAR_PRICE_ENDPOINT_NAME = os.getenv("SAGEMAKER_CAR_PRICE_ENDPOINT_NAME", "").strip()
SAGEMAKER_CAR_PRICE_CONTENT_TYPE = os.getenv("SAGEMAKER_CAR_PRICE_CONTENT_TYPE", "text/csv")
SAGEMAKER_CAR_PRICE_ACCEPT = os.getenv("SAGEMAKER_CAR_PRICE_ACCEPT", "text/csv").strip()
SAGEMAKER_CAR_PRICE_REQUEST_FORMAT = os.getenv("SAGEMAKER_CAR_PRICE_REQUEST_FORMAT", "").strip().lower()
CAR_PRICE_MODEL_REFERENCE_YEAR = int(os.getenv("CAR_PRICE_MODEL_REFERENCE_YEAR", "2026"))
CAR_PRICE_MODEL_OUTPUT_MULTIPLIER = float(
    os.getenv("CAR_PRICE_MODEL_OUTPUT_MULTIPLIER", "1000")
)
AWS_PROFILE = os.getenv("AWS_PROFILE", "").strip()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "").strip()
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "").strip()
AWS_SESSION_TOKEN = os.getenv("AWS_SESSION_TOKEN", "").strip()

# SQL Server connection
DB_SERVER = os.getenv("DB_SERVER", "localhost\\SQLEXPRESS")
DB_NAME = os.getenv("DB_NAME", "swinhackathon_db")
DB_DRIVER = os.getenv("DB_DRIVER", "{ODBC Driver 17 for SQL Server}")
DB_TRUSTED_CONNECTION = os.getenv("DB_TRUSTED_CONNECTION", "yes")
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_TRUST_SERVER_CERTIFICATE = os.getenv("DB_TRUST_SERVER_CERTIFICATE", "yes")
DB_ENCRYPT = os.getenv("DB_ENCRYPT", "no")
DB_SEED_DEFAULT_GOALS = os.getenv("DB_SEED_DEFAULT_GOALS", "no").strip().lower() in {"1", "true", "yes", "on"}


def _parse_force_strategy(value: str) -> str | None:
    normalized = (value or "").strip()
    if not normalized:
        return None
    if normalized not in {"A", "B", "None"}:
        raise ValueError("FORCE_STRATEGY must be one of: A, B, None")
    return normalized


FORCE_STRATEGY = _parse_force_strategy(os.getenv("FORCE_STRATEGY", ""))
RUNTIME_ENV_PATH = Path(os.getenv("RUNTIME_ENV_PATH", "/run/goalpilot/.env"))


def resolve_force_strategy() -> str | None:
    if RUNTIME_ENV_PATH.exists():
        runtime_values = dotenv_values(RUNTIME_ENV_PATH)
        runtime_force_strategy = _parse_force_strategy(str(runtime_values.get("FORCE_STRATEGY", "")))
        if runtime_force_strategy is not None:
            return runtime_force_strategy
    return FORCE_STRATEGY
