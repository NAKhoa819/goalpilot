"""
router_chat.py - Chat endpoints

POST /api/chat/message
GET  /api/chat/session/{session_id}
"""

import re
import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from api.chat_seed import ensure_chat_seed
from intelligence.intelligence import calculate_metrics, determine_strategy
from intelligence.llm_gateway import build_fallback_chat_advice, get_chat_advice
from memory.history import ConversationHistory
from memory.retriever import ContextRetriever

router = APIRouter()


class ChatContext(BaseModel):
    model_config = ConfigDict(extra="allow")

    active_goal_id: Optional[str] = None
    source_screen: Optional[str] = None


class PostChatMessageRequest(BaseModel):
    session_id: str
    message: str
    context: Optional[ChatContext] = None


def _error(message: str, error_code: str, status_code: int = 400):
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "message": message, "error_code": error_code},
    )


def _build_actions_from_strategy(strategy: str) -> list:
    if strategy == "None":
        return []

    return [
        {
            "type": "A",
            "label": "Plan A - Tang tiet kiem hang thang",
            "payload": {
                "strategy": "increase_savings",
                "amount": 2_000_000,
                "duration_months": 6,
            },
        },
        {
            "type": "B",
            "label": "Plan B - Gia han deadline",
            "payload": {
                "strategy": "extend_deadline",
                "months": 3,
            },
        },
    ]


def _extract_amount(text: str) -> Optional[int]:
    lowered = text.lower()

    million_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(trieu|triệu|tr)\b", lowered)
    if million_match:
        value = float(million_match.group(1).replace(",", "."))
        return int(value * 1_000_000)

    raw_match = re.search(r"\b(\d{1,3}(?:[.,]\d{3})+|\d{6,})\b", lowered)
    if raw_match:
        raw_value = re.sub(r"[.,]", "", raw_match.group(1))
        return int(raw_value)

    return None


def _extract_target_date(text: str) -> str:
    explicit_date = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
    if explicit_date:
        return explicit_date.group(1)

    months_match = re.search(r"(\d+)\s*th[aá]ng", text.lower())
    months = int(months_match.group(1)) if months_match else 8
    return (datetime.today() + timedelta(days=months * 30)).strftime("%Y-%m-%d")


def _infer_goal_name_and_type(text: str) -> tuple[str, str]:
    lowered = text.lower()

    if "laptop" in lowered:
        return "Buy Laptop", "purchase"
    if any(keyword in lowered for keyword in ("o to", "ô tô", "xe hoi", "xe hơi")):
        return "Buy Car", "purchase"
    if any(keyword in lowered for keyword in ("emergency fund", "quy khan cap", "quỹ khẩn cấp")):
        return "Emergency Fund", "emergency_fund"
    if any(keyword in lowered for keyword in ("du lich", "du lịch", "travel")):
        return "Travel Goal", "saving"

    purchase_match = re.search(
        r"mua\s+(.+?)(?:\s+gia|\s+giá|\s+\d|\s+trong\s+\d+\s*th[aá]ng|$)",
        lowered,
    )
    if purchase_match:
        subject = purchase_match.group(1).strip(" .,!?")
        if subject:
            return f"Buy {subject.title()}", "purchase"

    return "New Goal", "custom"


def _detect_create_goal_action(user_text: str) -> Optional[dict]:
    lowered = user_text.lower()
    if not any(keyword in lowered for keyword in (
        "mua",
        "goal",
        "muc tieu",
        "mục tiêu",
        "tiet kiem",
        "tiết kiệm",
        "quy khan cap",
        "quỹ khẩn cấp",
        "travel",
        "du lich",
        "du lịch",
    )):
        return None

    amount = _extract_amount(user_text)
    if amount is None:
        return None

    goal_name, goal_type = _infer_goal_name_and_type(user_text)
    return {
        "type": "create_goal",
        "label": "Create Goal",
        "payload": {
            "goal_name": goal_name,
            "goal_type": goal_type,
            "target_amount": amount,
            "target_date": _extract_target_date(user_text),
        },
    }


