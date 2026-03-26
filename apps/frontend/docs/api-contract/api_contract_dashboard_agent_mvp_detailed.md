# Detailed API Contract: Frontend <-> Backend

This document defines the API contract for the GoalPilot MVP across the dashboard, agent chat, goals, input data, and cash flow views.

## Scope

The MVP assumes:
- one frontend application
- one backend service
- application data managed inside the backend stack

Primary frontend areas:
1. Goal slider
2. Chat preview and agent tab
3. Input-data entry
4. Goal progress and replanning actions
5. Weekly cash flow view

Covered endpoints:
- `GET /api/dashboard`
- `GET /api/goals/{goal_id}/progress`
- `POST /api/chat/message`
- `GET /api/chat/session/{session_id}`
- `POST /api/goals`
- `POST /api/goals/{goal_id}/actions`
- `POST /api/input-data`
- `GET /api/cashflow/weekly`

---

## Response Conventions

### Success

```json
{
  "success": true,
  "message": "Optional message",
  "data": {}
}
```

### Error

```json
{
  "success": false,
  "message": "Human-readable error message",
  "error_code": "ERROR_CODE"
}
```

### Common Primitive Types

| Type | Meaning |
|---|---|
| `string` | Text value |
| `number` | Integer or float |
| `boolean` | `true` or `false` |
| `object` | JSON object |
| `array<object>` | Array of objects |
| `date` | `YYYY-MM-DD` |

### Common Enums

#### Goal status

| Value | Meaning |
|---|---|
| `on_track` | Goal is progressing as planned |
| `at_risk` | Goal is drifting or likely to miss target |
| `completed` | Goal is complete |
| `paused` | Goal is paused |

#### Warning level

| Value | Meaning |
|---|---|
| `info` | Informational |
| `warning` | Warning |
| `critical` | Critical warning |

#### Strategy selected

| Value | Meaning |
|---|---|
| `A` | Increase savings / budget correction |
| `B` | Extend deadline / realign goal |
| `None` | No remediation required |

#### Input source

| Value | Meaning |
|---|---|
| `manual` | User entered data manually |
| `ocr` | OCR extraction |
| `sms` | SMS-derived data |
| `file` | Imported file data |

---

## Reusable Data Objects

### GoalCard

Used in the dashboard goal slider.

| Field | Type | Required | Description |
|---|---|---:|---|
| `goal_id` | string | Yes | Goal identifier |
| `goal_name` | string | Yes | Goal display name |
| `target_amount` | number | Yes | Goal target amount |
| `target_date` | date | Yes | Goal deadline |
| `current_saved` | number | Yes | Current saved amount |
| `progress_percent` | number | Yes | Progress percentage |
| `status` | string | Yes | Goal status |

Example:

```json
{
  "goal_id": "g001",
  "goal_name": "Buy Laptop",
  "target_amount": 30000000,
  "target_date": "2026-12-01",
  "current_saved": 18000000,
  "progress_percent": 60,
  "status": "at_risk"
}
```

### ChatPreview

Used for the dashboard chat preview box.

| Field | Type | Required | Description |
|---|---|---:|---|
| `session_id` | string | Yes | Active chat session ID |
| `last_message` | string | Yes | Last message preview |
| `unread_count` | number | Yes | Number of unread messages |

### ChatAction

Structured action rendered as a button in chat.

| Field | Type | Required | Description |
|---|---|---:|---|
| `type` | string | Yes | Action type |
| `label` | string | Yes | Button label |
| `payload` | object | Yes | Action payload |

Supported action families:
- `create_goal`
- `accept`
- `cancel`
- `A`
- `B`
- `view_goal_progress`
- `open_input_data`
- `refresh_dashboard`

### ChatMessage

Used inside the agent chat view.

| Field | Type | Required | Description |
|---|---|---:|---|
| `message_id` | string | Yes | Message identifier |
| `role` | string | Yes | `user` or `assistant` |
| `text` | string | Yes | Message content |
| `actions` | array<object> | No | Optional action buttons |

### Plan A Payload

```json
{
  "goal_id": "g001",
  "strategy": "increase_savings",
  "amount": 1000000,
  "duration_months": 6
}
```

