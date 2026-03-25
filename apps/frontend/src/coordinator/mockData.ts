// ============================================================
// Mock Data for coordinator layer
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
    last_message: 'Your laptop goal is currently at risk.',
    unread_count: 1,
  },
  input_actions: [
    { type: 'manual_input', label: 'Enter Data' },
    { type: 'ocr_upload', label: 'Scan Receipt' },
  ],
};

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
    reprojected_eta: '2027-03-01',
    status: 'at_risk',
  },
  analysis: {
    gap_detected: true,
    gap_delta: 1_500_000,
    gap_reason: 'market_price_increase',
    confidence_score: 0.86,
    strategy_selected: 'B',
    accepted_action_type: null,
    accepted_action_payload: null,
    requires_manual_verification: false,
  },
  recommendations: {
    recommended_actions: ['GoalPilot recommends extending the deadline by 3 months.'],
    deadline_extension_option: {
      new_target_date: '2027-03-01',
      delay_days: 90,
    },
    plan_b_option: {
      goal_id: 'g001',
      strategy: 'extend_deadline',
      months: 3,
      new_target_date: '2027-03-01',
    },
  },
  ui: {
    banner_message: 'Your goal is currently at risk. GoalPilot recommends Plan B.',
    warning_level: 'warning',
    cta_buttons: ['Review Recommended Plan', 'Review Details'],
  },
};

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
      reprojected_eta: '2026-09-01',
      status: 'on_track',
    },
    analysis: {
      gap_detected: false,
      gap_delta: 0,
      gap_reason: 'overspending',
      confidence_score: 0.92,
      strategy_selected: 'None',
      accepted_action_type: null,
      accepted_action_payload: null,
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
      strategy_selected: 'None',
      accepted_action_type: null,
      accepted_action_payload: null,
      requires_manual_verification: false,
    },
    recommendations: {
      recommended_actions: ['You are making steady progress.'],
    },
    ui: {
      banner_message: "You're making steady progress toward your Japan trip!",
      warning_level: 'info',
      cta_buttons: ['Review Details'],
    },
  },
};

export const MOCK_CHAT_REPLY: ChatMessageData = {
  session_id: 's001',
  reply: {
    message_id: 'm005',
    role: 'assistant',
    text: 'Your laptop goal is currently at risk. GoalPilot selected Plan B. Confirm this plan if you want me to apply it.',
    actions: [
      {
        type: 'accept',
        label: 'Apply Recommended Plan',
        payload: {
          goal_id: 'g001',
          action: 'confirm_recommended_plan',
          action_type: 'B',
          action_label: 'Plan B - Extend deadline by 3 months',
          action_payload: {
            goal_id: 'g001',
            strategy: 'extend_deadline',
            months: 3,
            new_target_date: '2027-03-01',
          },
        },
      },
      {
        type: 'cancel',
        label: 'Keep Current Goal',
        payload: {
          goal_id: 'g001',
          action: 'keep_current_plan',
          action_type: 'B',
        },
      },
    ],
  },
};

export const MOCK_CHAT_SESSION: ChatSessionData = {
  session_id: 's001',
  messages: [
    {
      message_id: 'm001',
      role: 'user',
      text: 'I want to buy a laptop worth 30 million.',
    },
    {
      message_id: 'm002',
      role: 'assistant',
      text: 'I can create that goal for you.',
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
      text: 'Create it.',
    },
    {
      message_id: 'm004',
      role: 'assistant',
      text: 'Your laptop goal is currently at risk. GoalPilot selected Plan A. Confirm this plan if you want me to apply it.',
      actions: [
        {
          type: 'accept',
          label: 'Apply Recommended Plan',
          payload: {
            goal_id: 'g001',
            action: 'confirm_recommended_plan',
            action_type: 'A',
            action_label: 'Plan A - Save an extra 2,000,000 VND/month',
            action_payload: {
              goal_id: 'g001',
              strategy: 'increase_savings',
              amount: 2_000_000,
              duration_months: 6,
            },
          },
        },
        {
          type: 'cancel',
          label: 'Keep Current Goal',
          payload: {
            goal_id: 'g001',
            action: 'keep_current_plan',
            action_type: 'A',
          },
        },
      ],
    },
  ],
};

export const MOCK_CREATE_GOAL: CreateGoalData = {
  goal_id: 'g004',
  goal_name: 'New Goal',
  progress_percent: 0,
  status: 'on_track',
};

export const MOCK_INPUT_DATA: InputDataData = {
  imported_count: 1,
  affected_goals: ['g001', 'g002'],
  should_refresh_dashboard: true,
};

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
