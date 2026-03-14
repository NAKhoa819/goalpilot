# Detailed API Contract — FE ↔ Backend (Dashboard + Agent + Input Data)

## 1. Scope

Tài liệu này định nghĩa API contract chi tiết cho MVP với kiến trúc:

- Frontend
- Một Backend service duy nhất
- Data/DB nằm nội bộ backend

Dashboard hiện có 3 vùng chính:

1. Goal slider / thanh trượt goal
2. Chat preview, bấm vào để sang tab Agent
3. Nút nhập dữ liệu

Contract hiện chốt theo 7 endpoint:

- `GET /api/dashboard`
- `GET /api/goals/{goal_id}/progress`
- `POST /api/chat/message`
- `GET /api/chat/session/{session_id}`
- `POST /api/goals`
- `POST /api/input-data`
- `GET /api/cashflow/weekly`

---

## 2. General conventions

### 2.1 Base response format

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

### 2.2 Data types used in this document

| Type | Meaning |
|---|---|
| `string` | Chuỗi ký tự |
| `number` | Số, có thể là integer hoặc float |
| `boolean` | `true` / `false` |
| `array<object>` | Mảng object |
| `object` | Đối tượng JSON |
| `date` | Chuỗi ngày dạng `YYYY-MM-DD` |
| `datetime` | Chuỗi thời gian ISO 8601 |

### 2.3 Common enums

#### Goal status
| Value | Meaning |
|---|---|
| `on_track` | Goal đang đúng kế hoạch |
| `at_risk` | Goal có nguy cơ trễ / lệch |
| `completed` | Goal đã hoàn thành |
| `paused` | Goal đang tạm dừng |

#### Warning level
| Value | Meaning |
|---|---|
| `info` | Thông báo nhẹ |
| `warning` | Cảnh báo |
| `critical` | Cảnh báo nghiêm trọng |

#### Strategy selected
| Value | Meaning |
|---|---|
| `A` | Cost optimization / budget adjustment |
| `B` | Goal adjustment / extend deadline / income augmentation |

#### Input source
| Value | Meaning |
|---|---|
| `manual` | Người dùng nhập tay |
| `ocr` | Trích xuất từ OCR |
| `sms` | Dữ liệu từ SMS |
| `file` | Dữ liệu từ file import |

---

## 3. Reusable data objects

## 3.1 GoalCard
Dùng cho goal slider trên dashboard.

| Field | Type | Required | Description | Example |
|---|---|---:|---|---|
| `goal_id` | string | Yes | ID của goal | `g001` |
| `goal_name` | string | Yes | Tên goal | `Buy Laptop` |
| `target_amount` | number | Yes | Số tiền mục tiêu | `30000000` |
| `target_date` | date | Yes | Hạn hoàn thành goal | `2026-12-01` |
| `current_saved` | number | Yes | Số tiền đã tích lũy | `18000000` |
| `progress_percent` | number | Yes | Tiến độ phần trăm | `60` |
| `status` | string | Yes | Trạng thái goal | `at_risk` |

### Example
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

---

## 3.2 ChatPreview
Dùng cho ô chat trên dashboard.

| Field | Type | Required | Description | Example |
|---|---|---:|---|---|
| `session_id` | string | Yes | ID phiên chat hiện tại | `s001` |
| `last_message` | string | Yes | Tin nhắn gần nhất để preview | `Your laptop goal is currently off track.` |
| `unread_count` | number | Yes | Số tin nhắn chưa đọc | `0` |

---

## 3.3 ChatAction
Action có cấu trúc để FE render nút trong chat.

| Field | Type | Required | Description | Example |
|---|---|---:|---|---|
| `type` | string | Yes | Loại action | `create_goal` |
| `label` | string | Yes | Text hiển thị trên nút | `Create Goal` |
| `payload` | object | Yes | Dữ liệu đi kèm action | `{...}` |

### Supported action types
| Action type | Meaning |
|---|---|
| `create_goal` | Tạo goal mới |
| `view_goal_progress` | Mở chi tiết tiến trình goal |
| `open_input_data` | Mở form nhập dữ liệu |
| `refresh_dashboard` | Yêu cầu FE refresh dashboard |

---

## 3.4 ChatMessage
Dùng trong tab Agent.

