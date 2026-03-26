"""
router_chat.py - Chat endpoints

POST /api/chat/message
GET  /api/chat/session/{session_id}
"""

import re
import unicodedata
import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from api.chat_seed import ensure_chat_seed
from data.chat_state_store import clear_session_state, get_session_state, set_session_state
from data.goal_store import get_goal, list_goals, sync_goals_with_user_context
from intelligence.at_risk_guidance import build_at_risk_chat_proposal
from intelligence.intelligence import evaluate_user_context
from intelligence.llm_gateway import build_fallback_chat_advice, get_chat_advice, get_completion
from intelligence.market_prediction import PredictionError, predict_car_price
from intelligence.strategy_actions import build_confirmation_actions, build_recommended_action
from memory.history import ConversationHistory
from memory.retriever import ContextRetriever
from models.schemas import CarGoalIntentResponse, CarPricePredictionRequest

router = APIRouter()

CAR_GOAL_REQUIRED_FIELDS = (
    "Present_Price",
    "Kms_Driven",
    "Fuel_Type",
    "Seller_Type",
    "Transmission",
    "Owner",
    "Year",
)

CAR_GOAL_QUESTIONS = {
    "Present_Price": "What price range are you targeting for the car?",
    "Kms_Driven": "About how many kilometers has the car been driven?",
    "Fuel_Type": "What fuel type does it use: petrol, diesel, or CNG?",
    "Seller_Type": "Are you buying from a dealer or an individual seller?",
    "Transmission": "Is it a manual or automatic transmission?",
    "Owner": "How many previous owners has the car had?",
    "Year": "What model year is the car?",
}

CAR_GOAL_FIELD_LABELS = {
    "Present_Price": "car price",
    "Kms_Driven": "distance driven",
    "Fuel_Type": "fuel type",
    "Seller_Type": "seller type",
    "Transmission": "transmission type",
    "Owner": "number of previous owners",
    "Year": "model year",
}


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


def _resolve_goal_for_strategy(active_goal_id: str | None) -> dict | None:
    if active_goal_id:
        active_goal = get_goal(active_goal_id)
        if active_goal is not None:
            return active_goal

    goals = list_goals()
    for goal in goals:
        if goal.get("status") == "at_risk":
            return goal
    return goals[0] if goals else None


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text or "")
    normalized = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    normalized = normalized.replace("\u0111", "d").replace("\u0110", "d")
    normalized = normalized.lower()
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def _extract_amount(text: str) -> Optional[int]:
    lowered = _normalize_text(text)

    billion_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(ty|ti|billion|bil)\b", lowered)
    if billion_match:
        value = float(billion_match.group(1).replace(",", "."))
        return int(value * 1_000_000_000)

    colloquial_million_match = re.search(r"(\d+(?:[.,]\d+)?)\s*cu\b", lowered)
    if colloquial_million_match:
        value = float(colloquial_million_match.group(1).replace(",", "."))
        return int(value * 1_000_000)

    million_match = re.search(r"(\d+(?:[.,]\d+)?)\s*(trieu|tr|million|mil)\b", lowered)
    if million_match:
        value = float(million_match.group(1).replace(",", "."))
        return int(value * 1_000_000)

    raw_match = re.search(r"\b(\d{1,3}(?:[.,]\d{3})+|\d{6,})\b", lowered)
    if raw_match:
        raw_value = re.sub(r"[.,]", "", raw_match.group(1))
        return int(raw_value)

    return None


def _extract_decimal_number(text: str) -> Optional[float]:
    match = re.search(r"(-?\d[\d.,]*)", text)
    if not match:
        return None

    token = match.group(1).strip()
    if "," in token and "." in token:
        token = token.replace(",", "")
    elif "," in token:
        parts = token.split(",")
        if len(parts[-1]) == 3 and all(part.isdigit() for part in parts):
            token = "".join(parts)
        else:
            token = token.replace(",", ".")
    elif "." in token:
        parts = token.split(".")
        if len(parts[-1]) == 3 and all(part.isdigit() for part in parts):
            token = "".join(parts)

    try:
        return float(token)
    except ValueError:
        return None