def _build_goal_acknowledgement(context: ChatContext | None) -> str:
    payload = context.model_dump() if context else {}
    goal_name = payload.get("goal_name") or "your goal"
    target_amount = payload.get("target_amount")
    target_date = payload.get("target_date")

    details = []
    if target_amount:
        details.append(f"target amount {target_amount:,} VND")
    if target_date:
        details.append(f"target date {target_date}")

    suffix = f" with {', '.join(details)}" if details else ""
    return f"I have created {goal_name}{suffix}. You can review it from the dashboard."


def _build_plan_acknowledgement(context: ChatContext | None) -> str:
    payload = context.model_dump() if context else {}
    strategy = payload.get("strategy")

    if strategy == "increase_savings":
        amount = payload.get("amount")
        duration = payload.get("duration_months")
        details = []
        if amount:
            details.append(f"save an extra {amount:,} VND per month")
        if duration:
            details.append(f"for the next {duration} months")
        suffix = f" by {' '.join(details)}" if details else ""
        return f"Plan A selected. I will guide you{suffix} to recover the goal timeline."

    if strategy == "extend_deadline":
        months = payload.get("months")
        new_target_date = payload.get("new_target_date")
        details = []
        if months:
            details.append(f"extend the deadline by {months} months")
        if new_target_date:
            details.append(f"toward {new_target_date}")
        suffix = f" to {' and '.join(details)}" if details else ""
        return f"Plan B selected. I will guide you{suffix} so the goal remains achievable."

    return "I noted your plan adjustment choice. You can keep reviewing it in the dashboard."


@router.post("/chat/message")
def post_chat_message(body: PostChatMessageRequest):
    if not body.message or not body.message.strip():
        return _error("Message cannot be empty.", "EMPTY_MESSAGE")

    session_id = body.session_id
    user_text = body.message.strip()
    history = ConversationHistory(session_id)

    retriever = ContextRetriever()
    user_context = retriever.fetch_user_financial_context(user_id="user_123")

    try:
        metrics = calculate_metrics(user_context)
        s_i = metrics["s_i"]
        strategy = determine_strategy(s_i)
    except Exception as exc:
        return _error(f"Intelligence engine error: {exc}", "AGENT_PROCESSING_FAILED", 500)

    actions: list = []
    source_screen = body.context.source_screen if body.context else None

    if user_text.lower() == "create goal" and source_screen == "agent_action":
        reply_text = _build_goal_acknowledgement(body.context)
    elif source_screen == "agent_action" and body.context:
        context_payload = body.context.model_dump()
        if context_payload.get("strategy") in {"increase_savings", "extend_deadline"}:
            reply_text = _build_plan_acknowledgement(body.context)
        else:
            reply_text = "I noted your action. Let me know if you want to refine the plan further."
    else:
        create_goal_action = _detect_create_goal_action(user_text)
        if create_goal_action:
            actions = [create_goal_action]
            reply_text = (
                "I understood the financial goal you described. "
                "If this looks right, tap Create Goal and I will save it for you."
            )
        else:
            try:
                reply_text = get_chat_advice(user_query=user_text, s_i=s_i)
            except Exception:
                reply_text = build_fallback_chat_advice(user_query=user_text, s_i=s_i)
            actions = _build_actions_from_strategy(strategy)

    user_msg_id = f"u_{uuid.uuid4().hex[:8]}"
    assistant_msg_id = f"a_{uuid.uuid4().hex[:8]}"

    history.add_message("user", user_text, message_id=user_msg_id)
    history.add_message(
        "assistant",
        reply_text,
        actions=actions if actions else None,
        message_id=assistant_msg_id,
    )

    reply_obj = {
        "message_id": assistant_msg_id,
        "role": "assistant",
        "text": reply_text,
    }
    if actions:
        reply_obj["actions"] = actions

    return {
        "success": True,
        "data": {
            "session_id": session_id,
            "reply": reply_obj,
        },
    }


@router.get("/chat/session/{session_id}")
def get_chat_session(session_id: str):
    ensure_chat_seed(session_id)

    history = ConversationHistory(session_id)
    raw_messages = history.get_all_messages()

    messages = []
    for i, message in enumerate(raw_messages):
        item: dict = {
            "message_id": message.get("message_id", f"m_{i:04d}"),
            "role": message["role"],
            "text": message["content"],
        }
        if message.get("actions"):
            item["actions"] = message["actions"]
        messages.append(item)

    return {
        "success": True,
        "data": {
            "session_id": session_id,
            "messages": messages,
        },
    }