| Field | Type | Required | Description | Example |
|---|---|---:|---|---|
| `message_id` | string | Yes | ID tin nhắn | `m002` |
| `role` | string | Yes | `user` hoặc `assistant` | `assistant` |
| `text` | string | Yes | Nội dung tin nhắn | `Tôi có thể tạo goal này cho bạn.` |
| `actions` | array<object> | No | Danh sách action kèm theo | `[{...}]` |

### Example
```json
{
  "message_id": "m002",
  "role": "assistant",
  "text": "Tôi có thể tạo goal này cho bạn.",
  "actions": [
    {
      "type": "create_goal",
      "label": "Create Goal",
      "payload": {
        "goal_name": "Buy Laptop",
        "goal_type": "purchase",
        "target_amount": 30000000,
        "target_date": "2026-11-10"
      }
    }
  ]
}
```

---

## 3.5 RecommendationOptions
Dùng trong phần recommendation của progress.

| Field | Type | Required | Description | Example |
|---|---|---:|---|---|
| `recommended_actions` | array<string> | Yes | Danh sách gợi ý text ngắn | `["Extend deadline", "Increase monthly income target"]` |
| `deadline_extension_option` | object | No | Phương án kéo dài deadline | `{...}` |
| `income_augmentation_option` | object | No | Phương án tăng thu nhập | `{...}` |

### deadline_extension_option
| Field | Type | Required | Description | Example |
|---|---|---:|---|---|
| `new_target_date` | date | Yes | Deadline mới đề xuất | `2027-03-01` |
| `delay_days` | number | Yes | Số ngày dời | `90` |

### income_augmentation_option
| Field | Type | Required | Description | Example |
|---|---|---:|---|---|
| `required_extra_income_per_month` | number | Yes | Thu nhập tăng thêm cần thiết mỗi tháng | `2500000` |

---

## 3.6 ProgressGoal
Khối dữ liệu goal trong endpoint progress.

| Field | Type | Required | Description | Example |
|---|---|---:|---|---|
| `goal_id` | string | Yes | ID goal | `g001` |
| `goal_name` | string | Yes | Tên goal | `Buy Laptop` |
| `target_amount` | number | Yes | Số tiền mục tiêu | `30000000` |
| `target_date` | date | Yes | Deadline gốc | `2026-12-01` |
| `current_saved` | number | Yes | Đã tích lũy hiện tại | `18000000` |
| `remaining_amount` | number | Yes | Số tiền còn thiếu | `12000000` |
| `progress_percent` | number | Yes | Tiến độ | `60` |
| `planned_eta` | date | Yes | ETA kế hoạch ban đầu | `2026-12-01` |
| `reprojected_eta` | date | Yes | ETA sau khi tính lại | `2027-01-15` |
| `status` | string | Yes | Trạng thái goal | `at_risk` |

---

## 3.7 ProgressAnalysis
Khối dữ liệu phân tích của agent.

| Field | Type | Required | Description | Example |
|---|---|---:|---|---|
| `gap_detected` | boolean | Yes | Có phát hiện lệch kế hoạch hay không | `true` |
| `gap_delta` | number | Yes | Mức chênh lệch hiện tại | `1500000` |
| `gap_reason` | string | Yes | Lý do chính gây lệch | `market_price_increase` |
| `confidence_score` | number | Yes | Độ tin cậy của agent | `0.86` |
| `strategy_selected` | string | Yes | Chiến lược backend chọn | `B` |
| `requires_manual_verification` | boolean | Yes | Có cần xác minh tay không | `false` |

### Supported gap_reason values
| Value | Meaning |
|---|---|
| `market_price_increase` | Giá mục tiêu tăng |
| `overspending` | Người dùng chi vượt kế hoạch |
| `income_drop` | Thu nhập giảm |
| `mixed` | Nhiều nguyên nhân kết hợp |

---

## 3.8 ProgressUI
Dữ liệu FE dùng để hiển thị UI state.

| Field | Type | Required | Description | Example |
|---|---|---:|---|---|
| `banner_message` | string | Yes | Câu thông báo nổi bật | `Your goal is currently off track due to market price increase.` |
| `warning_level` | string | Yes | Mức độ cảnh báo | `warning` |
| `cta_buttons` | array<string> | Yes | Danh sách CTA FE hiển thị | `["Extend Deadline", "Increase Income Target", "Review Details"]` |

