import os
import json
from config import settings
from core.llm_gateway import get_completion
from core.intelligence import calculate_metrics, determine_strategy
from core.prompts import build_system_prompt
from memory.retriever import ContextRetriever
from memory.history import ConversationHistory
from models.schemas import StrategyResponse

def main():
    print(f"--- Starting GoalPilot Intelligence Engine ---")
    print(f"Using LLM Provider: {settings.LLM_PROVIDER}")
    
    user_id = "user_123"
    
    # 1. Retrieve Data
    retriever = ContextRetriever()
    user_context = retriever.fetch_user_financial_context(user_id)
    
    market_context = {
        "inflation_rate": 0.03,
        "category_average_dining": 200.00
    }
    
    # 2. Intelligence Logic (Calculate S_i and select strategy)
    metrics = calculate_metrics(user_context)
    s_i = metrics["s_i"]
    c_s = metrics["c_s"]
    strategy = determine_strategy(s_i)
    
    print(f"\n[Intelligence] Calculated S_i: {s_i:.2f}")
    print(f"[Intelligence] Calculated C_s: {c_s:.2f}")
    print(f"[Intelligence] Triggered Strategy: {strategy}")
    
    if strategy == "None":
        print("Finances are sustainable. No intervention needed.")
        return

    # 3. Prompt Engineering
    system_prompt = build_system_prompt(user_context, strategy)
    
    # 4. Memory & Context
    history_manager = ConversationHistory()
    # E.g., Adding a dummy previous user message
    history_manager.add_message("user", "Can you review my finances?")
    
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history_manager.get_last_n_messages(5))

    # 5. LLM Gateway call (Enforce JSON Schema)
    print("\n[LLM] Calling Gateway...")
    
    response = get_completion(
        messages=messages,
        response_format=StrategyResponse
    )
    
    # Parse output 
    try:
        # With LangChain .with_structured_output(), the model returns the Pydantic schema directly
        strategy_response = response
        print("\n[LLM Response Context]")
        print(json.dumps(strategy_response.model_dump(), indent=2))
        
        # Already validated by Langchain/Pydantic
        print(f"\nSuccessfully validated via Pydantic: Strategy {strategy_response.strategy}")
        
    except Exception as e:
        print(f"Error parsing or validating response: {e}")

if __name__ == "__main__":
    main()