def _detect_car_goal_intent(user_text: str) -> bool:
    lowered = _normalize_text(user_text)
    if "car" in lowered and any(keyword in lowered for keyword in ("buy", "purchase", "goal", "create", "add")):
        return True
    return any(
        keyword in lowered
        for keyword in (
            "mua xe",
            "mua o to",
            "mua oto",
            "xe hoi",
            "buy car",
            "buy a car",
            "purchase car",
            "purchase a car",
            "car goal",
        )
    )


def _has_car_goal_creation_signal(user_text: str) -> bool:
    lowered = _normalize_text(user_text)
    car_terms = ("car", "oto", "o to", "xe", "xe hoi")
    goal_terms = ("buy", "purchase", "goal", "create", "add", "mua", "muc tieu")
    return any(term in lowered for term in car_terms) and any(term in lowered for term in goal_terms)


def _detect_car_goal_intent_with_llm(user_text: str) -> bool:
    prompt = (
        "Classify whether the user is asking to create, add, or start a savings/purchase goal for buying a car. "
        "Return true only when the user clearly means a goal to buy a car, even if amount or deadline is missing. "
        "Do not mark true for generic car discussion, maintenance, insurance, or market-price questions."
    )
    try:
        result: CarGoalIntentResponse = get_completion(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_text},
            ],
            response_format=CarGoalIntentResponse,
        )
        return bool(result.is_car_purchase_goal and result.confidence_score >= 0.5)
    except Exception:
        return False


def _is_cancel_intent(user_text: str) -> bool:
    lowered = _normalize_text(user_text)
    return lowered in {"huy", "thoi", "cancel", "stop", "never mind", "nevermind"}


def _build_car_goal_draft(user_text: str) -> dict:
    goal_name, _ = _infer_goal_name_and_type(user_text)
    return {
        "flow_type": "car_goal_creation",
        "goal_name": goal_name if goal_name != "New Goal" else "Buy Car",
        "goal_type": "purchase",
        "target_date": _extract_target_date(user_text),
        "features": {},
        "pending_field": CAR_GOAL_REQUIRED_FIELDS[0],
    }


def _get_next_car_field(features: dict) -> Optional[str]:
    for field in CAR_GOAL_REQUIRED_FIELDS:
        if field not in features:
            return field
    return None


def _parse_car_field_value(field_name: str, user_text: str):
    lowered = _normalize_text(user_text)

    if field_name == "Fuel_Type":
        mapping = {
            "petrol": "Petrol",
            "gas": "Petrol",
            "gasoline": "Petrol",
            "xang": "Petrol",
            "diesel": "Diesel",
            "dau": "Diesel",
            "dau diesel": "Diesel",
            "cng": "CNG",
        }
        if lowered in mapping:
            return mapping[lowered]
        raise ValueError("I could not determine the fuel type. Please choose petrol, diesel, or CNG.")

    if field_name == "Seller_Type":
        mapping = {
            "dealer": "Dealer",
            "dai ly": "Dealer",
            "individual": "Individual",
            "private": "Individual",
            "private seller": "Individual",
            "ca nhan": "Individual",
        }
        if lowered in mapping:
            return mapping[lowered]
        raise ValueError("I could not determine whether the seller is a dealer or an individual.")

    if field_name == "Transmission":
        mapping = {
            "manual": "Manual",
            "manual transmission": "Manual",
            "stick": "Manual",
            "so san": "Manual",
            "san": "Manual",
            "automatic": "Automatic",
            "automatic transmission": "Automatic",
            "auto": "Automatic",
            "tu dong": "Automatic",
            "so tu dong": "Automatic",
        }
        if lowered in mapping:
            return mapping[lowered]
        raise ValueError("I could not determine the transmission. Please answer manual or automatic.")

    if field_name == "Year":
        match = re.search(r"\b(19\d{2}|20\d{2})\b", user_text)
        if match:
            return int(match.group(1))
        raise ValueError("I could not read the model year. Example: 2022.")

    number = _extract_decimal_number(user_text)
    if number is None:
        label = CAR_GOAL_FIELD_LABELS[field_name]
        raise ValueError(f"I could not read the {label} from your reply.")

    if field_name == "Owner":
        if number < 0 or int(number) != number:
            raise ValueError("The number of previous owners must be a non-negative integer.")
        return int(number)

    if number < 0:
        label = CAR_GOAL_FIELD_LABELS[field_name]
        raise ValueError(f"The {label} must be a non-negative number.")

    return number


