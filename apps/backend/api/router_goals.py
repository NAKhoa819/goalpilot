"""
router_goals.py - Goal endpoints

GET  /api/goals/{goal_id}/progress
POST /api/goals
POST /api/goals/{goal_id}/actions
"""

import time
import uuid
from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from data.goal_action_store import get_goal_action_state, upsert_goal_action_state
from data.goal_store import create_goal as create_goal_entry
from data.goal_store import get_goal, sync_goals_with_user_context, update_goal_target_date
from intelligence.intelligence import calculate_metrics, determine_strategy
from intelligence.llm_gateway import get_completion
from intelligence.prompts import build_system_prompt
from memory.history import ConversationHistory
from memory.retriever import ContextRetriever
from models.schemas import StrategyResponse

router = APIRouter()


class CreateGoalRequest(BaseModel):
    goal_name: str
    goal_type: str
    target_amount: float
    target_date: str
    currency: str = "VND"
    created_from: Optional[str] = None


class GoalActionItem(BaseModel):
    type: str
    label: str
    payload: dict[str, Any]


class GoalActionRequest(BaseModel):
    session_id: str
    action: GoalActionItem


def _error(message: str, error_code: str, status_code: int = 400):
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "message": message, "error_code": error_code},
    )


def _determine_warning_level(s_i: float) -> str:
    if s_i < 0.5:
        return "critical"
    if s_i < 0.8:
        return "warning"
    return "info"


def _calc_gap_reason(user_context: dict) -> str:
    balance = user_context.get("balance", 0)
    monthly_spending = user_context.get("monthly_spending", 0)
    if monthly_spending > balance * 0.9:
        return "overspending"
    return "mixed"


def _calc_reprojected_eta(target_date_str: str, gap_months: int) -> str:
    try:
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d")
        reprojected = target_date + timedelta(days=gap_months * 30)
        return reprojected.strftime("%Y-%m-%d")
    except Exception:
        return target_date_str