---

## 4. Endpoint definitions

# 4.1 GET /api/dashboard

## Purpose
Load toàn bộ dữ liệu cần để render dashboard lần đầu.

## Request
Không có request body.

## Response schema

### Root fields
| Field | Type | Required | Description |
|---|---|---:|---|
| `success` | boolean | Yes | Trạng thái request |
| `message` | string | No | Thông báo tùy chọn |
| `data` | object | Yes | Payload chính |

### data fields
| Field | Type | Required | Description |
|---|---|---:|---|
| `goals` | array<object> | Yes | Danh sách goal card |
| `active_goal_id` | string | Yes | Goal FE chọn mặc định |
| `chat_preview` | object | Yes | Preview ô chat |
| `input_actions` | array<object> | Yes | Danh sách action nhập dữ liệu |

### input_actions item
| Field | Type | Required | Description | Example |
|---|---|---:|---|---|
| `type` | string | Yes | Loại input action | `manual_input` |
| `label` | string | Yes | Text hiển thị | `Enter Data` |

## Example response
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
      },
      {
        "goal_id": "g002",
        "goal_name": "Emergency Fund",
        "target_amount": 20000000,
        "target_date": "2026-09-01",
        "current_saved": 15000000,
        "progress_percent": 75,
        "status": "on_track"
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
        "type": "manual_input",
        "label": "Enter Data"
      },
      {
        "type": "ocr_upload",
        "label": "Scan Receipt"
      }
    ]
  }
}
```

## FE usage
- Render goal slider
- Render chat preview
- Render nút nhập dữ liệu
- Dùng `active_goal_id` để quyết định goal đầu tiên

---

# 4.2 GET /api/goals/{goal_id}/progress

## Purpose
Load dữ liệu tiến trình chi tiết của một goal.

## Path params
| Param | Type | Required | Description | Example |
|---|---|---:|---|---|
| `goal_id` | string | Yes | ID goal cần lấy progress | `g001` |

## Request
Không có request body.

## Response schema

### data fields
| Field | Type | Required | Description |
|---|---|---:|---|
| `goal` | object | Yes | Thông tin tiến trình goal |
| `analysis` | object | Yes | Kết quả phân tích agent |
| `recommendations` | object | Yes | Gợi ý hành động |
| `ui` | object | Yes | UI state cho FE |

## Example response
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
      "reprojected_eta": "2027-01-15",
      "status": "at_risk"
    },
    "analysis": {
      "gap_detected": true,
      "gap_delta": 1500000,
      "gap_reason": "market_price_increase",
      "confidence_score": 0.86,
      "strategy_selected": "B",
      "requires_manual_verification": false
    },
    "recommendations": {
      "recommended_actions": [
        "Extend deadline",
        "Increase monthly income target"
      ],
      "deadline_extension_option": {
        "new_target_date": "2027-03-01",
        "delay_days": 90
      },
      "income_augmentation_option": {
        "required_extra_income_per_month": 2500000
      }
    },
    "ui": {
      "banner_message": "Your goal is currently off track due to market price increase.",
      "warning_level": "warning",
      "cta_buttons": [
        "Extend Deadline",
        "Increase Income Target",
        "Review Details"
      ]
    }
  }
}
```

## Error cases
| error_code | Meaning |
|---|---|
| `GOAL_NOT_FOUND` | Không tìm thấy goal |
| `INVALID_GOAL_ID` | goal_id sai định dạng |

## FE usage
- Update progress bar
- Update banner
- Hiển thị reason, confidence, strategy
- Hiển thị recommendation cards

---

# 4.3 POST /api/chat/message

## Purpose
Gửi tin nhắn user cho agent và nhận reply.

## Request schema

| Field | Type | Required | Description | Example |
|---|---|---:|---|---|
| `session_id` | string | Yes | ID phiên chat hiện tại | `s001` |
| `message` | string | Yes | Nội dung user nhập | `Tôi muốn mua laptop giá 30 triệu trong 8 tháng tới` |
| `context` | object | No | Context để backend hiểu màn hình hiện tại | `{...}` |

### context fields
| Field | Type | Required | Description | Example |
|---|---|---:|---|---|
| `active_goal_id` | string \| null | No | Goal đang active trên dashboard | `null` |
| `source_screen` | string | No | Màn hình gọi request | `dashboard` |

