// ============================================================
// Coordinator Types - FE <-> BE API Contract
// Based on: api_contract_dashboard_agent_mvp_detailed.md
// ============================================================

// ----------------------------------------------------------
// Base wrapper
// ----------------------------------------------------------
export interface ApiResponse<T> {
  success: boolean;
  message?: string;
  data: T;
}

export interface ApiErrorResponse {
  success: false;
  message: string;
  error_code: string;
}

// ----------------------------------------------------------
// Enums / Literal types
// ----------------------------------------------------------
export type GoalStatus = 'on_track' | 'at_risk' | 'completed' | 'paused';
export type WarningLevel = 'info' | 'warning' | 'critical';

/**
 * Strategy chosen by BE from the Sustainability Index:
 *   Si < 0.5      -> B (Goal Realignment)
 *   0.5 <= Si < 0.8 -> A (Cost Optimization)
 *   Si >= 0.8     -> None
 */
export type StrategySelected = 'A' | 'B' | 'None';

export interface StrategyResponse {
  strategy: StrategySelected;
  reasoning: string;
  remediation_steps: string[];
}

export type InputSource = 'manual' | 'ocr' | 'sms' | 'file';
export type GoalType = 'purchase' | 'saving' | 'emergency_fund' | 'custom';
export type ChatRole = 'user' | 'assistant';

/**
 * A/B remain internal recommendation types from BE.
 * User confirms the preselected recommendation with `accept`.
 */
export type ChatActionType =
  | 'A'
  | 'B'
  | 'create_goal'
  | 'view_goal_progress'
  | 'open_input_data'
  | 'refresh_dashboard'
  | 'accept'
  | 'cancel'
  | (string & {});

export type GapReason =
  | 'market_price_increase'
  | 'overspending'
  | 'income_drop'
  | 'mixed';

// ----------------------------------------------------------
// Goal card for slider
// ----------------------------------------------------------
export interface GoalCard {
  goal_id: string;
  goal_name: string;
  target_amount: number;
  target_date: string;
  current_saved: number;
  progress_percent: number;
  status: GoalStatus;
}

// ----------------------------------------------------------
// Chat preview
// ----------------------------------------------------------
export interface ChatPreview {
  session_id: string;
  last_message: string;
  unread_count: number;
}

// ----------------------------------------------------------
// Chat actions
// ----------------------------------------------------------
export interface PlanAPayload {
  goal_id: string;
  strategy: 'increase_savings';
  amount: number;
  duration_months?: number;
}

export interface PlanBPayload {
  goal_id: string;
  strategy: 'extend_deadline';
  months: number;
  new_target_date?: string;
}

export interface RecommendationConfirmationPayload {
  goal_id: string;
  action: 'confirm_recommended_plan';
  action_type: 'A' | 'B';
  action_label?: string;
  action_payload: PlanAPayload | PlanBPayload;
}

export interface RecommendationDismissPayload {
  goal_id: string;
  action: 'keep_current_plan';
  action_type: 'A' | 'B';
}

export interface ChatAction {
  type: ChatActionType;
  label: string;
  payload:
    | PlanAPayload
    | PlanBPayload
    | RecommendationConfirmationPayload
    | RecommendationDismissPayload
    | Record<string, unknown>;
}

// ----------------------------------------------------------
// Chat message
// ----------------------------------------------------------
export interface ChatMessage {
  message_id: string;
  role: ChatRole;
  text: string;
  actions?: ChatAction[];
}

// ----------------------------------------------------------
// Recommendation options
// ----------------------------------------------------------
export interface DeadlineExtensionOption {
  new_target_date: string;
  delay_days: number;
}

export interface IncomeAugmentationOption {
  required_extra_income_per_month: number;
}

export interface RecommendationOptions {
  recommended_actions: string[];
  deadline_extension_option?: DeadlineExtensionOption;
  income_augmentation_option?: IncomeAugmentationOption;
  plan_a_option?: PlanAPayload;
  plan_b_option?: PlanBPayload;
}

// ----------------------------------------------------------
// Progress goal
// ----------------------------------------------------------
export interface ProgressGoal {
  goal_id: string;
  goal_name: string;
  target_amount: number;
  target_date: string;
  current_saved: number;
  remaining_amount: number;
  progress_percent: number;
  planned_eta: string;
  reprojected_eta: string;
  status: GoalStatus;
}

