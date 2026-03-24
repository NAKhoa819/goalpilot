"""
router_cashflow.py - Cash flow endpoint

GET /api/cashflow/weekly?goal_id={goal_id}
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from data.goal_store import get_goal_ids
from memory.retriever import ContextRetriever

router = APIRouter()


def _error(message: str, error_code: str, status_code: int = 400):
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "message": message, "error_code": error_code},
    )


def _empty_weekly_points(period_start: datetime) -> list[dict]:
    points: list[dict] = []
    for i in range(7):
        day = (period_start + timedelta(days=i)).strftime("%Y-%m-%d")
        points.append({"date": day, "income": 0, "expense": 0, "net": 0})
    return points


@router.get("/cashflow/weekly")
def get_cashflow_weekly(goal_id: Optional[str] = Query(default=None)):
    period_end = datetime.today()
    period_start = period_end - timedelta(days=6)

    retriever = ContextRetriever()
    user_context = retriever.fetch_user_financial_context(user_id="user_123")
    transactions = user_context.get("recent_transactions", [])

    if not transactions:
        return {
            "success": True,
            "data": {
                "period_start": period_start.strftime("%Y-%m-%d"),
                "period_end": (period_start + timedelta(days=6)).strftime("%Y-%m-%d"),
                "points": _empty_weekly_points(period_start),
            },
        }

    if goal_id:
        valid_ids = set(get_goal_ids())
        if goal_id not in valid_ids:
            return _error(f"goal_id '{goal_id}' is invalid.", "INVALID_GOAL_ID", 400)

    daily: dict[str, dict] = {}
    for i in range(7):
        day = (period_start + timedelta(days=i)).strftime("%Y-%m-%d")
        daily[day] = {"date": day, "income": 0, "expense": 0, "net": 0}

    for tx in transactions:
        tx_date = tx.get("date", "")
        if tx_date in daily:
            amount = float(tx.get("amount", 0))
            category = tx.get("category", "").lower()
            if category in ("dining", "rent", "groceries", "utilities", "shopping"):
                daily[tx_date]["expense"] += amount
            else:
                daily[tx_date]["income"] += amount

    points = []
    for day_data in daily.values():
        day_data["net"] = day_data["income"] - day_data["expense"]
        points.append(day_data)

    points.sort(key=lambda item: item["date"])

    return {
        "success": True,
        "data": {
            "period_start": period_start.strftime("%Y-%m-%d"),
            "period_end": (period_start + timedelta(days=6)).strftime("%Y-%m-%d"),
            "points": points,
        },
    }
