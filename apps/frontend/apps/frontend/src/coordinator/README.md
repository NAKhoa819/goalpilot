# Coordinator Layer

The coordinator layer sits between the **Frontend** and the **Backend API**.
The frontend should call the coordinator only, not `fetch` directly.

---

## Structure

```text
coordinator/
|-- README.md                <- this file
|-- types.ts                 <- TypeScript interfaces for the API contract
|-- mockData.ts              <- Mock data used before the backend is fully connected
|-- dashboardCoordinator.ts  <- GET /api/dashboard
|-- goalCoordinator.ts       <- GET /api/goals/{id}/progress, POST /api/goals
|-- chatCoordinator.ts       <- POST /api/chat/message, GET /api/chat/session/{id}
|-- inputDataCoordinator.ts  <- POST /api/input-data
|-- cashFlowCoordinator.ts   <- GET /api/cashflow/weekly
`-- index.ts                 <- Single re-export entry point
```

---

## Usage

Import from `index.ts` instead of importing from each file directly:

```ts
import {
  getDashboard,
  getGoalProgress,
  createGoal,
  postChatMessage,
  getChatSession,
  postInputData,
  getCashFlow,
} from '@/coordinator';

import type { GoalCard, DashboardResponse, CashFlowData } from '@/coordinator';
```

---

## Endpoint Examples

### GET /api/dashboard

```ts
const res = await getDashboard();
if (res.success) {
  const { goals, active_goal_id, chat_preview } = res.data;
}
```

### GET /api/goals/{goal_id}/progress

```ts
const res = await getGoalProgress('g001');
if (res.success) {
  const { goal, analysis, recommendations, ui } = res.data;
}
```

### POST /api/chat/message

```ts
const res = await postChatMessage({
  session_id: 's001',
  message: 'I want to buy a laptop for 30 million',
  context: { active_goal_id: null, source_screen: 'dashboard' },
});

if (res.success) {
  const { reply } = res.data;
}
```

### GET /api/chat/session/{session_id}

```ts
const res = await getChatSession('s001');
if (res.success) {
  const { messages } = res.data;
}
```

### POST /api/goals

```ts
const res = await createGoal({
  goal_name: 'Buy Laptop',
  goal_type: 'purchase',
  target_amount: 30_000_000,
  target_date: '2026-11-10',
  currency: 'USD',
  created_from: 'chat',
});

if (res.success) {
  const { goal_id } = res.data;
}
```

### POST /api/input-data

```ts
const res = await postInputData({
  source: 'manual',
  payload: {
    monthly_income: 12_000_000,
    current_balance: 8_000_000,
  },
});

if (res.success && res.data.should_refresh_dashboard) {
  // call getDashboard() again
}
```

### GET /api/cashflow/weekly

```ts
const res = await getCashFlow();

const filtered = await getCashFlow('g001');

if (res.success) {
  const { period_start, period_end, points } = res.data;
}
```

---

## Current State: Mock Mode

All coordinator functions currently return mock data from `mockData.ts`.
They simulate a 300-600ms network delay so the frontend can test loading states.

### Switching To Real Backend Calls

Each function already includes a `TODO` comment showing where to replace the mock implementation with a real fetch call:

```ts
// Example in dashboardCoordinator.ts
// TODO: swap to real fetch when BE is ready:
//   const res = await fetch('/api/dashboard');
//   return res.json();
```

Once the backend is ready, uncomment the real fetch call and remove the mock return. The frontend screens should not need structural changes.

---

## Available Mock Data

| ID | Goal | Status |
|---|---|---|
| `g001` | Buy Laptop | `at_risk` - 60% |
| `g002` | Emergency Fund | `on_track` - 75% |
| `g003` | Travel to Japan | `on_track` - 20% |

Default session: `s001` with two sample messages, including one assistant reply with a `create_goal` action.

---

## Related Contract

See the detailed API contract in [api_contract_dashboard_agent_mvp_detailed.md](/d:/swin/swin2026/goalpilot/apps/frontend/docs/api-contract/api_contract_dashboard_agent_mvp_detailed.md).
