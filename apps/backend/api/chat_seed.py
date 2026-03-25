import uuid

from data.goal_store import list_goals, sync_goals_with_user_context
from intelligence.at_risk_guidance import build_at_risk_chat_proposal
from intelligence.intelligence import evaluate_user_context
from intelligence.strategy_actions import build_confirmation_actions, build_recommended_action
from config.settings import resolve_force_strategy
from memory.history import ConversationHistory, _welcome_message_id
from memory.retriever import ContextRetriever


def _extract_replan_action_type(message: dict) -> str | None:
    actions = message.get("actions") or []
    for action in actions:
        if action.get("type") in {"A", "B"}:
            return action.get("type")
        if action.get("type") in {"accept", "cancel"} and (action.get("payload") or {}).get("action_type") in {"A", "B"}:
            return (action.get("payload") or {}).get("action_type")
    return None


def _has_replan_actions(message: dict) -> bool:
    return _extract_replan_action_type(message) is not None


def _latest_replan_action_type(messages: list[dict]) -> str | None:
    for message in reversed(messages):
        action_type = _extract_replan_action_type(message)
        if action_type is not None:
            return action_type
    return None


def _pick_at_risk_goal() -> dict | None:
    goals = list_goals()
    for goal in goals:
        if goal.get("status") == "at_risk":
            return goal
    return goals[0] if goals else None

def ensure_chat_seed(session_id: str) -> None:
    ConversationHistory.ensure_session(session_id, seed_welcome=False)
    history = ConversationHistory(session_id)
    messages = history.get_all_messages()
    forced_strategy = resolve_force_strategy()

    if forced_strategy is None and any(_has_replan_actions(message) for message in messages):
        return

    user_context: dict = {}
    try:
        user_context = ContextRetriever().fetch_user_financial_context(user_id="user_123")
        sync_goals_with_user_context(user_context)
    except Exception:
        user_context = {}

    at_risk_goal = _pick_at_risk_goal()
    strategy = evaluate_user_context(user_context).get("strategy", "None")
    latest_action_type = _latest_replan_action_type(messages)

    if at_risk_goal and at_risk_goal.get("status") == "at_risk":
        if strategy not in {"A", "B"}:
            return
        if latest_action_type == strategy:
            return

        recommended_action = build_recommended_action(at_risk_goal, strategy)
        if recommended_action is None:
            return

        reply_text, _ = build_at_risk_chat_proposal(
            at_risk_goal,
            user_context,
            [recommended_action],
            strategy=strategy,
        )
        actions = build_confirmation_actions(recommended_action)
        history.add_message(
            "assistant",
            reply_text,
            actions=actions,
            message_id=f"m_replan_{at_risk_goal.get('goal_id', 'seed')}_{strategy}_{uuid.uuid4().hex[:6]}",
        )
        return

    if not messages:
        history.add_message(
            "assistant",
            "How can I help with your financial goals today?",
            message_id=_welcome_message_id(session_id),
        )
