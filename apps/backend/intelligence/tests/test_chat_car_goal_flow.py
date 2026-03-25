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
    monkeypatch.setattr(router_chat, "evaluate_user_context", lambda user_context: {"s_i": 1.0, "strategy": "None"})
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


def test_chat_asks_for_deadline_before_create_goal_when_missing(monkeypatch):
    client, session_state_store = _build_client(monkeypatch)
    session_id = "goal-flow-1"

    first_res = client.post(
        "/api/chat/message",
        json={
            "session_id": session_id,
            "message": "Toi muon mua laptop gia 30 trieu",
            "context": {"source_screen": "agent"},
        },
    )

    assert first_res.status_code == 200
    first_reply = first_res.json()["data"]["reply"]
    assert "truoc khi nao" in first_reply["text"]
    assert "actions" not in first_reply

    stored_state = session_state_store[session_id]
    assert stored_state["flow_type"] == "goal_creation_pending_deadline"
    assert stored_state["goal_name"] == "Buy Laptop"
    assert stored_state["target_amount"] == 30_000_000
    assert stored_state["target_date"] is None

    second_res = client.post(
        "/api/chat/message",
        json={
            "session_id": session_id,
            "message": "truoc 2026-11-10",
            "context": {"source_screen": "agent"},
        },
    )

    assert second_res.status_code == 200
    second_reply = second_res.json()["data"]["reply"]
    assert second_reply["actions"][0]["type"] == "create_goal"
    assert second_reply["actions"][0]["payload"]["goal_name"] == "Buy Laptop"
    assert second_reply["actions"][0]["payload"]["target_amount"] == 30_000_000
    assert second_reply["actions"][0]["payload"]["target_date"] == "2026-11-10"
    assert session_id not in session_state_store


def test_chat_asks_car_goal_deadline_before_collecting_features(monkeypatch):
    client, session_state_store = _build_client(monkeypatch)
    session_id = "car-flow-4"

    first_res = client.post(
        "/api/chat/message",
        json={
            "session_id": session_id,
            "message": "Toi muon mua xe",
            "context": {"source_screen": "agent"},
        },
    )

    assert first_res.status_code == 200
    first_reply = first_res.json()["data"]["reply"]
    assert "truoc khi nao" in first_reply["text"]
    assert "actions" not in first_reply
    assert session_state_store[session_id]["flow_type"] == "car_goal_creation"
    assert session_state_store[session_id]["target_date"] is None

    second_res = client.post(
        "/api/chat/message",
        json={
            "session_id": session_id,
            "message": "trong 8 thang",
            "context": {"source_screen": "agent"},
        },
    )

    assert second_res.status_code == 200
    second_reply = second_res.json()["data"]["reply"]
    assert "bao nhi" in second_reply["text"]
    assert session_state_store[session_id]["target_date"] is not None


def test_extract_create_goal_payload_supports_accented_non_car_goal():
    payload = router_chat._extract_create_goal_payload(
        "Toi muon mua dien thoai gia 20 trieu truoc 2026-12-01"
    )

    assert payload is not None
    assert payload["goal_name"] == "Buy Dien Thoai"
    assert payload["goal_type"] == "purchase"
    assert payload["target_amount"] == 20_000_000
    assert payload["target_date"] == "2026-12-01"


def test_extract_create_goal_payload_supports_ty_unit_for_non_car_goal():
    payload = router_chat._extract_create_goal_payload(
        "Toi muon mua nha gia 2 ty truoc 2030-01-01"
    )

    assert payload is not None
    assert payload["goal_name"] == "Buy Nha"
    assert payload["goal_type"] == "purchase"
    assert payload["target_amount"] == 2_000_000_000
    assert payload["target_date"] == "2030-01-01"


def test_extract_create_goal_payload_supports_cu_unit():
    payload = router_chat._extract_create_goal_payload(
        "Toi muon mua laptop 30 cu truoc 2026-11-10"
    )

    assert payload is not None
    assert payload["goal_name"] == "Buy Laptop"
    assert payload["target_amount"] == 30_000_000
    assert payload["target_date"] == "2026-11-10"


def test_extract_create_goal_payload_supports_unicode_vietnamese():
    payload = router_chat._extract_create_goal_payload(
        "T\u00f4i mu\u1ed1n mua \u0111i\u1ec7n tho\u1ea1i gi\u00e1 20 tri\u1ec7u tr\u01b0\u1edbc 2026-12-01"
    )

    assert payload is not None
    assert payload["goal_name"] == "Buy Dien Thoai"
    assert payload["target_amount"] == 20_000_000
    assert payload["target_date"] == "2026-12-01"
