"""
goal_action_store.py - Persistent accepted-plan state per goal.
"""

import json

from data.db import execute_non_query, execute_query


def get_goal_action_state(goal_id: str) -> dict | None:
    rows = execute_query(
        """
        SELECT goal_id, action_type, strategy, payload_json, updated_at
        FROM goal_action_state
        WHERE goal_id = ?
        """,
        (goal_id,),
    )
    if not rows:
        return None

    row = dict(rows[0])
    payload = row.get("payload_json")
    if isinstance(payload, str):
        try:
            row["payload"] = json.loads(payload)
        except json.JSONDecodeError:
            row["payload"] = {}
    else:
        row["payload"] = payload or {}
    row.pop("payload_json", None)
    return row


def upsert_goal_action_state(goal_id: str, action_type: str, strategy: str, payload: dict) -> dict:
    payload_json = json.dumps(payload)

    updated = execute_non_query(
        """
        UPDATE goal_action_state
        SET action_type = ?, strategy = ?, payload_json = ?, updated_at = GETDATE()
        WHERE goal_id = ?
        """,
        (action_type, strategy, payload_json, goal_id),
    )
    if updated == 0:
        execute_non_query(
            """
            INSERT INTO goal_action_state (goal_id, action_type, strategy, payload_json)
            VALUES (?, ?, ?, ?)
            """,
            (goal_id, action_type, strategy, payload_json),
        )

    return {
        "goal_id": goal_id,
        "action_type": action_type,
        "strategy": strategy,
        "payload": payload,
    }
