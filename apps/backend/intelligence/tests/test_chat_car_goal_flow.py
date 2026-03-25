import os
import sys
from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from api import router_chat


class FakeConversationHistory:
    store: dict[str, list[dict]] = {}

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.store.setdefault(session_id, [])

    def add_message(self, role: str, content: str, actions=None, message_id=None):
        self.store[self.session_id].append(
            {
                "message_id": message_id,
                "role": role,
                "content": content,
                "actions": actions,
            }
        )

    def get_all_messages(self):
        return list(self.store[self.session_id])


class FakeRetriever:
    def fetch_user_financial_context(self, user_id: str):
        return {"monthly_spending": 1_000_000}


def _build_client(monkeypatch):
    app = FastAPI()
    app.include_router(router_chat.router, prefix="/api")

    session_state_store: dict[str, dict] = {}
    FakeConversationHistory.store.clear()

    monkeypatch.setattr(router_chat, "ConversationHistory", FakeConversationHistory)
    monkeypatch.setattr(router_chat, "ContextRetriever", lambda: FakeRetriever())
    monkeypatch.setattr(router_chat, "calculate_metrics", lambda user_context: {"s_i": 1.0})
    monkeypatch.setattr(router_chat, "determine_strategy", lambda s_i: "None")
    monkeypatch.setattr(router_chat, "get_chat_advice", lambda user_query, s_i: "general")
    monkeypatch.setattr(router_chat, "build_fallback_chat_advice", lambda user_query, s_i: "fallback")
    monkeypatch.setattr(router_chat, "get_session_state", lambda session_id: session_state_store.get(session_id))
    monkeypatch.setattr(
        router_chat,
        "set_session_state",
        lambda session_id, state: session_state_store.__setitem__(session_id, dict(state)),
    )
    monkeypatch.setattr(router_chat, "clear_session_state", lambda session_id: session_state_store.pop(session_id, None))

    return TestClient(app), session_state_store


def test_chat_starts_car_goal_draft(monkeypatch):
    client, session_state_store = _build_client(monkeypatch)

    res = client.post(
        "/api/chat/message",
        json={
            "session_id": "car-flow-1",
            "message": "Tôi muốn mua xe trước 2026-12-31",
            "context": {"source_screen": "agent"},
        },
    )

    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "giá khoảng bao nhiêu" in data["data"]["reply"]["text"]
    assert "actions" not in data["data"]["reply"]

    stored_state = session_state_store["car-flow-1"]
    assert stored_state["flow_type"] == "car_goal_creation"
    assert stored_state["target_date"] == "2026-12-31"
    assert stored_state["pending_field"] == "Present_Price"


def test_chat_collects_car_features_and_returns_create_goal_action(monkeypatch):
    client, session_state_store = _build_client(monkeypatch)
    monkeypatch.setattr(
        router_chat,
        "predict_car_price",
        lambda body: SimpleNamespace(predicted_price=456_000_000),
    )

    session_id = "car-flow-2"
    messages = [
        "Tôi muốn mua xe trước 2026-12-31",
        "600000000",
        "25000 km",
        "dầu diesel",
        "cá nhân",
        "số tự động",
        "0",
        "2022",
    ]

    last_response = None
    for message in messages:
        last_response = client.post(
            "/api/chat/message",
            json={"session_id": session_id, "message": message, "context": {"source_screen": "agent"}},
        )

    assert last_response is not None
    assert last_response.status_code == 200
    data = last_response.json()
    reply = data["data"]["reply"]
    assert reply["actions"][0]["type"] == "create_goal"
    assert reply["actions"][0]["payload"]["goal_name"] == "Buy Car"
    assert reply["actions"][0]["payload"]["target_amount"] == 456_000_000
    assert reply["actions"][0]["payload"]["target_date"] == "2026-12-31"
    assert session_id not in session_state_store


def test_chat_direct_goal_creation_still_works_when_amount_is_provided(monkeypatch):
    client, _ = _build_client(monkeypatch)

    res = client.post(
        "/api/chat/message",
        json={
            "session_id": "car-flow-3",
            "message": "Tôi muốn mua xe giá 500000000 trước 2026-11-01",
            "context": {"source_screen": "agent"},
        },
    )

    assert res.status_code == 200
    data = res.json()
    reply = data["data"]["reply"]
    assert reply["actions"][0]["type"] == "create_goal"
    assert reply["actions"][0]["payload"]["target_amount"] == 500_000_000
    assert reply["actions"][0]["payload"]["target_date"] == "2026-11-01"
