// ============================================================
// Mock Data — Dữ liệu giả cho coordinator
// Dựa theo: api_contract_dashboard_agent_mvp_detailed.md
// ============================================================

import type {
  DashboardData,
  GoalProgressData,
  ChatMessageData,
  ChatSessionData,
  CreateGoalData,
  InputDataData,
  CashFlowData,
} from './types';

// ----------------------------------------------------------
// Mock: GET /api/dashboard
// ----------------------------------------------------------
export const MOCK_DASHBOARD: DashboardData = {
  goals: [
    {
      goal_id: 'g001',
      goal_name: 'Buy Laptop',
      target_amount: 30_000_000,
      target_date: '2026-12-01',
      current_saved: 18_000_000,
      progress_percent: 60,
      status: 'at_risk',
    },
    {
      goal_id: 'g002',
      goal_name: 'Emergency Fund',
      target_amount: 20_000_000,
      target_date: '2026-09-01',
      current_saved: 15_000_000,
      progress_percent: 75,
      status: 'on_track',
    },
    {
      goal_id: 'g003',
      goal_name: 'Travel to Japan',
      target_amount: 25_000_000,
      target_date: '2027-04-01',
      current_saved: 5_000_000,
      progress_percent: 20,
      status: 'on_track',
    },
  ],
  active_goal_id: 'g001',
  chat_preview: {
    session_id: 's001',
    last_message: 'Your laptop goal is currently off track.',
    unread_count: 1,
  },
  input_actions: [
    { type: 'manual_input', label: 'Enter Data' },
    { type: 'ocr_upload', label: 'Scan Receipt' },
  ],
};

// ----------------------------------------------------------
// Mock: GET /api/goals/{goal_id}/progress  (default: g001)
// ----------------------------------------------------------
export const MOCK_GOAL_PROGRESS: GoalProgressData = {
  goal: {
    goal_id: 'g001',
    goal_name: 'Buy Laptop',
    target_amount: 30_000_000,
    target_date: '2026-12-01',
    current_saved: 18_000_000,
    remaining_amount: 12_000_000,
    progress_percent: 60,
    planned_eta: '2026-12-01',
    reprojected_eta: '2027-01-15',
    status: 'at_risk',
  },
  analysis: {
    gap_detected: true,
    gap_delta: 1_500_000,
    gap_reason: 'market_price_increase',
    confidence_score: 0.86,
    strategy_selected: 'B',
    requires_manual_verification: false,
  },
  recommendations: {
    recommended_actions: ['Extend deadline', 'Increase monthly income target'],
    deadline_extension_option: {
      new_target_date: '2027-03-01',
      delay_days: 90,
    },
    income_augmentation_option: {
      required_extra_income_per_month: 2_500_000,
    },
  },
  ui: {
    banner_message:
      'Your goal is currently off track due to market price increase.',
    warning_level: 'warning',
    cta_buttons: ['Extend Deadline', 'Increase Income Target', 'Review Details'],
  },
};

/** Per-goal overrides để mock đa goal */
export const MOCK_GOAL_PROGRESS_MAP: Record<string, GoalProgressData> = {
  g001: MOCK_GOAL_PROGRESS,
  g002: {
    goal: {
      goal_id: 'g002',
      goal_name: 'Emergency Fund',
      target_amount: 20_000_000,
      target_date: '2026-09-01',
      current_saved: 15_000_000,
      remaining_amount: 5_000_000,
      progress_percent: 75,
      planned_eta: '2026-09-01',
      reprojected_eta: '2026-08-15',
      status: 'on_track',
    },
    analysis: {
      gap_detected: false,
      gap_delta: 0,
      gap_reason: 'overspending',
      confidence_score: 0.92,
      strategy_selected: 'A',
      requires_manual_verification: false,
    },
    recommendations: {
      recommended_actions: ['Keep current pace', 'Review monthly savings rate'],
    },
    ui: {
      banner_message: 'Great job! Your emergency fund is on track.',
      warning_level: 'info',
      cta_buttons: ['View Details'],
    },
  },
  g003: {
    goal: {
      goal_id: 'g003',
      goal_name: 'Travel to Japan',
      target_amount: 25_000_000,
      target_date: '2027-04-01',
      current_saved: 5_000_000,
      remaining_amount: 20_000_000,
      progress_percent: 20,
      planned_eta: '2027-04-01',
      reprojected_eta: '2027-04-01',
      status: 'on_track',
    },
    analysis: {
      gap_detected: false,
      gap_delta: 0,
      gap_reason: 'overspending',
      confidence_score: 0.78,
      strategy_selected: 'A',
      requires_manual_verification: false,
    },
    recommendations: {
      recommended_actions: ['Increase monthly saving by 500,000 VND'],
    },
    ui: {
      banner_message: "You're making steady progress toward your Japan trip!",
      warning_level: 'info',
      cta_buttons: ['Review Details'],
    },
  },
};

