import sys
import os
import pytest

# Sys.path anchor
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

# Mock provider — no real LLM calls
os.environ["ACTIVE_LLM_PROVIDER"] = "backup"
os.environ["BACKUP_PROVIDER"] = "mock"

from fastapi.testclient import TestClient
from main_api import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

def test_health(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


# ---------------------------------------------------------------------------
# GET /api/dashboard
# ---------------------------------------------------------------------------

def test_get_dashboard(client):
    res = client.get("/api/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    d = data["data"]
    assert "goals" in d and "active_goal_id" in d
    assert "chat_preview" in d and "input_actions" in d
    assert d["active_goal_id"] is None or isinstance(d["active_goal_id"], str)
    for goal in d["goals"]:
        for field in ("goal_id", "goal_name", "target_amount", "target_date",
                      "current_saved", "progress_percent", "status"):
            assert field in goal, f"Missing GoalCard field: {field}"


# ---------------------------------------------------------------------------
# GET /api/goals/{goal_id}/progress
# ---------------------------------------------------------------------------

def test_get_goal_progress(client):
    create_res = client.post("/api/goals", json={
        "goal_name": "Progress Goal",
        "goal_type": "saving",
        "target_amount": 12_000_000,
        "target_date": "2027-01-01",
        "currency": "VND",
    })
    goal_id = create_res.json()["data"]["goal_id"]
    res = client.get(f"/api/goals/{goal_id}/progress")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    d = data["data"]
    for block in ("goal", "analysis", "recommendations", "ui"):
        assert block in d, f"Missing block: {block}"
    a = d["analysis"]
    for field in ("gap_detected", "gap_delta", "gap_reason",
                  "confidence_score", "strategy_selected", "requires_manual_verification"):
        assert field in a, f"Missing analysis field: {field}"
    assert isinstance(a["confidence_score"], float)
    assert a["strategy_selected"] in ("A", "B", "None")
    expected_status = "on_track" if a["strategy_selected"] == "None" else "at_risk"
    assert d["goal"]["status"] == expected_status


def test_get_goal_progress_not_found(client):
    res = client.get("/api/goals/zzz_nonexistent/progress")
    data = res.json()
    if res.status_code == 404:
        assert data["success"] is False
        assert data["error_code"] == "GOAL_NOT_FOUND"
    else:
        assert data["success"] is True


# ---------------------------------------------------------------------------
# POST /api/goals
# ---------------------------------------------------------------------------

def test_create_goal(client):
    res = client.post("/api/goals", json={
        "goal_name": "Travel to Europe",
        "goal_type": "purchase",
        "target_amount": 50_000_000,
        "target_date": "2027-06-01",
        "currency": "VND",
        "created_from": "chat",
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "goal_id" in data["data"]
    assert data["data"]["progress_percent"] == 0
    assert data["data"]["status"] == "on_track"


def test_create_goal_missing_field(client):
    res = client.post("/api/goals", json={
        "goal_type": "saving",
        "target_amount": 10_000_000,
        "target_date": "2027-01-01",
        "currency": "VND",
    })
    assert res.status_code in (400, 422)


def test_create_goal_invalid_date(client):
    res = client.post("/api/goals", json={
        "goal_name": "Bad Date Goal",
        "goal_type": "saving",
        "target_amount": 10_000_000,
        "target_date": "not-a-date",
        "currency": "VND",
    })
    data = res.json()
    assert data["success"] is False
    assert data["error_code"] == "INVALID_TARGET_DATE"


# ---------------------------------------------------------------------------
# POST /api/chat/message
# ---------------------------------------------------------------------------

def test_post_chat_message(client):
    res = client.post("/api/chat/message", json={
        "session_id": "s_test_001",
        "message": "Xem tài chính của tôi",
        "context": {"active_goal_id": None, "source_screen": "dashboard"},
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    reply = data["data"]["reply"]
    assert reply["role"] == "assistant"
    assert "text" in reply and "message_id" in reply


def test_apply_goal_action_accept_wrapper(client):
    create_res = client.post("/api/goals", json={
        "goal_name": "Action Goal",
        "goal_type": "saving",
        "target_amount": 10_000_000,
        "target_date": "2027-01-01",
        "currency": "VND",
    })
    goal_id = create_res.json()["data"]["goal_id"]

    res = client.post(f"/api/goals/{goal_id}/actions", json={
        "session_id": "s_apply_accept_001",
        "action": {
            "type": "accept",
            "label": "Apply Recommended Plan",
            "payload": {
                "goal_id": goal_id,
                "action": "confirm_recommended_plan",
                "action_type": "A",
                "action_label": "Plan A - Save an extra 1,000,000 VND/month",
                "action_payload": {
                    "goal_id": goal_id,
                    "strategy": "increase_savings",
                    "amount": 1_000_000,
                    "duration_months": 6,
                },
            },
        },
    })

    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["applied_action_type"] == "A"
    assert "Plan A" in data["data"]["reply"]["text"]


def test_post_chat_message_empty(client):
    res = client.post("/api/chat/message", json={
        "session_id": "s_test_002",
        "message": "   ",
        "context": {},
    })
    data = res.json()
    assert data["success"] is False
    assert data["error_code"] == "EMPTY_MESSAGE"


# ---------------------------------------------------------------------------
# GET /api/chat/session/{session_id}
# ---------------------------------------------------------------------------

def test_get_chat_session_not_found(client):
    res = client.get("/api/chat/session/nonexistent_session_99")
    assert res.status_code == 404
    data = res.json()
    assert data["success"] is False
    assert data["error_code"] == "SESSION_NOT_FOUND"


def test_get_chat_session_after_message(client):
    session_id = "s_integration_001"
    client.post("/api/chat/message", json={
        "session_id": session_id,
        "message": "Tôi muốn mua laptop",
        "context": {},
    })
    res = client.get(f"/api/chat/session/{session_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    messages = data["data"]["messages"]
    assert len(messages) >= 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"


# ---------------------------------------------------------------------------
# GET /api/cashflow/weekly
# ---------------------------------------------------------------------------

def test_get_cashflow_weekly(client):
    res = client.get("/api/cashflow/weekly")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    d = data["data"]
    assert "period_start" in d and "period_end" in d and "points" in d
    for point in d["points"]:
        for field in ("date", "income", "expense", "net"):
            assert field in point


def test_get_cashflow_weekly_with_goal_id(client):
    dash = client.get("/api/dashboard").json()
    if dash["data"]["goals"]:
        goal_id = dash["data"]["goals"][0]["goal_id"]
    else:
        create_res = client.post("/api/goals", json={
            "goal_name": "Cashflow Goal",
            "goal_type": "saving",
            "target_amount": 5_000_000,
            "target_date": "2027-01-01",
            "currency": "VND",
        })
        goal_id = create_res.json()["data"]["goal_id"]
    res = client.get(f"/api/cashflow/weekly?goal_id={goal_id}")
    assert res.status_code == 200
    assert res.json()["success"] is True


def test_get_cashflow_invalid_goal_id(client):
    res = client.get("/api/cashflow/weekly?goal_id=zzz_bad")
    data = res.json()
    assert data["success"] is False
    assert data["error_code"] == "INVALID_GOAL_ID"


# ---------------------------------------------------------------------------
# POST /api/input-data
# ---------------------------------------------------------------------------

def test_post_input_data_manual(client):
    res = client.post("/api/input-data", json={
        "source": "manual",
        "payload": {
            "monthly_income": 12_000_000,
            "current_balance": 8_000_000,
            "projected_savings": 3_500_000,
            "categories": [
                {"name": "dining", "current_month_spend": 2_200_000, "is_essential": False}
            ],
        },
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["imported_count"] > 0
    assert data["data"]["should_refresh_dashboard"] is True


def test_post_input_data_ocr(client):
    res = client.post("/api/input-data", json={
        "source": "ocr",
        "payload": {
            "transactions": [
                {"date": "2026-03-10", "amount": 250_000, "description": "Restaurant", "category": "dining"}
            ]
        },
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["data"]["imported_count"] == 1


def test_post_input_data_invalid_source(client):
    res = client.post("/api/input-data", json={
        "source": "invalid_source",
        "payload": {},
    })
    data = res.json()
    assert data["success"] is False
    assert data["error_code"] == "INVALID_INPUT_SOURCE"


def test_post_input_data_no_records(client):
    res = client.post("/api/input-data", json={
        "source": "ocr",
        "payload": {"transactions": []},
    })
    data = res.json()
    assert data["success"] is False
    assert data["error_code"] == "NO_VALID_RECORDS"