## Example request
```json
{
  "session_id": "s001",
  "message": "Tôi muốn mua laptop giá 30 triệu trong 8 tháng tới",
  "context": {
    "active_goal_id": null,
    "source_screen": "dashboard"
  }
}
```

## Response schema

### data fields
| Field | Type | Required | Description |
|---|---|---:|---|
| `session_id` | string | Yes | ID phiên chat |
| `reply` | object | Yes | Tin nhắn trả lời của assistant |

### reply fields
| Field | Type | Required | Description | Example |
|---|---|---:|---|---|
| `message_id` | string | Yes | ID tin nhắn trả lời | `m002` |
| `role` | string | Yes | Luôn là `assistant` | `assistant` |
| `text` | string | Yes | Nội dung trả lời | `Tôi đã hiểu mục tiêu của bạn...` |
| `actions` | array<object> | No | Action FE có thể render | `[{...}]` |

## Example response
```json
{
  "success": true,
  "data": {
    "session_id": "s001",
    "reply": {
      "message_id": "m002",
      "role": "assistant",
      "text": "Tôi đã hiểu mục tiêu của bạn. Tôi có thể tạo goal mua laptop 30 triệu với hạn hoàn thành sau 8 tháng.",
      "actions": [
        {
          "type": "create_goal",
          "label": "Create Goal",
          "payload": {
            "goal_name": "Buy Laptop",
            "goal_type": "purchase",
            "target_amount": 30000000,
            "target_date": "2026-11-10"
          }
        }
      ]
    }
  }
}
```

## Error cases
| error_code | Meaning |
|---|---|
| `INVALID_SESSION_ID` | session_id không hợp lệ |
| `EMPTY_MESSAGE` | message rỗng |
| `AGENT_PROCESSING_FAILED` | agent xử lý lỗi |

## FE usage
- Append tin nhắn user
- Append reply assistant
- Render button từ `actions`

---

# 4.4 GET /api/chat/session/{session_id}

## Purpose
Load lịch sử chat khi user mở tab Agent.

## Path params
| Param | Type | Required | Description | Example |
|---|---|---:|---|---|
| `session_id` | string | Yes | ID phiên chat | `s001` |

## Response schema

### data fields
| Field | Type | Required | Description |
|---|---|---:|---|
| `session_id` | string | Yes | ID phiên chat |
| `messages` | array<object> | Yes | Danh sách tin nhắn |

## Example response
```json
{
  "success": true,
  "data": {
    "session_id": "s001",
    "messages": [
      {
        "message_id": "m001",
        "role": "user",
        "text": "Tôi muốn mua laptop giá 30 triệu trong 8 tháng tới"
      },
      {
        "message_id": "m002",
        "role": "assistant",
        "text": "Tôi có thể tạo goal này cho bạn.",
        "actions": [
          {
            "type": "create_goal",
            "label": "Create Goal",
            "payload": {
              "goal_name": "Buy Laptop",
              "goal_type": "purchase",
              "target_amount": 30000000,
              "target_date": "2026-11-10"
            }
          }
        ]
      }
    ]
  }
}
```

## Error cases
| error_code | Meaning |
|---|---|
| `SESSION_NOT_FOUND` | Không tìm thấy phiên chat |
| `INVALID_SESSION_ID` | session_id sai định dạng |

---

# 4.5 POST /api/goals

## Purpose
Tạo goal mới.

## Request schema

| Field | Type | Required | Description | Example |
|---|---|---:|---|---|
| `goal_name` | string | Yes | Tên goal | `Buy Laptop` |
| `goal_type` | string | Yes | Loại goal | `purchase` |
| `target_amount` | number | Yes | Số tiền mục tiêu | `30000000` |
| `target_date` | date | Yes | Deadline goal | `2026-11-10` |
| `currency` | string | Yes | Loại tiền | `VND` |
| `created_from` | string | No | Nguồn tạo goal | `chat` |

### Supported goal_type values
| Value | Meaning |
|---|---|
| `purchase` | Mua sắm |
| `saving` | Tích lũy |
| `emergency_fund` | Quỹ khẩn cấp |
| `custom` | Goal tùy chỉnh |

## Example request
```json
{
  "goal_name": "Buy Laptop",
  "goal_type": "purchase",
  "target_amount": 30000000,
  "target_date": "2026-11-10",
  "currency": "VND",
  "created_from": "chat"
}
```

