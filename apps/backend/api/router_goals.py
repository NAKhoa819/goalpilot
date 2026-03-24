"""
router_goals.py - Goal endpoints

GET  /api/goals/{goal_id}/progress
POST /api/goals
"""

import time
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from data.goal_store import create_goal as create_goal_entry
from data.goal_store import get_goal
from data.goal_store import sync_goals_with_user_context
from intelligence.intelligence import calculate_metrics, determine_strategy
from intelligence.llm_gateway import get_completion
from intelligence.prompts import build_system_prompt
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
    goal_status = "at_risk" if strategy == "B" else ("warning" if strategy == "A" else goal.get("status", "on_track"))

    recommendations: dict = {"recommended_actions": remediation_steps}
    if gap_detected:
        extra_per_month = int(remaining / max(1, delay_months * 6))
        recommendations["plan_a_option"] = {
            "strategy": "increase_savings",
            "amount": extra_per_month,
            "duration_months": delay_months * 2,
        }
        recommendations["plan_b_option"] = {
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
                "strategy_selected": strategy if strategy != "None" else "A",
                "requires_manual_verification": c_s < 0.5,
            },
            "recommendations": recommendations,
            "ui": {
                "banner_message": reasoning,
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
    try:
        datetime.strptime(body.target_date, "%Y-%m-%d")
    except ValueError:
        return _error("target_date must be YYYY-MM-DD.", "INVALID_TARGET_DATE")

    goal = create_goal_entry(
        goal_name=body.goal_name.strip(),
        goal_type=body.goal_type,
        target_amount=body.target_amount,
        target_date=body.target_date,
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
