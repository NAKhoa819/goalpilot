import os
import json
from core.llm_gateway import get_completion
from core.intelligence import determine_strategy, compute_s_i
from core.prompts import build_system_prompt
from models.schemas import StrategyResponse
from db import get_user_context  # adjust to your actual db module


def run(user_id: str, user_message: str) -> StrategyResponse:
    """
    Run the financial reasoning agent for a given user.

    Args:
        user_id:      The user's unique identifier for fetching their context.
        user_message: The user's input message to the agent.

    Returns:
        A StrategyResponse with remediation steps.
    """
    user_context = get_user_context(user_id)

    s_i = compute_s_i(user_context)
    strategy = determine_strategy(s_i)

    print(f"[Context] User ID: {user_id}")
    print(f"[Context] Computed S_i: {s_i}")
    print(f"[Context] Triggered Strategy: {strategy}")

    system_prompt = build_system_prompt(user_context, strategy)
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]

    response = get_completion(
        messages=messages,
        response_format=StrategyResponse,
    )

    return response


if __name__ == "__main__":
    result = run(
        user_id="user-123",
        user_message="I am considering updating my computer with a new RTX 5090 costing $2,500. Would that be a good idea?",
    )

    print("\nAgent Remediation Steps:")
    for step in result.remediation_steps:
        print(f"- {step}")