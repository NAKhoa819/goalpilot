from __future__ import annotations

from datetime import datetime, timedelta


def extend_target_date(target_date: str, months: int) -> str:
    try:
        current = datetime.strptime(target_date, "%Y-%m-%d")
        return (current + timedelta(days=months * 30)).strftime("%Y-%m-%d")
    except Exception:
        return target_date


def build_recommended_action(goal: dict | None, strategy: str) -> dict | None:
    if goal is None or strategy not in {"A", "B"}:
        return None

    goal_id = goal.get("goal_id")
    if not goal_id:
        return None

    target_amount = float(goal.get("target_amount", 0))
    current_saved = float(goal.get("current_saved", 0))
    remaining = max(0, target_amount - current_saved)

    if strategy == "A":
        extra_per_month = max(500_000, int(remaining / 6)) if remaining else 500_000
        return {
            "type": "A",
            "label": f"Plan A - Save an extra {extra_per_month:,} VND/month",
            "payload": {
                "goal_id": goal_id,
                "strategy": "increase_savings",
                "amount": extra_per_month,
                "duration_months": 6,
            },
        }

    delay_months = 3
    new_target_date = extend_target_date(goal.get("target_date", "2026-12-01"), delay_months)
    return {
        "type": "B",
        "label": f"Plan B - Extend deadline by {delay_months} months",
        "payload": {
            "goal_id": goal_id,
            "strategy": "extend_deadline",
            "months": delay_months,
            "new_target_date": new_target_date,
        },
    }


def build_confirmation_actions(recommended_action: dict | None) -> list[dict]:
    if not recommended_action:
        return []

    payload = recommended_action.get("payload", {})
    goal_id = payload.get("goal_id")
    if not goal_id:
        return []

    return [
        {
            "type": "accept",
            "label": "Apply Recommended Plan",
            "payload": {
                "goal_id": goal_id,
                "action": "confirm_recommended_plan",
                "action_type": recommended_action["type"],
                "action_label": recommended_action.get("label"),
                "action_payload": payload,
            },
        },
        {
            "type": "cancel",
            "label": "Keep Current Goal",
            "payload": {
                "goal_id": goal_id,
                "action": "keep_current_plan",
                "action_type": recommended_action["type"],
            },
        },
    ]
