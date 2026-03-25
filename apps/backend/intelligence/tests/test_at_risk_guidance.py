import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from api import chat_seed, router_chat
from intelligence import at_risk_guidance
from models.schemas import AtRiskProposalResponse


class FakeSeedHistory:
    store: dict[str, list[dict]] = {}

    @staticmethod
    def ensure_session(session_id: str, seed_welcome: bool = False) -> None:
        FakeSeedHistory.store.setdefault(session_id, [])

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.store.setdefault(session_id, [])

    def get_all_messages(self):
        return list(self.store[self.session_id])

    def add_message(self, role: str, content: str, actions=None, message_id=None):
        self.store[self.session_id].append(
            {
                "role": role,
                "content": content,
                "actions": actions,
                "message_id": message_id,
            }
        )


def _sample_goal() -> dict:
    return {
        "goal_id": "g001",
        "goal_name": "Buy Laptop",
        "goal_type": "purchase",
        "target_amount": 30_000_000,
        "target_date": "2026-12-01",
        "current_saved": 18_000_000,
        "status": "at_risk",
    }


def _sample_actions() -> list[dict]:
    return [
        {
            "type": "A",
            "label": "Plan A - Tang them 2,000,000 VND/thang",
            "payload": {
                "goal_id": "g001",
                "strategy": "increase_savings",
                "amount": 2_000_000,
                "duration_months": 6,
            },
        },
        {
            "type": "B",
            "label": "Plan B - Doi deadline them 3 thang",
            "payload": {
                "goal_id": "g001",
                "strategy": "extend_deadline",
                "months": 3,
                "new_target_date": "2027-03-01",
            },
        },
    ]


def test_build_at_risk_chat_proposal_preserves_legacy_dual_actions(monkeypatch):
    monkeypatch.setattr(
        at_risk_guidance,
        "get_completion",
        lambda messages, response_format=None: AtRiskProposalResponse(
            risk_summary="Your laptop goal is off track because the gap is not closing fast enough.",
            plan_a_reason="Plan A works if you can redirect a bit more money every month.",
            plan_a_saving_tips=[
                "Cut one flexible expense category.",
                "Pause a low-value subscription.",
            ],
            plan_b_reason="Plan B works if you want a safer timeline with lower monthly pressure.",
        ),
    )

    actions = _sample_actions()
    text, returned_actions = at_risk_guidance.build_at_risk_chat_proposal(
        _sample_goal(),
        {"monthly_spending": 1_000_000},
        actions,
        strategy="A",
    )

    assert "Plan A:" in text
    assert "Plan B:" in text
    assert "Saving ideas:" in text
    assert returned_actions == actions


def test_build_at_risk_chat_proposal_supports_single_recommended_action():
    selected_action = [_sample_actions()[0]]
    text, returned_actions = at_risk_guidance.build_at_risk_chat_proposal(
        _sample_goal(),
        {"monthly_spending": 1_000_000},
        selected_action,
        strategy="A",
    )

    assert "GoalPilot selected Plan A" in text
    assert "Confirm this plan" in text
    assert returned_actions == selected_action


def test_build_at_risk_chat_proposal_falls_back_when_llm_fails(monkeypatch):
    monkeypatch.setattr(
        at_risk_guidance,
        "get_completion",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("llm down")),
    )

    actions = _sample_actions()
    text, returned_actions = at_risk_guidance.build_at_risk_chat_proposal(
        _sample_goal(),
        {"monthly_spending": 1_000_000},
        actions,
        strategy="B",
    )

    assert "Plan A helps" in text
    assert "Plan B helps" in text
    assert returned_actions == actions


