"""
goal_store.py - Goal data access layer backed by SQL Server.

Provides CRUD operations against the `goals` table and keeps runtime-only
progress fields that are not persisted in the current schema.
"""

import uuid

from data.db import execute_non_query, execute_query
from intelligence.intelligence import evaluate_user_context, map_strategy_to_goal_status

_goal_runtime_state: dict[str, dict] = {}


def _progress_percent(goal: dict) -> int:
    target_amount = float(goal.get("target_amount", 0))
    current_saved = float(goal.get("current_saved", 0))
    if target_amount <= 0:
        return 0
    return int(min(100, (current_saved / target_amount) * 100))


def _merge_runtime_state(goal: dict) -> dict:
    merged = dict(goal)
    runtime_state = _goal_runtime_state.get(goal["goal_id"], {})
    if runtime_state:
        merged.update(runtime_state)
    merged.setdefault("current_saved", 0.0)
    return merged


def list_goals() -> list[dict]:
    """Return all goals."""
    rows = execute_query("SELECT * FROM goals ORDER BY created_at DESC")
    return [_merge_runtime_state(row) for row in rows]


def get_goal(goal_id: str) -> dict | None:
    """Return a single goal by ID, or None."""
    rows = execute_query("SELECT * FROM goals WHERE goal_id = ?", (goal_id,))
    if not rows:
        return None
    return _merge_runtime_state(rows[0])


def create_goal(
    goal_name: str,
    goal_type: str,
    target_amount: float,
    target_date: str,
    currency: str = "USD",
    created_from: str | None = None,
) -> dict:
    """Insert a new goal and return its dict representation."""
    goal_id = f"g_{uuid.uuid4().hex[:8]}"
    execute_non_query(
        """
        INSERT INTO goals (goal_id, goal_name, goal_type, target_amount, target_date, currency, status, created_from)
        VALUES (?, ?, ?, ?, ?, ?, 'on_track', ?)
        """,
        (goal_id, goal_name, goal_type, float(target_amount), target_date, currency, created_from),
    )
    goal = {
        "goal_id": goal_id,
        "goal_name": goal_name,
        "goal_type": goal_type,
        "target_amount": float(target_amount),
        "target_date": target_date,
        "currency": currency,
        "created_from": created_from,
        "status": "on_track",
    }
    _goal_runtime_state[goal_id] = {"current_saved": 0.0, "status": "on_track"}
    return _merge_runtime_state(goal)


def update_goal_target_date(goal_id: str, target_date: str) -> int:
    """Update a goal target date without overriding intelligence status."""
    _goal_runtime_state.setdefault(goal_id, {})
    return execute_non_query(
        "UPDATE goals SET target_date = ? WHERE goal_id = ?",
        (target_date, goal_id),
    )


def get_goal_ids() -> list[str]:
    """Return all goal IDs."""
    rows = execute_query("SELECT goal_id FROM goals")
    return [row["goal_id"] for row in rows]


def sync_goals_with_user_context(user_context: dict) -> list[dict]:
    available_balance = max(0.0, float(user_context.get("balance", 0)))
    synced_goals: list[dict] = []
    strategy = evaluate_user_context(user_context).get("strategy", "None")

    for goal in list_goals():
        target_amount = max(0.0, float(goal.get("target_amount", 0)))
        allocated = min(target_amount, available_balance)
        available_balance = max(0.0, available_balance - allocated)

        runtime_goal = dict(goal)
        runtime_goal["current_saved"] = allocated
        runtime_goal["status"] = map_strategy_to_goal_status(
            strategy,
            progress_percent=_progress_percent(runtime_goal),
        )

        _goal_runtime_state[goal["goal_id"]] = {
            "current_saved": allocated,
            "status": runtime_goal["status"],
        }
        execute_non_query(
            "UPDATE goals SET status = ? WHERE goal_id = ?",
            (runtime_goal["status"], goal["goal_id"]),
        )
        synced_goals.append(runtime_goal)

    return synced_goals
