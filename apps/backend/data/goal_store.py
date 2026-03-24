"""
goal_store.py — Goal data access layer backed by SQL Server.

Provides CRUD operations against the `goals` table.
"""

import uuid

from data.db import execute_query, execute_non_query


def list_goals() -> list[dict]:
    """Return all goals."""
    rows = execute_query("SELECT * FROM goals ORDER BY created_at DESC")
    # Ensure current_saved is present (default 0) for API contract compatibility
    for row in rows:
        row.setdefault("current_saved", 0.0)
    return rows


def get_goal(goal_id: str) -> dict | None:
    """Return a single goal by ID, or None."""
    rows = execute_query("SELECT * FROM goals WHERE goal_id = ?", (goal_id,))
    if not rows:
        return None
    goal = rows[0]
    goal.setdefault("current_saved", 0.0)
    return goal


def create_goal(
    goal_name: str,
    goal_type: str,
    target_amount: float,
    target_date: str,
    currency: str = "VND",
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
    return {
        "goal_id": goal_id,
        "goal_name": goal_name,
        "goal_type": goal_type,
        "target_amount": float(target_amount),
        "target_date": target_date,
        "currency": currency,
        "created_from": created_from,
        "current_saved": 0.0,
        "status": "on_track",
    }


def get_goal_ids() -> list[str]:
    """Return all goal IDs."""
    rows = execute_query("SELECT goal_id FROM goals")
    return [row["goal_id"] for row in rows]
