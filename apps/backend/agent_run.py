from intelligence.intelligence import calculate_metrics, determine_strategy
from intelligence.llm_gateway import get_completion
from intelligence.prompts import build_system_prompt
from memory.retriever import ContextRetriever
from models.schemas import StrategyResponse


def run(user_id: str, user_message: str) -> StrategyResponse:
    """
    Run the financial reasoning agent for a given user against the current
    backend module layout.
    """
    retriever = ContextRetriever()
    user_context = retriever.fetch_user_financial_context(user_id=user_id)

    profile = {
        "mu_hist": user_context.get("monthly_spending", 4500.0) * 0.9,
        "sigma_hist": user_context.get("monthly_spending", 4500.0) * 0.15,
        "beta_prop": user_context.get("monthly_spending", 4500.0),
        "last_update_timestamp": user_context.get("last_update_timestamp", 0.0),
        "data_completeness": user_context.get("data_completeness", 0.85),
        "market_volatility": user_context.get("market_volatility", 0.3),
    }

    metrics = calculate_metrics(profile)
    s_i = metrics["s_i"]
    strategy = determine_strategy(s_i)

    system_prompt = build_system_prompt(user_context, strategy if strategy != "None" else "A")
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    return get_completion(
        messages=messages,
        response_format=StrategyResponse,
    )


if __name__ == "__main__":
    result = run(
        user_id="user_123",
        user_message="I am considering updating my computer with a new RTX 5090 costing $2,500. Would that be a good idea?",
    )

    print("\nAgent Remediation Steps:")
    for step in result.remediation_steps:
        print(f"- {step}")