def test_chat_seed_uses_confirmation_actions_for_selected_strategy(monkeypatch):
    FakeSeedHistory.store.clear()
    monkeypatch.setattr(chat_seed, "ConversationHistory", FakeSeedHistory)
    monkeypatch.setattr(chat_seed, "list_goals", lambda: [_sample_goal()])
    monkeypatch.setattr(chat_seed, "sync_goals_with_user_context", lambda user_context: [_sample_goal()])
    monkeypatch.setattr(
        chat_seed,
        "ContextRetriever",
        lambda: type("Retriever", (), {"fetch_user_financial_context": lambda self, user_id: {"balance": 1_000_000}})(),
    )
    monkeypatch.setattr(chat_seed, "evaluate_user_context", lambda user_context: {"strategy": "B"})
    monkeypatch.setattr(
        chat_seed,
        "build_at_risk_chat_proposal",
        lambda goal, user_context, actions, strategy: (
            "Your goal is off track. GoalPilot selected Plan B.",
            actions,
        ),
    )

    chat_seed.ensure_chat_seed("s_seed_test")

    messages = FakeSeedHistory.store["s_seed_test"]
    assert len(messages) == 1
    assert messages[0]["role"] == "assistant"
    assert "Plan B" in messages[0]["content"]
    assert [action["type"] for action in messages[0]["actions"]] == ["accept", "cancel"]
    assert messages[0]["actions"][0]["payload"]["action_type"] == "B"


def test_chat_seed_uses_session_scoped_welcome_message_id(monkeypatch):
    FakeSeedHistory.store.clear()
    monkeypatch.setattr(chat_seed, "ConversationHistory", FakeSeedHistory)
    monkeypatch.setattr(chat_seed, "list_goals", lambda: [])
    monkeypatch.setattr(chat_seed, "sync_goals_with_user_context", lambda user_context: [])
    monkeypatch.setattr(
        chat_seed,
        "ContextRetriever",
        lambda: type("Retriever", (), {"fetch_user_financial_context": lambda self, user_id: {"balance": 0}})(),
    )

    chat_seed.ensure_chat_seed("s_empty")

    messages = FakeSeedHistory.store["s_empty"]
    assert len(messages) == 1
    assert messages[0]["message_id"] == "m_welcome_s_empty"
    assert messages[0]["content"] == "How can I help with your financial goals today?"


def test_router_chat_uses_confirmation_actions_for_runtime_recommendation(monkeypatch):
    client, _ = router_chat_test_client(monkeypatch)

    monkeypatch.setattr(router_chat, "evaluate_user_context", lambda user_context: {"s_i": 0.6, "strategy": "A"})
    monkeypatch.setattr(
        router_chat,
        "_resolve_goal_for_strategy",
        lambda active_goal_id: _sample_goal(),
    )
    monkeypatch.setattr(
        router_chat,
        "get_chat_advice",
        lambda user_query, s_i: (_ for _ in ()).throw(AssertionError("generic advice should not be used")),
    )
    monkeypatch.setattr(
        router_chat,
        "build_at_risk_chat_proposal",
        lambda goal, user_context, actions, strategy: (
            "Your goal is off track. GoalPilot selected Plan A.",
            actions,
        ),
    )

    res = client.post(
        "/api/chat/message",
        json={
            "session_id": "runtime-ab-1",
            "message": "Help me recover this goal",
            "context": {"source_screen": "agent"},
        },
    )

    assert res.status_code == 200
    reply = res.json()["data"]["reply"]
    assert "Plan A" in reply["text"]
    assert [action["type"] for action in reply["actions"]] == ["accept", "cancel"]
    assert reply["actions"][0]["payload"]["action_type"] == "A"
    assert reply["actions"][0]["payload"]["action_payload"]["amount"] == 2_000_000


def router_chat_test_client(monkeypatch):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    app = FastAPI()
    app.include_router(router_chat.router, prefix="/api")

    session_state_store: dict[str, dict] = {}

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

    monkeypatch.setattr(router_chat, "ConversationHistory", FakeConversationHistory)
    monkeypatch.setattr(
        router_chat,
        "ContextRetriever",
        lambda: type("Retriever", (), {"fetch_user_financial_context": lambda self, user_id: {"monthly_spending": 1_000_000}})(),
    )
    monkeypatch.setattr(router_chat, "get_session_state", lambda session_id: session_state_store.get(session_id))
    monkeypatch.setattr(
        router_chat,
        "set_session_state",
        lambda session_id, state: session_state_store.__setitem__(session_id, dict(state)),
    )
    monkeypatch.setattr(router_chat, "clear_session_state", lambda session_id: session_state_store.pop(session_id, None))
    monkeypatch.setattr(router_chat, "sync_goals_with_user_context", lambda user_context: None)

    return TestClient(app), session_state_store