## Response schema

### data fields
| Field | Type | Required | Description | Example |
|---|---|---:|---|---|
| `goal_id` | string | Yes | ID goal vừa tạo | `g003` |
| `goal_name` | string | Yes | Tên goal | `Buy Laptop` |
| `progress_percent` | number | Yes | Tiến độ ban đầu | `0` |
| `status` | string | Yes | Trạng thái ban đầu | `on_track` |

## Example response
```json
{
  "success": true,
  "message": "Goal created successfully",
  "data": {
    "goal_id": "g003",
    "goal_name": "Buy Laptop",
    "progress_percent": 0,
    "status": "on_track"
  }
}
```

## Error cases
| error_code | Meaning |
|---|---|
| `MISSING_REQUIRED_FIELD` | Thiếu field bắt buộc |
| `INVALID_TARGET_AMOUNT` | target_amount không hợp lệ |
| `INVALID_TARGET_DATE` | target_date không hợp lệ |

## FE usage
- Sau khi tạo goal thành công, refresh dashboard
- Có thể scroll goal slider tới goal mới

---

# 4.6 POST /api/input-data

## Purpose
Nhập dữ liệu từ dashboard.

## Request schema

| Field | Type | Required | Description | Example |
|---|---|---:|---|---|
| `source` | string | Yes | Nguồn dữ liệu nhập | `manual` |
| `payload` | object | Yes | Nội dung dữ liệu nhập | `{...}` |

## Manual input payload example
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

## OCR input payload example
```json
{
  "source": "ocr",
  "payload": {
    "transactions": [
      {
        "date": "2026-03-10",
        "amount": 250000,
        "description": "Restaurant bill",
        "category": "dining"
      }
    ]
  }
}
```

## Suggested payload schemas

### Manual payload
| Field | Type | Required | Description | Example |
|---|---|---:|---|---|
| `monthly_income` | number | No | Thu nhập hàng tháng | `12000000` |
| `current_balance` | number | No | Số dư hiện tại | `8000000` |
| `projected_savings` | number | No | Khả năng tiết kiệm dự phóng | `3500000` |
| `categories` | array<object> | No | Thống kê theo danh mục | `[{...}]` |

### Manual category item
| Field | Type | Required | Description | Example |
|---|---|---:|---|---|
| `name` | string | Yes | Tên danh mục | `dining` |
| `current_month_spend` | number | Yes | Chi tiêu tháng hiện tại | `2200000` |
| `is_essential` | boolean | Yes | Có phải chi thiết yếu không | `false` |

### OCR/SMS/file transaction item
| Field | Type | Required | Description | Example |
|---|---|---:|---|---|
| `date` | date | Yes | Ngày giao dịch | `2026-03-10` |
| `amount` | number | Yes | Số tiền giao dịch | `250000` |
| `description` | string | No | Mô tả giao dịch | `Restaurant bill` |
| `category` | string | No | Danh mục gán cho giao dịch | `dining` |

## Response schema

### data fields
| Field | Type | Required | Description | Example |
|---|---|---:|---|---|
| `imported_count` | number | Yes | Số bản ghi đã nhập | `1` |
| `affected_goals` | array<string> | Yes | Danh sách goal bị ảnh hưởng | `["g001", "g002"]` |
| `should_refresh_dashboard` | boolean | Yes | FE có nên reload dashboard không | `true` |

## Example response
```json
{
  "success": true,
  "message": "Input data processed successfully",
  "data": {
    "imported_count": 1,
    "affected_goals": ["g001", "g002"],
    "should_refresh_dashboard": true
  }
}
```

## Error cases
| error_code | Meaning |
|---|---|
| `INVALID_INPUT_SOURCE` | source không hợp lệ |
| `INVALID_PAYLOAD` | payload sai cấu trúc |
| `NO_VALID_RECORDS` | Không có record hợp lệ để import |

## FE usage
- Thông báo nhập dữ liệu thành công/thất bại
- Nếu `should_refresh_dashboard = true` thì gọi lại dashboard

---

# 4.7 GET /api/cashflow/weekly

## Purpose
Lấy dữ liệu dòng tiền (income / expense) trong **7 ngày gần nhất** để render biểu đồ Cash Flow trên dashboard.