// ----------------------------------------------------------
// Mock: POST /api/chat/message
// ----------------------------------------------------------
export const MOCK_CHAT_REPLY: ChatMessageData = {
  session_id: 's001',
  reply: {
    message_id: 'm005',
    role: 'assistant',
    text: 'Cảnh báo: Mục tiêu Mua Laptop đang chậm tiến độ do tháng này bạn chi tiêu lố. Bạn muốn điều chỉnh lộ trình như thế nào?',
    actions: [
      {
        type: 'A',
        label: 'Plan A — Tăng 3tr/tháng',
        payload: { goal_id: 'g001', strategy: 'increase_savings', amount: 3000000 },
      },
      {
        type: 'B',
        label: 'Plan B — Dời hạn thêm 2 tháng',
        payload: { goal_id: 'g001', strategy: 'extend_deadline', months: 2 },
      }
    ],
  },
};

// ----------------------------------------------------------
// Mock: GET /api/chat/session/{session_id}
// ----------------------------------------------------------
export const MOCK_CHAT_SESSION: ChatSessionData = {
  session_id: 's001',
  messages: [
    {
      message_id: 'm001',
      role: 'user',
      text: 'Tôi muốn mua laptop giá 30 triệu.',
    },
    {
      message_id: 'm002',
      role: 'assistant',
      text: 'Tôi có thể tạo goal này cho bạn.',
      actions: [
        {
          type: 'create_goal',
          label: 'Create Goal',
          payload: {
            goal_name: 'Buy Laptop',
            goal_type: 'purchase',
            target_amount: 30_000_000,
            target_date: '2026-11-10',
          },
        },
      ],
    },
    {
      message_id: 'm003',
      role: 'user',
      text: 'Tạo đi.',
    },
    {
      message_id: 'm004',
      role: 'assistant',
      text: 'Đây là kế hoạch: Tiết kiệm 3.750.000đ/tháng trong 8 tháng. Bạn có đồng ý với lộ trình này không?',
      actions: [
        { type: 'accept', label: 'Đồng ý', payload: { action: 'confirm' } },
        { type: 'cancel', label: 'Hủy', payload: { action: 'abort' } }
      ],
    },
  ],
};

// ----------------------------------------------------------
// Mock: POST /api/goals
// ----------------------------------------------------------
export const MOCK_CREATE_GOAL: CreateGoalData = {
  goal_id: 'g004',
  goal_name: 'New Goal',
  progress_percent: 0,
  status: 'on_track',
};

// ----------------------------------------------------------
// Mock: POST /api/input-data
// ----------------------------------------------------------
export const MOCK_INPUT_DATA: InputDataData = {
  imported_count: 1,
  affected_goals: ['g001', 'g002'],
  should_refresh_dashboard: true,
};

// ----------------------------------------------------------
// Mock: GET /api/cashflow/weekly
// Dữ liệu dòng tiền 7 ngày (08/03 – 14/03/2026)
// ----------------------------------------------------------
export const MOCK_CASH_FLOW: CashFlowData = {
  period_start: '2026-03-08',
  period_end: '2026-03-14',
  points: [
    { date: '2026-03-08', income: 0, expense: 320_000, net: -320_000 },
    { date: '2026-03-09', income: 3_000_000, expense: 750_000, net: 2_250_000 },
    { date: '2026-03-10', income: 0, expense: 480_000, net: -480_000 },
    { date: '2026-03-11', income: 500_000, expense: 200_000, net: 300_000 },
    { date: '2026-03-12', income: 0, expense: 650_000, net: -650_000 },
    { date: '2026-03-13', income: 4_000_000, expense: 900_000, net: 3_100_000 },
    { date: '2026-03-14', income: 0, expense: 410_000, net: -410_000 },
  ],
};
