from config import settings


def build_fallback_chat_advice(user_query: str, s_i: float) -> str:
    """
    Deterministic fallback used when the external LLM is unavailable.
    Keeps chat usable during network, quota, or provider outages.
    """
    if s_i < 0.5:
        tone = "Your financial situation needs attention right away."
        action = "Cut one non-essential expense this month and prioritize increasing your savings."
    else:
        tone = "Your finances look stable overall."
        action = "Stay close to your goal and review weekly spending so you do not drift over budget."

    if user_query.strip():
        context = f"You asked: '{user_query.strip()}'."
    else:
        context = "You sent a financial advice request."

    return f"{tone} {context} {action}"

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
            return ChatGroq(model=backup_model, temperature=0.7)
        elif backup_provider == "gemini":
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(model=backup_model, temperature=0.7)
        elif backup_provider == "mock":
            return "mock"
        else:
            raise ValueError(f"Unsupported backup provider: {backup_provider}")
    else:
        raise ValueError(f"Unsupported provider: {selected_provider}")
    
    #Note: Temperature range [0.0, 1.0]
    #towards 1 give more diverse and creative responses
    #towards 0 give more deterministic and focused responses

def get_completion(messages: list, response_format=None, provider=None):
    """
    Unified LLM completion function using LangChain.
    """
    selected_provider = provider or settings.ACTIVE_LLM_PROVIDER
    model = get_model(selected_provider)

    if model == "mock":
        # Simulate API response for testing the Sustainability Index ($S_i$) without API calls
        if response_format:
            field_names = set(getattr(response_format, "model_fields", {}).keys())
            if {"strategy", "reasoning", "remediation_steps"}.issubset(field_names):
                return response_format(
                    strategy="A",
                    reasoning="S_i is below 0.8. Client spends excessively on dining out.",
                    remediation_steps=[
                        "Reduce dining budget by 20%",
                        "Allocate savings to emergency fund"
                    ]
                )
            if {"risk_summary", "plan_a_reason", "plan_a_saving_tips", "plan_b_reason"}.issubset(field_names):
                return response_format(
                    risk_summary="Your goal is off track because current savings are not closing the gap quickly enough.",
                    plan_a_reason="Plan A works if you can free up more money each month and redirect it to this goal.",
                    plan_a_saving_tips=[
                        "Trim one flexible spending category this month.",
                        "Pause a low-value subscription and move that amount to savings.",
                    ],
                    plan_b_reason="Plan B works if you want to reduce monthly pressure and spread the goal over a safer timeline.",
                )
            if {"is_car_purchase_goal", "confidence_score"}.issubset(field_names):
                serialized_messages = " ".join(str(message.get("content", "")) for message in messages if isinstance(message, dict))
                lowered = serialized_messages.lower()
                is_car_goal = (
                    "car" in lowered
                    and any(token in lowered for token in ("buy", "purchase", "goal", "create", "add"))
                )
                return response_format(
                    is_car_purchase_goal=is_car_goal,
                    confidence_score=0.9 if is_car_goal else 0.1,
                )
            return response_format()
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
