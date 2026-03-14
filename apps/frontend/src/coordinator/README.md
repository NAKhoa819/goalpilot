# Coordinator Layer

Lớp trung gian giữa **Frontend** và **Backend API**.  
FE **chỉ gọi qua coordinator**, không gọi `fetch` trực tiếp.

---

## Cấu trúc

```
coordinator/
├── README.md              ← file này
├── types.ts               ← TypeScript interfaces cho toàn bộ API contract
├── mockData.ts            ← Dữ liệu giả (dùng khi BE chưa sẵn sàng)
├── dashboardCoordinator.ts  ← GET /api/dashboard
├── goalCoordinator.ts       ← GET /api/goals/{id}/progress, POST /api/goals
├── chatCoordinator.ts       ← POST /api/chat/message, GET /api/chat/session/{id}
├── inputDataCoordinator.ts  ← POST /api/input-data
├── cashFlowCoordinator.ts   ← GET /api/cashflow/weekly
└── index.ts               ← Re-export tất cả (entry point duy nhất)
```

---

## Cách dùng

Import từ `index.ts` — không import trực tiếp từ từng file:

```ts
import {
  getDashboard,
  getGoalProgress,
  createGoal,
  postChatMessage,
  getChatSession,
  postInputData,
  getCashFlow,
} from '@/coordinator';                    // hoặc './coordinator'

import type { GoalCard, DashboardResponse, CashFlowData } from '@/coordinator';
```

---

## Ví dụ từng endpoint

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
  message: 'Tôi muốn mua laptop 30 triệu',
  context: { active_goal_id: null, source_screen: 'dashboard' },
});
if (res.success) {
  const { reply } = res.data; // reply.text, reply.actions
}
```

### GET /api/chat/session/{session_id}
```ts
const res = await getChatSession('s001');
if (res.success) {
  const { messages } = res.data; // ChatMessage[]
}
```

### POST /api/goals
```ts
const res = await createGoal({
  goal_name: 'Buy Laptop',
  goal_type: 'purchase',
  target_amount: 30_000_000,
  target_date: '2026-11-10',
  currency: 'VND',
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
  // gọi lại getDashboard()
}
```

### GET /api/cashflow/weekly
```ts
// Lấy dữ liệu dòng tiền 7 ngày gần nhất (không lọc theo goal)
const res = await getCashFlow();

// Hoặc lọc theo goal cụ thể
const res = await getCashFlow('g001');

if (res.success) {
  const { period_start, period_end, points } = res.data;
  // points: CashFlowPoint[] — mỷi phần tử có { date, income, expense, net }
}
```

---

## Trạng thái hiện tại: Mock Mode

Tất cả functions đang trả **mock data** từ `mockData.ts`.  
Simulate network delay 300–600ms để FE test loading state.

### Swap sang BE thật

Mỗi function có `TODO` comment chỉ rõ đoạn cần thay:

```ts
// Ví dụ trong dashboardCoordinator.ts
// TODO: swap sang fetch thật khi BE sẵn sàng:
//   const res = await fetch('/api/dashboard');
//   return res.json();
```

Khi BE sẵn sàng: uncomment fetch, xóa mock return — **FE không cần sửa gì**.

---

## Mock data có sẵn

| ID | Goal | Status |
|---|---|---|
| `g001` | Buy Laptop | `at_risk` · 60% |
| `g002` | Emergency Fund | `on_track` · 75% |
| `g003` | Travel to Japan | `on_track` · 20% |

Session mặc định: `s001` — 2 messages (user + assistant có action `create_goal`).

---

## API Contract tham khảo

[`api_contract_dashboard_agent_mvp_detailed.md`](file:///d:/swin/swin2026/goalpilot/api_contract_dashboard_agent_mvp_detailed.md)
