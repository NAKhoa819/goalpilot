from datetime import datetime, timedelta

from data.goal_store import list_goals
from memory.history import ConversationHistory


def _has_replan_actions(message: dict) -> bool:
    actions = message.get("actions") or []
    action_types = {action.get("type") for action in actions}
    return "A" in action_types and "B" in action_types


def _pick_at_risk_goal() -> dict | None:
    goals = list_goals()
    for goal in goals:
        if goal.get("status") == "at_risk":
            return goal
    return goals[0] if goals else None


def _extend_target_date(target_date: str, months: int) -> str:
    try:
        current = datetime.strptime(target_date, "%Y-%m-%d")
        return (current + timedelta(days=months * 30)).strftime("%Y-%m-%d")
    except Exception:
        return target_date


def _build_replan_actions(goal: dict) -> list[dict]:
    target_amount = float(goal.get("target_amount", 0))
    current_saved = float(goal.get("current_saved", 0))
    remaining = max(0, target_amount - current_saved)
    plan_a_amount = max(500_000, int(remaining / 6)) if remaining else 500_000
    plan_b_months = 2
    goal_id = goal.get("goal_id", "")

    return [
        {
            "type": "A",
            "label": f"Plan A - Tang them {plan_a_amount:,} VND/thang",
            "payload": {
                "goal_id": goal_id,
                "strategy": "increase_savings",
                "amount": plan_a_amount,
                "duration_months": 6,
            },
        },
        {
            "type": "B",
            "label": f"Plan B - Doi deadline them {plan_b_months} thang",
            "payload": {
                "goal_id": goal_id,
                "strategy": "extend_deadline",
                "months": plan_b_months,
                "new_target_date": _extend_target_date(
                    goal.get("target_date", "2026-12-01"),
                    plan_b_months,
                ),
            },
        },
    ]


def _build_replan_message(goal: dict) -> str:
    goal_name = goal.get("goal_name", "your goal")
    return (
        f"Your {goal_name} goal is currently off track. "
        "Choose how you want to adjust the plan."
    )


def ensure_chat_seed(session_id: str) -> None:
    ConversationHistory.ensure_session(session_id, seed_welcome=False)
    history = ConversationHistory(session_id)
    messages = history.get_all_messages()

    if any(_has_replan_actions(message) for message in messages):
        return

    at_risk_goal = _pick_at_risk_goal()
    if at_risk_goal and at_risk_goal.get("status") == "at_risk":
        history.add_message(
            "assistant",
            _build_replan_message(at_risk_goal),
            actions=_build_replan_actions(at_risk_goal),
            message_id=f"m_replan_{at_risk_goal.get('goal_id', 'seed')}",
        )
        return

    if not messages:
        history.add_message(
            "assistant",
            "How can I help with your financial goals today?",
            message_id="m_welcome",
        )
