# Frontend MVP Documentation

## Environment Requirements

- Node.js 18+ recommended
- Expo CLI
- Expo Go on a physical device, or an Android/iOS simulator

## Run Commands

Open a terminal in the frontend project and run:

```bash
# 1. Install dependencies
npm install

# 2. Start the Expo server
npx expo start

# 3. Clear cache if you hit UI or dependency issues
npx expo start -c
```

## Main Project Structure

The frontend is built with React Native (Expo) and TypeScript.

```text
src/
|-- components/
|   |-- ActionButtons/    # Neon action buttons such as Plan A, Plan B, Accept
|   |-- ChatBubble/       # User and assistant chat bubbles
|   `-- FinancialChart/   # Cash flow chart with liquid-glass styling
|-- screens/
|   |-- AgentScreen/      # Main AI chat screen
|   `-- DashboardScreen/  # Overview screen with chart and goal cards
|-- coordinator/
|   |-- types.ts          # Important API contract interfaces
|   |-- mockData.ts       # Mock chat, replan, and cash flow data
|   `-- chatCoordinator.ts
`-- theme.ts              # Colors, gradients, and shared visual tokens
```

## Data Flow

### A. Load Chat History

File: `chatCoordinator.ts`
Function: `getChatSession(sessionId)`

Current state:
- Returns static data from `mockData.ts`

Backend integration target:
- Replace with `GET /api/chat/session`

### B. Send Text Messages

File: `chatCoordinator.ts`
Function: `postChatMessage(payload)`

Current state:
- Accepts user text
- waits about 600ms
- returns a mock assistant reply

Backend integration target:
- Replace with `POST /api/chat/message`

### C. Handle Action Buttons

File: `chatCoordinator.ts`
Function: `handleActionSelection(action: ChatAction)`

Behavior:
- The UI passes the full action object, not only an ID
- The action includes both `type` and detailed `payload`

Current state:
- Logs the outgoing payload with `console.log`

Backend integration target:
- Send `action.payload` directly to the related goal-adjustment API

Example payload:

```ts
{
  strategy: 'increase_savings',
  amount: 3000000
}
```

## Notes

- The frontend currently supports mock mode for backend-independent UI work.
- The coordinator layer is the intended integration boundary.
- Once backend APIs are ready, swap the mock coordinator implementations for real network calls.
