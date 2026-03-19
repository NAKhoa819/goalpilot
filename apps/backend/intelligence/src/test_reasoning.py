import os
import json
from core.llm_gateway import get_completion
from core.intelligence import determine_strategy
from core.prompts import build_system_prompt
from models.schemas import StrategyResponse

def run_test():
    print("--- Testing Financial Reasoning (Gemini vs Llama 3) ---")
    
    # Simulate a scenario with a low S_i = 0.45 (45%)
    # S_i < 0.5 triggers Strategy B (Goal Re-alignment) in determine_strategy
    s_i = 0.45
    strategy = determine_strategy(s_i)
    
    print(f"\n[Context] Simulated S_i: {s_i}")
    print(f"[Context] Triggered Strategy: {strategy}")
    
    # Mock user context for the prompt
    user_context = {
        "balance": 1000,
        "monthly_spending": 3000,
        "goals": [{"name": "High Priority Retirement"}]
    }
    
    system_prompt = build_system_prompt(user_context, strategy)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "I need help with my finances. I spend too much and want to save for retirement."}
    ]
    
    # # Test Gemini
    # print("\n--- Testing Gemini ---")
    # try:
    #     gemini_response = get_completion(
    #         messages=messages,
    #         response_format=StrategyResponse,
    #         provider="gemini"
    #     )
    #     print("Gemini Remediation Steps:")
    #     for step in gemini_response.remediation_steps:
    #         print(f"- {step}")
    # except Exception as e:
    #     print(f"Gemini Test Failed: {e}")
        
    # # Test Llama 4
    # print("\n--- Testing llama-3.3-70b-versatile (via Groq) ---")
    # try:
    #     # Check if API key is present
    #     if not os.getenv("GROQ_API_KEY"):
    #         print("WARNING: GROQ_API_KEY environment variable is missing!")
    #         print("Please add it to your .env file to run this test successfully.")
    #         return

    #     llama_response = get_completion(
    #         messages=messages,
    #         response_format=StrategyResponse,
    #         provider="llama-3.3-70b-versatile"
    #     )
    #     print("llama-3.3-70b-versatile Remediation Steps:")
    #     for step in llama_response.remediation_steps:
    #         print(f"- {step}")
    # except Exception as e:
    #     print(f"llama-3.3-70b-versatile Test Failed: {e}")



    try:
        response = get_completion(
            messages=messages,
            response_format=StrategyResponse
        )
        print("Agent Remediation Steps:")
        for step in response.remediation_steps:
            print(f"- {step}")
    except Exception as e:
        print(f"Agent Test Failed: {e}")

if __name__ == "__main__":
    run_test()
