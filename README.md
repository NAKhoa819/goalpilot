# GoalPilot

A 4-layer agentic finance application:
1. **Presentation Layer (UI)**: `frontend/`
2. **API & Logic Layer (API Gateway + Lambda)**: `backend-ingestion/`
3. **Intelligence Layer (Agentic Reasoning)**: `backend-agent/`
4. **Data Layer (External Context/Forecasts)**: `backend-forecast/`

## Components
- **frontend**: The presentation layer providing the user interface.
- **backend-ingestion** (BE#1): Data ingestion and user context persistence.
- **backend-agent** (BE#2): Agentic reasoning boundary with Bedrock Claude, prompt management, RAG glue, and decision tree mapping.
- **backend-forecast** (BE#3): Market data collection and forecasting service boundary.

## Development Workflow (Contract-First)
We use a contract-first approach. The frontend can be built concurrently with the backends using mock data based on our OpenAPI specification and Realtime Event definitions:
- **REST API Specs**: See `docs/api-contract/openapi.yaml`
- **Realtime Events**: See `docs/api-contract/events.md`
- **Shared Types**: See `shared/types/README.md`

## Running Locally (Placeholders)
To run the full stack locally:
1. Run Frontend: `cd frontend && npm run dev`
2. Run BE#1: `cd backend-ingestion && npm run dev`
3. Run BE#2: `cd backend-agent && npm run dev`
4. Run BE#3: `cd backend-forecast && npm run dev`