def _build_car_question(field_name: str) -> str:
    return CAR_GOAL_QUESTIONS[field_name]


def _build_missing_deadline_question(goal_name: str) -> str:
    return (
        f"I understand the goal {goal_name}. "
        "When do you want to complete it? "
        "For example: 2026-12-31 or in 8 months."
    )


def _build_car_goal_clarification(goal_name: str) -> str:
    return (
        f"If you want to create the goal {goal_name}, I can help with that. "
        "Tell me the deadline first, for example 2026-12-31 or in 8 months."
    )


def _build_create_goal_action(payload: dict) -> dict:
    return {
        "type": "create_goal",
        "label": "Create Goal",
        "payload": {
            "goal_name": payload["goal_name"],
            "goal_type": payload["goal_type"],
            "target_amount": payload["target_amount"],
            "target_date": payload["target_date"],
        },
    }


def _build_car_goal_action(draft: dict, predicted_price: float) -> dict:
    return _build_create_goal_action(
        {
            "goal_name": draft.get("goal_name") or "Buy Car",
            "goal_type": draft.get("goal_type") or "purchase",
            "target_amount": int(round(predicted_price)),
            "target_date": draft["target_date"],
        }
    )


def _complete_car_goal_flow(session_id: str, draft: dict) -> tuple[str, list]:
    body = CarPricePredictionRequest(**draft["features"])
    prediction = predict_car_price(body)
    clear_session_state(session_id)

    action = _build_car_goal_action(draft, prediction.predicted_price)
    target_amount = action["payload"]["target_amount"]
    target_date = action["payload"]["target_date"]

    reply_text = (
        f"I estimate the car price at about {target_amount:,} VND. "
        f"If that looks right, tap Create Goal to save the goal with target date {target_date}."
    )
    return reply_text, [action]


def _car_prediction_unavailable_message() -> str:
    return (
        "I collected the required car details, but the price prediction model is not available right now. "
        "Please check the SageMaker configuration or enter the target amount directly in chat."
    )


def _handle_active_car_goal_draft(session_id: str, user_text: str, draft: dict) -> tuple[str, list]:
    if _is_cancel_intent(user_text):
        clear_session_state(session_id)
        return "I canceled the car goal creation flow. Start again whenever you are ready.", []

    if not draft.get("target_date"):
        target_date = _extract_target_date(user_text)
        if target_date is None:
            return _build_missing_deadline_question(draft.get("goal_name") or "Buy Car"), []

        draft["target_date"] = target_date
        set_session_state(session_id, draft)
        return _build_car_question(draft["pending_field"]), []

    pending_field = draft.get("pending_field") or _get_next_car_field(draft.get("features", {}))
    if pending_field is None:
        try:
            return _complete_car_goal_flow(session_id, draft)
        except PredictionError:
            clear_session_state(session_id)
            return _car_prediction_unavailable_message(), []

    try:
        parsed_value = _parse_car_field_value(pending_field, user_text)
    except ValueError as exc:
        return f"{exc} {_build_car_question(pending_field)}", []

    features = dict(draft.get("features", {}))
    features[pending_field] = parsed_value
    draft["features"] = features
    next_field = _get_next_car_field(features)
    draft["pending_field"] = next_field

    if next_field is None:
        try:
            return _complete_car_goal_flow(session_id, draft)
        except PredictionError:
            clear_session_state(session_id)
            return _car_prediction_unavailable_message(), []

    set_session_state(session_id, draft)
    return _build_car_question(next_field), []


def _extract_target_date(text: str) -> Optional[str]:
    explicit_date = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
    if explicit_date:
        return explicit_date.group(1)

    normalized_text = _normalize_text(text)
    months_match = re.search(r"(\d+)\s*(thang|month|months)\b", normalized_text)
    if months_match:
        months = int(months_match.group(1))
        return (datetime.today() + timedelta(days=months * 30)).strftime("%Y-%m-%d")

    return None