def _parse_date(value: str, *, error_code: str = "INVALID_TARGET_DATE") -> str | JSONResponse:
    try:
        return datetime.strptime(value, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        return _error("target_date must be YYYY-MM-DD.", error_code)


def _coerce_positive_int(value: Any, field_name: str) -> int | JSONResponse:
    try:
        coerced = int(float(value))
    except (TypeError, ValueError):
        return _error(f"{field_name} must be a positive number.", "INVALID_ACTION_PAYLOAD")

    if coerced <= 0:
        return _error(f"{field_name} must be a positive number.", "INVALID_ACTION_PAYLOAD")
    return coerced


def _build_active_plan_banner(goal: dict, accepted_plan: dict) -> str:
    payload = accepted_plan.get("payload", {})
    goal_name = goal.get("goal_name", "your goal")
    if accepted_plan.get("action_type") == "A":
        amount = int(payload.get("amount", 0))
        duration = payload.get("duration_months")
        duration_text = f" for the next {duration} months" if duration else ""
        return (
            f"Plan A is active for {goal_name}. "
            f"Save an extra {amount:,} VND per month{duration_text} to stay on track."
        )

    new_target_date = payload.get("new_target_date") or goal.get("target_date", "2026-12-01")
    months = payload.get("months")
    months_text = f" by {months} months" if months else ""
    return (
        f"Plan B is active for {goal_name}. "
        f"The target date has been extended{months_text} to {new_target_date}."
    )


def _build_goal_action_reply(goal: dict, action_type: str, payload: dict[str, Any]) -> str:
    goal_name = goal.get("goal_name", "your goal")
    if action_type == "A":
        amount = int(payload.get("amount", 0))
        duration = payload.get("duration_months")
        duration_text = f" for the next {duration} months" if duration else ""
        return (
            f"Plan A is now active for {goal_name}. "
            f"Aim to save an extra {amount:,} VND per month{duration_text}."
        )

    new_target_date = payload.get("new_target_date") or goal.get("target_date", "2026-12-01")
    return (
        f"Plan B is now active for {goal_name}. "
        f"I updated the target date to {new_target_date}."
    )


def _normalize_goal_action_payload(goal_id: str, goal: dict, action: GoalActionItem) -> dict | JSONResponse:
    payload = dict(action.payload or {})
    if payload.get("goal_id") != goal_id:
        return _error("goal_id in payload must match the target goal.", "GOAL_ACTION_MISMATCH")

    if action.type == "A":
        if payload.get("strategy") != "increase_savings":
            return _error("Plan A payload must use increase_savings.", "INVALID_ACTION_PAYLOAD")

        amount = _coerce_positive_int(payload.get("amount"), "amount")
        if isinstance(amount, JSONResponse):
            return amount

        normalized = {
            "goal_id": goal_id,
            "strategy": "increase_savings",
            "amount": amount,
        }
        if payload.get("duration_months") is not None:
            duration = _coerce_positive_int(payload.get("duration_months"), "duration_months")
            if isinstance(duration, JSONResponse):
                return duration
            normalized["duration_months"] = duration
        return normalized

    if action.type == "B":
        if payload.get("strategy") != "extend_deadline":
            return _error("Plan B payload must use extend_deadline.", "INVALID_ACTION_PAYLOAD")

        months = _coerce_positive_int(payload.get("months"), "months")
        if isinstance(months, JSONResponse):
            return months

        new_target_date = payload.get("new_target_date") or _calc_reprojected_eta(
            goal.get("target_date", "2026-12-01"),
            months,
        )
        parsed_date = _parse_date(str(new_target_date))
        if isinstance(parsed_date, JSONResponse):
            return parsed_date

        return {
            "goal_id": goal_id,
            "strategy": "extend_deadline",
            "months": months,
            "new_target_date": parsed_date,
        }

    return _error("Only action types A and B are supported here.", "INVALID_ACTION_TYPE")


@router.get("/goals/{goal_id}/progress")
def get_goal_progress(goal_id: str):
    if not goal_id or not goal_id.strip():
        return _error("goal_id is invalid.", "INVALID_GOAL_ID")

    goal = get_goal(goal_id)
    if goal is None:
        return _error(f"Goal '{goal_id}' not found.", "GOAL_NOT_FOUND", 404)

    retriever = ContextRetriever()
    user_context = retriever.fetch_user_financial_context(user_id="user_123")
    sync_goals_with_user_context(user_context)
    goal = get_goal(goal_id)
    if goal is None:
        return _error(f"Goal '{goal_id}' not found.", "GOAL_NOT_FOUND", 404)

    accepted_plan = get_goal_action_state(goal_id)

    profile = {
        "mu_hist": user_context.get("monthly_spending", 4500.0) * 0.9,
        "sigma_hist": user_context.get("monthly_spending", 4500.0) * 0.15,
        "beta_prop": user_context.get("monthly_spending", 4500.0),
        "last_update_timestamp": time.time() - 86400,
        "data_completeness": 0.85,
        "market_volatility": 0.3,
    }
    metrics = calculate_metrics(profile)
    s_i = metrics["s_i"]
    c_s = metrics["c_s"]
    strategy = determine_strategy(s_i)

    gap_detected = strategy != "None"
    warning_level = _determine_warning_level(s_i)
    gap_reason = _calc_gap_reason(user_context) if gap_detected else "mixed"

    reasoning = ""
    remediation_steps: list[str] = []
    try:
        system_prompt = build_system_prompt(user_context, strategy if strategy != "None" else "A")
        messages = [{"role": "system", "content": system_prompt}]
        llm_resp: StrategyResponse = get_completion(messages=messages, response_format=StrategyResponse)
        reasoning = llm_resp.reasoning
        remediation_steps = llm_resp.remediation_steps
    except Exception:
        reasoning = (
            "Your goal is currently at risk. Consider reviewing your spending habits."
            if gap_detected
            else "Your finances are on track."
        )
        remediation_steps = ["Review your monthly budget", "Check recent transactions"]

    target_amount = float(goal.get("target_amount", 0))
    current_saved = float(goal.get("current_saved", 0))
    remaining = max(0, target_amount - current_saved)
    progress_pct = int(min(100, (current_saved / target_amount * 100) if target_amount > 0 else 0))

    planned_eta = goal.get("target_date", "2026-12-01")
    delay_months = 3 if strategy == "B" else 1
    reprojected_eta = _calc_reprojected_eta(planned_eta, delay_months) if gap_detected else planned_eta
    goal_status = "at_risk" if strategy in {"A", "B"} else goal.get("status", "on_track")

    recommendations: dict[str, Any] = {"recommended_actions": remediation_steps}
    accepted_action_type = None
    accepted_action_payload = None
    banner_message = reasoning

    if accepted_plan:
        accepted_action_type = accepted_plan.get("action_type")
        accepted_action_payload = accepted_plan.get("payload")
        gap_detected = False
        warning_level = "info"
        goal_status = "completed" if progress_pct >= 100 else "on_track"
        banner_message = _build_active_plan_banner(goal, accepted_plan)
        recommendations = {"recommended_actions": [banner_message]}
        if accepted_action_type == "B":
            reprojected_eta = accepted_action_payload.get("new_target_date", planned_eta)
        else:
            reprojected_eta = planned_eta
        cta_buttons = ["View Details"]
    else:
        if gap_detected:
            extra_per_month = int(remaining / max(1, delay_months * 6))
            recommendations["plan_a_option"] = {
                "goal_id": goal_id,
                "strategy": "increase_savings",
                "amount": extra_per_month,
                "duration_months": delay_months * 2,
            }
            recommendations["plan_b_option"] = {
                "goal_id": goal_id,
                "strategy": "extend_deadline",
                "months": delay_months,
                "new_target_date": reprojected_eta,
            }

            if strategy == "B":
                recommendations["deadline_extension_option"] = {
                    "new_target_date": reprojected_eta,
                    "delay_days": delay_months * 30,
                }
            if strategy == "A":
                recommendations["income_augmentation_option"] = {
                    "required_extra_income_per_month": extra_per_month,
                }

        if strategy == "A":
            cta_buttons = ["Increase Savings", "Review Budget", "Review Details"]
        elif strategy == "B":
            cta_buttons = ["Extend Deadline", "Increase Income Target", "Review Details"]
        else:
            cta_buttons = ["View Details"]

    return {
        "success": True,
        "data": {
            "goal": {
                "goal_id": goal["goal_id"],
                "goal_name": goal["goal_name"],
                "target_amount": target_amount,
                "target_date": planned_eta,
                "current_saved": current_saved,
                "remaining_amount": remaining,
                "progress_percent": progress_pct,
                "planned_eta": planned_eta,
                "reprojected_eta": reprojected_eta,
                "status": goal_status,
            },
            "analysis": {
                "gap_detected": gap_detected,
                "gap_delta": int(remaining * 0.1) if gap_detected else 0,
                "gap_reason": gap_reason,
                "confidence_score": round(c_s, 2),
                "strategy_selected": strategy,
                "accepted_action_type": accepted_action_type,
                "accepted_action_payload": accepted_action_payload,
                "requires_manual_verification": c_s < 0.5,
            },
            "recommendations": recommendations,
            "ui": {
                "banner_message": banner_message,
                "warning_level": warning_level,
                "cta_buttons": cta_buttons,
            },
        },
    }


@router.post("/goals")
def create_goal(body: CreateGoalRequest):
    if not body.goal_name or not body.goal_name.strip():
        return _error("goal_name is required.", "MISSING_REQUIRED_FIELD")
    if body.target_amount <= 0:
        return _error("target_amount must be positive.", "INVALID_TARGET_AMOUNT")

    parsed_date = _parse_date(body.target_date)
    if isinstance(parsed_date, JSONResponse):
        return parsed_date

    goal = create_goal_entry(
        goal_name=body.goal_name.strip(),
        goal_type=body.goal_type,
        target_amount=body.target_amount,
        target_date=parsed_date,
        currency=body.currency,
        created_from=body.created_from,
    )

    return {
        "success": True,
        "message": "Goal created successfully",
        "data": {
            "goal_id": goal["goal_id"],
            "goal_name": goal["goal_name"],
            "progress_percent": 0,
            "status": "on_track",
        },
    }


@router.post("/goals/{goal_id}/actions")
def apply_goal_action(goal_id: str, body: GoalActionRequest):
    if not goal_id or not goal_id.strip():
        return _error("goal_id is invalid.", "INVALID_GOAL_ID")
    if not body.session_id or not body.session_id.strip():
        return _error("session_id is invalid.", "INVALID_SESSION_ID")

    goal = get_goal(goal_id)
    if goal is None:
        return _error(f"Goal '{goal_id}' not found.", "GOAL_NOT_FOUND", 404)

    normalized_payload = _normalize_goal_action_payload(goal_id, goal, body.action)
    if isinstance(normalized_payload, JSONResponse):
        return normalized_payload

    if body.action.type == "B":
        update_goal_target_date(goal_id, normalized_payload["new_target_date"])
        refreshed_goal = get_goal(goal_id)
        if refreshed_goal is not None:
            goal = refreshed_goal

    upsert_goal_action_state(
        goal_id=goal_id,
        action_type=body.action.type,
        strategy=normalized_payload["strategy"],
        payload=normalized_payload,
    )

    reply_text = _build_goal_action_reply(goal, body.action.type, normalized_payload)
    history = ConversationHistory(body.session_id.strip())
    user_msg_id = f"u_{uuid.uuid4().hex[:8]}"
    assistant_msg_id = f"a_{uuid.uuid4().hex[:8]}"
    history.add_message("user", body.action.label.strip() or body.action.type, message_id=user_msg_id)
    history.add_message("assistant", reply_text, message_id=assistant_msg_id)

    return {
        "success": True,
        "data": {
            "goal_id": goal_id,
            "applied_action_type": body.action.type,
            "should_refresh_dashboard": True,
            "reply": {
                "message_id": assistant_msg_id,
                "role": "assistant",
                "text": reply_text,
            },
        },
    }
