# GoalPilot Intelligence Engine: Technical Reference

## Function Overview

### `intelligence/intelligence.py`

`calculate_metrics(profile: dict) -> dict`
- Computes `s_i` and `c_s` from summarized financial context.

`determine_strategy(s_i: float) -> str`
- Returns `A`, `B`, or `None` from the sustainability threshold.

### `intelligence/llm_gateway.py`

`get_model(provider: str | None = None)`
- Resolves the active LLM provider configured by environment variables.

`get_completion(messages: list, response_format=None, provider=None)`
- Sends prompt messages to the configured LLM and optionally enforces structured output.

`get_chat_advice(user_query: str, s_i: float) -> str`
- Generates chat advice using the current sustainability index.

### `agent_run.py`

`run(user_id: str, user_message: str) -> StrategyResponse`
- Fetches user context from the backend retriever, computes metrics, builds the system prompt, and returns a structured reasoning response.

## Data Integration

The current backend keeps user context and goal state in in-memory stores for MVP usage:
- `data/user_context_store.py`
- `data/goal_store.py`

`memory/retriever.py` reads from those stores and returns the compact financial context required by the intelligence layer.

## Testing Notes

The repo currently runs the FastAPI API from:
- `apps/backend/main.py`
- `apps/backend/main_api.py`

You can run the intelligence tests with:

```bash
cd apps/backend
..\..\venv\Scripts\python -m pytest intelligence/tests/test_api.py
```
