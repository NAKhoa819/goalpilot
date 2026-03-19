from config import settings
from models.schemas import StrategyResponse

def get_model(provider: str = None):
    """
    Returns the correct LangChain chat model based on the ACTIVE_LLM_PROVIDER toggle.
    """
    selected_provider = provider or settings.ACTIVE_LLM_PROVIDER

    # Bedrock Engine details    
    if selected_provider.lower() == "bedrock":
        try:
            from langchain_aws import ChatBedrock
            return ChatBedrock(model_id=settings.BEDROCK_MODEL, region_name="us-east-1", model_kwargs={"temperature": 0.0})
        except ImportError:
            from langchain_community.chat_models import BedrockChat
            return BedrockChat(model_id=settings.BEDROCK_MODEL, region_name="us-east-1", model_kwargs={"temperature": 0.0})


    # Backup Engine details (when LLM_PROVIDER is "backup")
    elif selected_provider.lower() == "backup":
        backup_provider = settings.BACKUP_PROVIDER.lower()
        backup_model = settings.BACKUP_MODEL_ID
        
        if backup_provider == "groq":
            from langchain_groq import ChatGroq
            return ChatGroq(model=backup_model, temperature=0.0)
        elif backup_provider == "gemini":
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(model=backup_model, temperature=0.0)
        elif backup_provider == "mock":
            return "mock"
        else:
            raise ValueError(f"Unsupported backup provider: {backup_provider}")
    else:
        raise ValueError(f"Unsupported provider: {selected_provider}")

def get_completion(messages: list, response_format=None, provider=None):
    """
    Unified LLM completion function using LangChain.
    """
    selected_provider = provider or settings.ACTIVE_LLM_PROVIDER
    model = get_model(selected_provider)

    if model == "mock":
        # Simulate API response for testing the Sustainability Index ($S_i$) without API calls
        if response_format:
            # LangChain structured output binds and returns the Pydantic model directly
            return response_format(
                strategy="A",
                reasoning="S_i is below 0.8. Client spends excessively on dining out.",
                remediation_steps=[
                    "Reduce dining budget by 20%",
                    "Allocate savings to emergency fund"
                ]
            )
        else:
            return "Mock logic tested successfully"
            
    # LLM execution using LangChain
    if response_format:
        # Bind the Pydantic schema using .with_structured_output()
        structured_llm = model.with_structured_output(response_format)
        response = structured_llm.invoke(messages)
        return response
    else:
        response = model.invoke(messages)
        return response.content

def get_chat_advice(user_query: str, s_i: float) -> str:
    """
    Gets chat advice from the LLM, setting the personality based on the S_i value.
    Does not run any math calculations internally.
    """
    personality = "Strict and direct" if s_i < 0.5 else "Encouraging and supportive"
    
    system_prompt = (
        f"You are a financial advisor. Your personality should be {personality}. "
        f"The user's Sustainability Index is {s_i:.2f}. "
        "Provide helpful advice based on this index without running any calculations yourself."
    )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]
    
    return get_completion(messages=messages)