def _infer_goal_name_and_type(text: str) -> tuple[str, str]:
    lowered = _normalize_text(text)

    if "laptop" in lowered:
        return "Buy Laptop", "purchase"
    if any(keyword in lowered for keyword in ("mua xe", "o to", "oto", "xe hoi", "buy car", "buy a car", "purchase car")):
        return "Buy Car", "purchase"
    if "car" in lowered and any(keyword in lowered for keyword in ("buy", "purchase", "goal", "create", "add")):
        return "Buy Car", "purchase"
    if any(keyword in lowered for keyword in ("emergency fund", "quy khan cap")):
        return "Emergency Fund", "emergency_fund"
    if any(keyword in lowered for keyword in ("du lich", "travel", "trip")):
        return "Travel Goal", "saving"

    purchase_patterns = (
        r"mua\s+(.+?)(?:\s+gia|\s+\d|\s+truoc|\s+trong|\s+by|\s+before|\s+in\s+\d+\s*(?:month|months|thang)|$)",
        r"(?:buy|purchase)\s+(?:a|an|the)?\s*(.+?)(?:\s+for|\s+worth|\s+costing|\s+\d|\s+by|\s+before|\s+in\s+\d+\s*months?|$)",
    )
    for pattern in purchase_patterns:
        purchase_match = re.search(pattern, lowered)
        if purchase_match:
            subject = purchase_match.group(1).strip(" .,!?")
            if subject:
                return f"Buy {subject.title()}", "purchase"

    return "New Goal", "custom"


