"""
router_dashboard.py - Dashboard endpoint

GET /api/dashboard
"""

from fastapi import APIRouter

from api.chat_seed import ensure_chat_seed
from data.goal_store import list_goals, sync_goals_with_user_context
from memory.history import ConversationHistory
from memory.retriever import ContextRetriever

router = APIRouter()


@router.get("/dashboard")
def get_dashboard():
    ensure_chat_seed("s001")
    user_context = ContextRetriever().fetch_user_financial_context(user_id="user_123")
    sync_goals_with_user_context(user_context)
    history = ConversationHistory("s001")
    messages = history.get_all_messages()

    goal_cards = []
    for goal in list_goals():
        target = float(goal.get("target_amount", 0))
        current = float(goal.get("current_saved", 0))
        pct = int(min(100, (current / target * 100) if target > 0 else 0))
        status = goal.get("status") or ("on_track" if pct >= 60 else "at_risk")

        goal_cards.append({
            "goal_id": goal["goal_id"],
            "goal_name": goal.get("goal_name", "Goal"),
            "target_amount": target,
            "target_date": goal.get("target_date", "2026-12-01"),
            "current_saved": current,
            "progress_percent": pct,
            "status": status,
        })

    active_goal_id = goal_cards[0]["goal_id"] if goal_cards else None
    last_message = messages[-1]["content"] if messages else "How can I help with your financial goals today?"
    last_actions = messages[-1].get("actions", []) if messages else []
    unread_count = 1 if any(
        action.get("type") == "accept"
        or action.get("type") in {"A", "B"}
        for action in last_actions
    ) else 0

    return {
        "success": True,
        "data": {
            "goals": goal_cards,
            "active_goal_id": active_goal_id,
            "chat_preview": {
                "session_id": "s001",
                "last_message": last_message,
                "unread_count": unread_count,
            },
            "input_actions": [
                {"type": "manual_input", "label": "Enter Data"},
                {"type": "ocr_upload", "label": "Scan Receipt"},
            ],
        },
    }