### Plan B Payload

```json
{
  "goal_id": "g001",
  "strategy": "extend_deadline",
  "months": 3,
  "new_target_date": "2027-03-01"
}
```

### ProgressGoal

Goal data returned by the progress endpoint.

| Field | Type | Required |
|---|---|---:|
| `goal_id` | string | Yes |
| `goal_name` | string | Yes |
| `target_amount` | number | Yes |
| `target_date` | date | Yes |
| `current_saved` | number | Yes |
| `remaining_amount` | number | Yes |
| `progress_percent` | number | Yes |
| `planned_eta` | date | Yes |
| `reprojected_eta` | date | Yes |
| `status` | string | Yes |

### RecommendationOptions

| Field | Type | Required | Description |
|---|---|---:|---|
| `recommended_actions` | array<string> | Yes | Human-readable recommendation strings |
| `plan_a_option` | object | No | Structured Plan A payload |
| `plan_b_option` | object | No | Structured Plan B payload |
| `deadline_extension_option` | object | No | Proposed deadline extension |
| `income_augmentation_option` | object | No | Proposed extra monthly savings |

### CashFlowPoint

```json
{
  "date": "2026-03-21",
  "income": 1200000,
  "expense": 400000,
  "net": 800000
}
```

---

## Endpoints

## `GET /api/dashboard`

Returns dashboard data for the goal slider, chat preview, and input actions.

### Response

```json
{
  "success": true,
  "data": {
    "goals": [
      {
        "goal_id": "g001",
        "goal_name": "Buy Laptop",
        "target_amount": 30000000,
        "target_date": "2026-12-01",
        "current_saved": 18000000,
        "progress_percent": 60,
        "status": "at_risk"
      }
    ],
    "active_goal_id": "g001",
    "chat_preview": {
      "session_id": "s001",
      "last_message": "Your laptop goal is currently off track.",
      "unread_count": 0
    },
    "input_actions": [
      {
        "type": "open_input_data",
        "label": "Add Data"
      }
    ]
  }
}
```

## `GET /api/goals/{goal_id}/progress`

Returns progress, analysis, recommendations, and UI copy for a single goal.

### Response

```json
{
  "success": true,
  "data": {
    "goal": {
      "goal_id": "g001",
      "goal_name": "Buy Laptop",
      "target_amount": 30000000,
      "target_date": "2026-12-01",
      "current_saved": 18000000,
      "remaining_amount": 12000000,
      "progress_percent": 60,
      "planned_eta": "2026-12-01",
      "reprojected_eta": "2027-03-01",
      "status": "at_risk"
    },
    "analysis": {
      "gap_detected": true,
      "gap_delta": 1200000,
      "gap_reason": "overspending",
      "confidence_score": 0.84,
      "strategy_selected": "A",
      "accepted_action_type": null,
      "accepted_action_payload": null,
      "requires_manual_verification": false
    },
    "recommendations": {
      "recommended_actions": [
        "Reduce discretionary spending",
        "Increase monthly savings"
      ],
      "plan_a_option": {
        "goal_id": "g001",
        "strategy": "increase_savings",
        "amount": 1000000,
        "duration_months": 6
      }
    },
    "ui": {
      "banner_message": "Your goal is currently at risk.",
      "warning_level": "warning",
      "cta_buttons": [
        "Review Recommended Plan",
        "Review Details"
      ]
    }
  }
}
```

## `POST /api/chat/message`

Posts a user chat message and returns the assistant reply.

### Request

```json
{
  "session_id": "s001",
  "message": "I want to buy a laptop for 30 million before 2026-11-10",
  "context": {
    "active_goal_id": null,
    "source_screen": "dashboard"
  }
}
```

### Response

```json
{
  "success": true,
  "data": {
    "session_id": "s001",
    "reply": {
      "message_id": "a_1234abcd",
      "role": "assistant",
      "text": "I understood the financial goal you described. If this looks right, tap Create Goal and I will save it for you.",
      "actions": [
        {
          "type": "create_goal",
          "label": "Create Goal",
          "payload": {
            "goal_name": "Buy Laptop",
            "goal_type": "purchase",
            "target_amount": 28169014,
            "target_date": "2026-11-10",
            "currency": "USD"
          }
        }
      ]
    }
  }
}
```