// ----------------------------------------------------------
// Progress analysis
// ----------------------------------------------------------
export interface ProgressAnalysis {
  gap_detected: boolean;
  gap_delta: number;
  gap_reason: GapReason;
  confidence_score: number;
  strategy_selected: StrategySelected;
  accepted_action_type?: 'A' | 'B' | null;
  accepted_action_payload?: PlanAPayload | PlanBPayload | null;
  requires_manual_verification: boolean;
}

// ----------------------------------------------------------
// Progress UI
// ----------------------------------------------------------
export interface ProgressUI {
  banner_message: string;
  warning_level: WarningLevel;
  cta_buttons: string[];
}

// ----------------------------------------------------------
// Dashboard input actions
// ----------------------------------------------------------
export interface InputAction {
  type: string;
  label: string;
}

// ----------------------------------------------------------
// GET /api/dashboard
// ----------------------------------------------------------
export interface DashboardData {
  goals: GoalCard[];
  active_goal_id: string | null;
  chat_preview: ChatPreview;
  input_actions: InputAction[];
}

export type DashboardResponse = ApiResponse<DashboardData>;

// ----------------------------------------------------------
// GET /api/goals/{goal_id}/progress
// ----------------------------------------------------------
export interface GoalProgressData {
  goal: ProgressGoal;
  analysis: ProgressAnalysis;
  recommendations: RecommendationOptions;
  ui: ProgressUI;
}

export type GoalProgressResponse = ApiResponse<GoalProgressData>;

// ----------------------------------------------------------
// POST /api/chat/message
// ----------------------------------------------------------
export interface PostChatMessageRequest {
  session_id: string;
  message: string;
  context?: {
    active_goal_id?: string | null;
    source_screen?: string;
  };
}

export interface ChatMessageData {
  session_id: string;
  reply: ChatMessage;
}

export type ChatMessageResponse = ApiResponse<ChatMessageData>;

// ----------------------------------------------------------
// GET /api/chat/session/{session_id}
// ----------------------------------------------------------
export interface ChatSessionData {
  session_id: string;
  messages: ChatMessage[];
}

export type ChatSessionResponse = ApiResponse<ChatSessionData>;

// ----------------------------------------------------------
// POST /api/goals/{goal_id}/actions
// ----------------------------------------------------------
export interface GoalActionRequest {
  session_id: string;
  action: ChatAction;
}

export interface GoalActionData {
  goal_id: string;
  applied_action_type: 'A' | 'B';
  should_refresh_dashboard: boolean;
  reply: ChatMessage;
}

export type GoalActionResponse = ApiResponse<GoalActionData>;

// ----------------------------------------------------------
// POST /api/goals
// ----------------------------------------------------------
export interface CreateGoalRequest {
  goal_name: string;
  goal_type: GoalType;
  target_amount: number;
  target_date: string;
  currency: string;
  created_from?: string;
}

export interface CreateGoalData {
  goal_id: string;
  goal_name: string;
  progress_percent: number;
  status: GoalStatus;
}

export type CreateGoalResponse = ApiResponse<CreateGoalData>;

export interface ActionSelectionResult {
  success: boolean;
  should_post_chat: boolean;
  should_refresh_dashboard?: boolean;
  reply?: ChatMessage;
}

// ----------------------------------------------------------
// POST /api/input-data
// ----------------------------------------------------------
export interface ManualCategoryItem {
  name: string;
  current_month_spend: number;
  is_essential: boolean;
}

export interface ManualInputPayload {
  monthly_income?: number;
  current_balance?: number;
  projected_savings?: number;
  categories?: ManualCategoryItem[];
}

export interface TransactionItem {
  date: string;
  amount: number;
  description?: string;
  category?: string;
}

export interface OcrInputPayload {
  transactions: TransactionItem[];
}

export interface InputDataRequest {
  source: InputSource;
  payload: ManualInputPayload | OcrInputPayload | Record<string, unknown>;
}

export interface InputDataData {
  imported_count: number;
  affected_goals: string[];
  should_refresh_dashboard: boolean;
}

export type InputDataResponse = ApiResponse<InputDataData>;

// ----------------------------------------------------------
// Cash flow
// ----------------------------------------------------------
export interface CashFlowPoint {
  date: string;
  income: number;
  expense: number;
  net: number;
}

// ----------------------------------------------------------
// GET /api/cashflow/weekly
// ----------------------------------------------------------
export interface CashFlowData {
  period_start: string;
  period_end: string;
  points: CashFlowPoint[];
}

export type CashFlowResponse = ApiResponse<CashFlowData>;
