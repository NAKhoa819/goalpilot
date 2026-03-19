import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Active provider toggle: must be "bedrock" or "backup"
ACTIVE_LLM_PROVIDER = os.getenv("ACTIVE_LLM_PROVIDER", "backup")

# Backup Engine details (when ACTIVE_LLM_PROVIDER is "backup")
BACKUP_PROVIDER = os.getenv("BACKUP_PROVIDER", "groq") # e.g., "groq", "gemini", or "mock"
BACKUP_MODEL_ID = os.getenv("BACKUP_MODEL_ID", "llama-3.3-70b-versatile") # e.g., "llama-3.1-8b-instant"

# Primary Engine details
BEDROCK_MODEL = os.getenv("BEDROCK_MODEL", "bedrock/anthropic.claude-3-5-sonnet-20240620-v1:0")