## Query params
| Param | Type | Required | Description | Example |
|---|---|---:|---|---|
| `goal_id` | string | No | Lọc dữ liệu theo goal cụ thể | `g001` |

## Request
Không có request body.

## Response schema

### data fields
| Field | Type | Required | Description |
|---|---|---:|---|
| `period_start` | date | Yes | Ngày đầu tuần (YYYY-MM-DD) |
| `period_end` | date | Yes | Ngày cuối tuần (YYYY-MM-DD) |
| `points` | array\<object\> | Yes | Dữ liệu dòng tiền từng ngày |

### points item (CashFlowPoint)
| Field | Type | Required | Description | Example |
|---|---|---:|---|---|
| `date` | date | Yes | Ngày cụ thể | `2026-03-08` |
| `income` | number | Yes | Tổng thu trong ngày | `3000000` |
| `expense` | number | Yes | Tổng chi trong ngày | `750000` |
| `net` | number | Yes | income − expense (tính sẵn) | `2250000` |

## Example response
```json
{
  "success": true,
  "data": {
    "period_start": "2026-03-08",
    "period_end": "2026-03-14",
    "points": [
      { "date": "2026-03-08", "income": 0,       "expense": 320000, "net": -320000 },
      { "date": "2026-03-09", "income": 3000000, "expense": 750000, "net": 2250000 },
      { "date": "2026-03-10", "income": 0,       "expense": 480000, "net": -480000 },
      { "date": "2026-03-11", "income": 500000,  "expense": 200000, "net":  300000 },
      { "date": "2026-03-12", "income": 0,       "expense": 650000, "net": -650000 },
      { "date": "2026-03-13", "income": 4000000, "expense": 900000, "net": 3100000 },
      { "date": "2026-03-14", "income": 0,       "expense": 410000, "net": -410000 }
    ]
  }
}
```

## Error cases
| error_code | Meaning |
|---|---|
| `INVALID_GOAL_ID` | goal_id không hợp lệ |
| `NO_DATA_AVAILABLE` | Chưa có dữ liệu giao dịch trong tuần |

## FE usage
- Render biểu đồ cột / đường theo `points`
- Trục X: `date` (hiển thị ngày trong tuần, ví dụ T2, T3…)
- Trục Y: giá trị VND
- Vẽ 2 series: `income` (xanh) và `expense` (đỏ), hoặc dùng `net` cho line chart
- Hiển thị `period_start` → `period_end` làm tiêu đề tuần

---

## 5. Suggested FE flows

### Flow 1 — Open dashboard
1. FE gọi `GET /api/dashboard`
2. Render goal slider
3. Render chat preview
4. Render input button

### Flow 2 — Slide to another goal
1. FE lấy `goal_id`
2. Gọi `GET /api/goals/{goal_id}/progress`
3. Update progress region

### Flow 3 — Open Agent tab
1. FE lấy `session_id` từ `chat_preview`
2. Gọi `GET /api/chat/session/{session_id}`
3. Render message list

### Flow 4 — User enters goal in chat
1. FE gọi `POST /api/chat/message`
2. Backend trả `text + actions`
3. FE render nút từ `actions`
4. User bấm `Create Goal`
5. FE gọi `POST /api/goals`
6. FE refresh dashboard

### Flow 5 — User imports data
1. FE mở form / upload
2. Gửi `POST /api/input-data`
3. Nếu `should_refresh_dashboard = true`, gọi lại `GET /api/dashboard`

---

## 6. Final endpoint summary

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/dashboard` | Load toàn bộ dữ liệu dashboard |
| GET | `/api/goals/{goal_id}/progress` | Load tiến trình chi tiết của một goal |
| POST | `/api/chat/message` | Gửi tin nhắn cho agent |
| GET | `/api/chat/session/{session_id}` | Load lịch sử chat |
| POST | `/api/goals` | Tạo goal |
| POST | `/api/input-data` | Nhập dữ liệu |

---

## 7. Notes for implementation

- Backend có thể code chung trong một service duy nhất
- Data layer nằm trong backend, FE không cần biết chi tiết DB
- FE chỉ bám theo contract FE ↔ Backend
- Nếu mở rộng sau này, có thể thêm:
  - `POST /api/goals/{goal_id}/actions`
  - `GET /api/goals`
  - realtime event stream
  - auth / user profile
