from config import settings
from core.llm_gateway import get_model
model = get_model()
provider = settings.ACTIVE_LLM_PROVIDER if settings.ACTIVE_LLM_PROVIDER == "bedrock" else settings.BACKUP_PROVIDER
print(f"Using {provider}: {settings.BEDROCK_MODEL if provider == 'bedrock' else settings.BACKUP_MODEL_ID}")

"""
This script allow to test the switch between Bedrock and Backup provider
To switch between Bedrock and Backup provider, change the ACTIVE_LLM_PROVIDER environment variable in the .env file
"""