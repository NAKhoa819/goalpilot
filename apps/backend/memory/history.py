"""
history.py — Conversation history backed by SQL Server.

Uses the `chat_sessions` and `messages` tables.
"""

import json
import uuid
from typing import Optional

from data.db import execute_query, execute_non_query


def _welcome_message_id(session_id: str) -> str:
    return f"m_welcome_{session_id}"


def _ensure_session_row(session_id: str) -> None:
    execute_non_query(
        """
        IF NOT EXISTS (SELECT 1 FROM chat_sessions WHERE session_id = ?)
        BEGIN
            INSERT INTO chat_sessions (session_id) VALUES (?)
        END
        """,
        (session_id, session_id),
    )


class ConversationHistory:
    """
    Manages conversation history per session_id.
    Each message: { "role": "user"|"assistant", "content": str, "actions": list|None }
    """

    def __init__(self, session_id: str):
        self.session_id = session_id
        # Auto-create session if it doesn't exist.
        _ensure_session_row(session_id)

    # ------------------------------------------------------------------
    # Static helpers
    # ------------------------------------------------------------------
    @staticmethod
    def session_exists(session_id: str) -> bool:
        """Returns True if session has been previously created."""
        rows = execute_query(
            "SELECT 1 AS exists_flag FROM chat_sessions WHERE session_id = ?",
            (session_id,),
        )
        return len(rows) > 0

    @staticmethod
    def ensure_session(session_id: str, seed_welcome: bool = False) -> None:
        """Creates a session if it does not exist."""
        _ensure_session_row(session_id)

        if seed_welcome:
            # Check if session has any messages
            rows = execute_query(
                "SELECT TOP 1 message_id FROM messages WHERE session_id = ?",
                (session_id,),
            )
            if not rows:
                msg_id = _welcome_message_id(session_id)
                execute_non_query(
                    """
                    INSERT INTO messages (message_id, session_id, role, text)
                    VALUES (?, ?, 'assistant', 'How can I help with your financial goals today?')
                    """,
                    (msg_id, session_id),
                )

    # ------------------------------------------------------------------
    # Instance methods
    # ------------------------------------------------------------------
    def add_message(
        self,
        role: str,
        content: str,
        actions: Optional[list] = None,
        message_id: Optional[str] = None,
    ) -> None:
        """Appends a message to this session's history."""
        if message_id is None:
            message_id = f"m_{uuid.uuid4().hex[:8]}"

        actions_json = json.dumps(actions) if actions else None

        execute_non_query(
            """
            INSERT INTO messages (message_id, session_id, role, text, actions)
            VALUES (?, ?, ?, ?, ?)
            """,
            (message_id, self.session_id, role, content, actions_json),
        )

    def get_last_n_messages(self, n: int) -> list:
        """Returns last N messages (for LLM context window)."""
        rows = execute_query(
            """
            SELECT TOP (?) message_id, role, text, actions, created_at
            FROM messages
            WHERE session_id = ?
            ORDER BY created_at DESC
            """,
            (n, self.session_id),
        )
        # Reverse so oldest first
        rows.reverse()
        return [self._row_to_message(row) for row in rows]

    def get_all_messages(self) -> list:
        """Returns all messages in this session (for GET /api/chat/session)."""
        rows = execute_query(
            """
            SELECT message_id, role, text, actions, created_at
            FROM messages
            WHERE session_id = ?
            ORDER BY created_at ASC
            """,
            (self.session_id,),
        )
        return [self._row_to_message(row) for row in rows]

    @staticmethod
    def _row_to_message(row: dict) -> dict:
        """Convert a DB row to the message dict format expected by routers."""
        msg: dict = {
            "role": row["role"],
            "content": row["text"],
        }
        if row.get("message_id"):
            msg["message_id"] = row["message_id"]
        if row.get("actions"):
            try:
                msg["actions"] = json.loads(row["actions"]) if isinstance(row["actions"], str) else row["actions"]
            except (json.JSONDecodeError, TypeError):
                pass
        return msg