Notes:
- Car-goal flows may return follow-up questions instead of immediate actions.
- Assistant replies may include `accept` / `cancel` actions for replanning.

## `GET /api/chat/session/{session_id}`

Returns the full message history for a chat session.

### Response

```json
{
  "success": true,
  "data": {
    "session_id": "s001",
    "messages": [
      {
        "message_id": "u_1111aaaa",
        "role": "user",
        "text": "I want to buy a laptop."
      },
      {
        "message_id": "a_2222bbbb",
        "role": "assistant",
        "text": "When do you want to complete it?"
      }
    ]
  }
}
```

## `POST /api/goals`

Creates a goal record.

### Request

```json
{
  "goal_name": "Buy Laptop",
  "goal_type": "purchase",
  "target_amount": 28169014,
  "target_date": "2026-11-10",
  "currency": "USD",
  "created_from": "chat"
}
```

### Response

```json
{
  "success": true,
  "message": "Goal created successfully",
  "data": {
    "goal_id": "g_ab12cd34",
    "goal_name": "Buy Laptop",
    "progress_percent": 0,
    "status": "on_track"
  }
}
```

## `POST /api/goals/{goal_id}/actions`

Applies an accepted replanning action to a goal.

### Request

```json
{
  "session_id": "s001",
  "action": {
    "type": "accept",
    "label": "Apply Recommended Plan",
    "payload": {
      "goal_id": "g001",
      "action": "confirm_recommended_plan",
      "action_type": "A",
      "action_label": "Plan A - Save an extra $1,065,000/month",
      "action_payload": {
        "goal_id": "g001",
        "strategy": "increase_savings",
        "amount": 1000000,
        "duration_months": 6
      }
    }
  }
}
```

### Response

```json
{
  "success": true,
  "data": {
    "goal_id": "g001",
    "applied_action_type": "A",
    "should_refresh_dashboard": true,
    "reply": {
      "message_id": "a_3333cccc",
      "role": "assistant",
      "text": "Plan A is now active for Buy Laptop. Aim to save an extra $1,065,000 per month."
    }
  }
}
```

## `POST /api/input-data`

Imports user financial input data.

### Manual example

```json
{
  "source": "manual",
  "payload": {
    "monthly_income": 12000000,
    "current_balance": 8000000,
    "projected_savings": 3500000,
    "categories": [
      {
        "name": "dining",
        "current_month_spend": 2200000,
        "is_essential": false
      }
    ]
  }
}
```

### OCR example

```json
{
  "source": "ocr",
  "payload": {
    "transactions": [
      {
        "date": "2026-03-10",
        "amount": 250000,
        "description": "Restaurant",
        "category": "dining"
      }
    ]
  }
}
```

### Response

```json
{
  "success": true,
  "data": {
    "imported_count": 1,
    "affected_goals": [
      "g001"
    ],
    "should_refresh_dashboard": true
  }
}
```

## `GET /api/cashflow/weekly`

Returns weekly cash-flow data. May optionally filter by `goal_id`.

### Query parameters

| Name | Type | Required | Description |
|---|---|---:|---|
| `goal_id` | string | No | Optional goal filter |

### Response

```json
{
  "success": true,
  "data": {
    "period_start": "2026-03-15",
    "period_end": "2026-03-21",
    "points": [
      {
        "date": "2026-03-15",
        "income": 1200000,
        "expense": 400000,
        "net": 800000
      }
    ]
  }
}
```

---

## Error Examples

### Empty chat message

```json
{
  "success": false,
  "message": "Message cannot be empty.",
  "error_code": "EMPTY_MESSAGE"
}
```

### Missing goal

```json
{
  "success": false,
  "message": "Goal 'g999' not found.",
  "error_code": "GOAL_NOT_FOUND"
}
```

### Invalid target date

```json
{
  "success": false,
  "message": "target_date must be YYYY-MM-DD.",
  "error_code": "INVALID_TARGET_DATE"
}
```

### Invalid input source

```json
{
  "success": false,
  "message": "Unsupported input source.",
  "error_code": "INVALID_INPUT_SOURCE"
}
```