def _extract_create_goal_payload(user_text: str) -> Optional[dict]:
    lowered = _normalize_text(user_text)
    if not any(
        keyword in lowered
        for keyword in (
            "mua",
            "buy",
            "purchase",
            "goal",
            "muc tieu",
            "tiet kiem",
            "save",
            "saving",
            "quy khan cap",
            "emergency fund",
            "travel",
            "trip",
            "du lich",
        )
    ):
        return None

    amount = _extract_amount(user_text)
    if amount is None:
        return None

    goal_name, goal_type = _infer_goal_name_and_type(user_text)
    return {
        "goal_name": goal_name,
        "goal_type": goal_type,
        "target_amount": amount,
        "target_date": _extract_target_date(user_text),
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


def _handle_pending_goal_deadline(session_id: str, user_text: str, draft: dict) -> tuple[str, list]:
    if _is_cancel_intent(user_text):
        clear_session_state(session_id)
        return "I canceled this goal creation flow. Start again whenever you want.", []

    target_date = _extract_target_date(user_text)
    if target_date is None:
        return _build_missing_deadline_question(draft.get("goal_name") or "this goal"), []

    completed_draft = {
        **draft,
        "target_date": target_date,
    }
    clear_session_state(session_id)
    action = _build_create_goal_action(completed_draft)
    reply_text = (
        "I have enough information for this goal. "
        f"If this looks right, tap Create Goal to save it with target date {target_date}."
    )
    return reply_text, [action]


def _build_plan_acknowledgement(context: ChatContext | None) -> str:
    payload = context.model_dump() if context else {}
    action_type = payload.get("action_type")
    action_payload = payload.get("action_payload") or payload

    if action_type == "A" or action_payload.get("strategy") == "increase_savings":
        amount = action_payload.get("amount")
        duration = action_payload.get("duration_months")
        details = []
        if amount:
            details.append(f"save an extra {amount:,} VND per month")
        if duration:
            details.append(f"for the next {duration} months")
        suffix = f" by {' '.join(details)}" if details else ""
        return f"Plan A was confirmed. I will guide you{suffix} to recover the goal timeline."

    if action_type == "B" or action_payload.get("strategy") == "extend_deadline":
        months = action_payload.get("months")
        new_target_date = action_payload.get("new_target_date")
        details = []
        if months:
            details.append(f"extend the deadline by {months} months")
        if new_target_date:
            details.append(f"toward {new_target_date}")
        suffix = f" to {' and '.join(details)}" if details else ""
        return f"Plan B was confirmed. I will guide you{suffix} so the goal remains achievable."

    if payload.get("action") == "keep_current_plan":
        return "Okay. I will keep the current goal setup and continue monitoring the risk signal."

    return "I noted your plan adjustment choice. You can keep reviewing it in the dashboard."


@router.post("/chat/message")
def post_chat_message(body: PostChatMessageRequest):
    if not body.message or not body.message.strip():
        return _error("Message cannot be empty.", "EMPTY_MESSAGE")

    session_id = body.session_id
    user_text = body.message.strip()
    history = ConversationHistory(session_id)

    actions: list = []
    source_screen = body.context.source_screen if body.context else None

    if user_text.lower() == "create goal" and source_screen == "agent_action":
        reply_text = _build_goal_acknowledgement(body.context)
    elif source_screen == "agent_action" and body.context:
        context_payload = body.context.model_dump()
        if (
            context_payload.get("strategy") in {"increase_savings", "extend_deadline"}
            or context_payload.get("action_type") in {"A", "B"}
            or context_payload.get("action") == "keep_current_plan"
        ):
            reply_text = _build_plan_acknowledgement(body.context)
        else:
            reply_text = "I noted your action. Let me know if you want to refine the plan further."
    else:
        session_state = get_session_state(session_id) or {}
        if session_state.get("flow_type") == "goal_creation_pending_deadline":
            reply_text, actions = _handle_pending_goal_deadline(session_id, user_text, session_state)
        elif session_state.get("flow_type") == "car_goal_creation":
            reply_text, actions = _handle_active_car_goal_draft(session_id, user_text, session_state)
        else:
            car_goal_signal = _has_car_goal_creation_signal(user_text)
            car_goal_intent = _detect_car_goal_intent(user_text)
            if not car_goal_intent and car_goal_signal:
                car_goal_intent = _detect_car_goal_intent_with_llm(user_text)

            if car_goal_intent and _extract_amount(user_text) is None:
                draft = _build_car_goal_draft(user_text)
                set_session_state(session_id, draft)
                if draft.get("target_date"):
                    reply_text = (
                        "To create a car goal based on a predicted price, I need a few details about the car. "
                        f"{_build_car_question(draft['pending_field'])}"
                    )
                else:
                    reply_text = _build_missing_deadline_question(draft["goal_name"])
            else:
                create_goal_payload = _extract_create_goal_payload(user_text)
                if create_goal_payload and create_goal_payload.get("target_date"):
                    actions = [_build_create_goal_action(create_goal_payload)]
                    reply_text = (
                        "I understood the financial goal you described. "
                        "If this looks right, tap Create Goal and I will save it for you."
                    )
                elif create_goal_payload:
                    set_session_state(
                        session_id,
                        {
                            "flow_type": "goal_creation_pending_deadline",
                            **create_goal_payload,
                        },
                    )
                    reply_text = _build_missing_deadline_question(create_goal_payload["goal_name"])
                elif car_goal_signal:
                    goal_name, _ = _infer_goal_name_and_type(user_text)
                    clear_session_state(session_id)
                    reply_text = _build_car_goal_clarification(goal_name if goal_name != "New Goal" else "Buy Car")
                else:
                    retriever = ContextRetriever()
                    user_context = retriever.fetch_user_financial_context(user_id="user_123")
                    sync_goals_with_user_context(user_context)

                    try:
                        intelligence = evaluate_user_context(user_context)
                        s_i = intelligence["s_i"]
                        strategy = intelligence["strategy"]
                    except Exception as exc:
                        return _error(f"Intelligence engine error: {exc}", "AGENT_PROCESSING_FAILED", 500)

                    active_goal_id = body.context.active_goal_id if body.context else None
                    goal = _resolve_goal_for_strategy(active_goal_id)
                    recommended_action = build_recommended_action(goal, strategy)
                    if recommended_action and goal is not None:
                        reply_text, _ = build_at_risk_chat_proposal(
                            goal,
                            user_context,
                            [recommended_action],
                            strategy=strategy,
                        )
                        actions = build_confirmation_actions(recommended_action)
                    else:
                        try:
                            reply_text = get_chat_advice(user_query=user_text, s_i=s_i)
                        except Exception:
                            reply_text = build_fallback_chat_advice(user_query=user_text, s_i=s_i)

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
