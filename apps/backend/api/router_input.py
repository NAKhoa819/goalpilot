"""
router_input.py - Input data endpoint

POST /api/input-data
"""

from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from data.goal_store import get_goal_ids, sync_goals_with_user_context
from data.user_context_store import apply_manual_input, apply_transactions
from memory.retriever import ContextRetriever

router = APIRouter()

VALID_SOURCES = {"manual", "ocr", "sms", "file"}


class InputDataRequest(BaseModel):
    source: str
    payload: Any


def _error(message: str, error_code: str, status_code: int = 400):
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "message": message, "error_code": error_code},
    )


@router.post("/input-data")
def post_input_data(body: InputDataRequest):
    if body.source not in VALID_SOURCES:
        return _error(
            f"Invalid source '{body.source}'. Must be one of: {sorted(VALID_SOURCES)}",
            "INVALID_INPUT_SOURCE",
        )

    payload = body.payload or {}
    imported_count = 0

    if body.source == "manual":
        imported_count = apply_manual_input(payload)
    else:
        transactions = payload.get("transactions", [])
        if not transactions:
            return _error("No valid records found in payload.", "NO_VALID_RECORDS")

        imported_count = apply_transactions(transactions)
        if not imported_count:
            return _error("No valid transaction records.", "NO_VALID_RECORDS")

    if imported_count == 0:
        return _error("No valid records found in payload.", "NO_VALID_RECORDS")

    user_context = ContextRetriever().fetch_user_financial_context(user_id="user_123")
    sync_goals_with_user_context(user_context)

    return {
        "success": True,
        "message": "Input data processed successfully",
        "data": {
            "imported_count": imported_count,
            "affected_goals": get_goal_ids(),
            "should_refresh_dashboard": True,
        },
    }
