from __future__ import annotations

from typing import Any

from intelligence.llm_gateway import get_completion
from intelligence.prompts import build_at_risk_chat_prompt
from models.schemas import AtRiskProposalResponse
from utils.currency import format_usd


def _find_action(actions: list[dict], action_type: str) -> dict | None:
    for action in actions:
        if action.get("type") == action_type:
            return action
    return None


def _fallback_chat_text(goal: dict, actions: list[dict]) -> str:
    goal_name = goal.get("goal_name", "your goal")
    action_a = _find_action(actions, "A")
    action_b = _find_action(actions, "B")

    parts = [f"Your {goal_name} goal is currently off track."]

    if action_a:
        payload = action_a.get("payload", {})
        amount = int(payload.get("amount", 0))
        duration_months = payload.get("duration_months")
        duration_text = f" for the next {duration_months} months" if duration_months else ""
        parts.append(
            f"Plan A helps if you can save an extra {format_usd(amount)} per month{duration_text}. "
            "Start with flexible spending like dining, shopping, or subscriptions."
        )

    if action_b:
        payload = action_b.get("payload", {})
        months = payload.get("months")
        new_target_date = payload.get("new_target_date")
        schedule_text = []
        if months:
            schedule_text.append(f"extend the deadline by {months} months")
        if new_target_date:
            schedule_text.append(f"move the target date to {new_target_date}")
        suffix = " and ".join(schedule_text) if schedule_text else "reduce timeline pressure"
        parts.append(f"Plan B helps if you want to {suffix} and make the goal more realistic.")

    parts.append("Choose the direction that fits your cash flow best.")
    return "\n\n".join(parts)


def _recommended_plan_text(goal: dict, action: dict) -> str:
    goal_name = goal.get("goal_name", "your goal")
    payload = action.get("payload", {})

    if action.get("type") == "A":
        amount = int(payload.get("amount", 0))
        duration_months = payload.get("duration_months")
        duration_text = f" for the next {duration_months} months" if duration_months else ""
        return (
            f"Your {goal_name} goal is currently at risk. "
            f"GoalPilot selected Plan A from the intelligence score: save an extra {format_usd(amount)} per month"
            f"{duration_text}. Confirm this plan if you want me to apply it."
        )

    months = payload.get("months")
    new_target_date = payload.get("new_target_date")
    timing_bits: list[str] = []
    if months:
        timing_bits.append(f"extend the deadline by {months} months")
    if new_target_date:
        timing_bits.append(f"move the target date to {new_target_date}")
    timing_text = " and ".join(timing_bits) if timing_bits else "reduce the timeline pressure"
    return (
        f"Your {goal_name} goal is currently at risk. "
        f"GoalPilot selected Plan B from the intelligence score: {timing_text}. "
        "Confirm this plan if you want me to apply it."
    )


def _build_goal_context(goal: dict, strategy: str) -> dict[str, Any]:
    return {
        "goal_id": goal.get("goal_id"),
        "goal_name": goal.get("goal_name"),
        "goal_type": goal.get("goal_type"),
        "target_amount": goal.get("target_amount"),
        "target_date": goal.get("target_date"),
        "current_saved": goal.get("current_saved"),
        "status": goal.get("status"),
        "strategy": strategy,
    }


def _compose_chat_text(proposal: AtRiskProposalResponse) -> str:
    lines = [proposal.risk_summary.strip(), f"Plan A: {proposal.plan_a_reason.strip()}"]
    saving_tips = [tip.strip() for tip in proposal.plan_a_saving_tips if tip and tip.strip()]
    if saving_tips:
        lines.append("Saving ideas: " + "; ".join(saving_tips[:3]))
    lines.append(f"Plan B: {proposal.plan_b_reason.strip()}")
    return "\n\n".join(lines)


def build_at_risk_chat_proposal(
    goal: dict,
    user_context: dict,
    actions: list[dict],
    strategy: str,
) -> tuple[str, list[dict]]:
    strategy_actions = [action for action in actions if action.get("type") in {"A", "B"}]
    if len(strategy_actions) == 1:
        return _recommended_plan_text(goal, strategy_actions[0]), actions

    action_a = _find_action(actions, "A") or {}
    action_b = _find_action(actions, "B") or {}
    if not action_a and not action_b:
        return _fallback_chat_text(goal, actions), actions

    try:
        prompt = build_at_risk_chat_prompt(
            user_financial_context=user_context or {},
            goal_context=_build_goal_context(goal, strategy),
            plan_a_context=action_a.get("payload", {}),
            plan_b_context=action_b.get("payload", {}),
            risk_status=goal.get("status", strategy or "at_risk"),
        )
        response: AtRiskProposalResponse = get_completion(
            messages=[{"role": "system", "content": prompt}],
            response_format=AtRiskProposalResponse,
        )
        return _compose_chat_text(response), actions
    except Exception:
        return _fallback_chat_text(goal, actions), actions
