"""
chat_state_store.py - Lightweight per-session chat state persisted as JSON.
"""

from __future__ import annotations

import json

from data.db import execute_non_query, execute_query


def get_session_state(session_id: str) -> dict | None:
    rows = execute_query(
        "SELECT state_json FROM chat_session_state WHERE session_id = ?",
        (session_id,),
    )
    if not rows:
        return None

    raw_state = rows[0].get("state_json")
    if not raw_state:
        return None

    try:
        return json.loads(raw_state)
    except (TypeError, json.JSONDecodeError):
        return None


def set_session_state(session_id: str, state: dict) -> None:
    state_json = json.dumps(state)
    updated = execute_non_query(
        """
        UPDATE chat_session_state
        SET state_json = ?, updated_at = GETDATE()
        WHERE session_id = ?
        """,
        (state_json, session_id),
    )
    if updated == 0:
        execute_non_query(
            """
            INSERT INTO chat_session_state (session_id, state_json)
            VALUES (?, ?)
            """,
            (session_id, state_json),
        )


def clear_session_state(session_id: str) -> None:
    execute_non_query(
        "DELETE FROM chat_session_state WHERE session_id = ?",
        (session_id,),
    )
