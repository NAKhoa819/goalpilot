// ============================================================
// Coordinator Types — FE ↔ BE API Contract
// Dựa theo: api_contract_dashboard_agent_mvp_detailed.md
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
 * Strategy BE chọn sau khi phân tích:
 *   A = Cost optimization / cắt chi tiêu
 *   B = Goal adjustment / gia hạn deadline hoặc tăng thu nhập
 * Lưu ý: FE luôn hiện CẢ 2 nút plan_a + plan_b khi gap_detected = true.
 * strategy_selected chỉ dùng để highlight nút BE recommend.
 */
export type StrategySelected = 'A' | 'B';
export type InputSource = 'manual' | 'ocr' | 'sms' | 'file';
export type GoalType = 'purchase' | 'saving' | 'emergency_fund' | 'custom';
export type ChatRole = 'user' | 'assistant';

/**
 * Action type trong chat. plan_a + plan_b luôn xuất hiện cùng nhau
 * trong 1 reply khi agent phát hiện gap (gap_detected = true).
 */
export type ChatActionType =
  | 'plan_a'             // Tăng tiết kiệm hàng tháng
  | 'plan_b'             // Gia hạn deadline
  | 'create_goal'        // Tạo goal mới
  | 'view_goal_progress' // Mở chi tiết tiến trình goal
  | 'open_input_data'    // Mở form nhập liệu
  | 'refresh_dashboard'  // Refresh dashboard
  | 'accept'             // Đồng ý lộ trình
  | 'cancel'             // Huỷ
  | (string & {});       // Fallback — không mất type-narrowing
export type GapReason =
  | 'market_price_increase'
  | 'overspending'
  | 'income_drop'
  | 'mixed';

// ----------------------------------------------------------
// 3.1 GoalCard — dùng cho goal slider
// ----------------------------------------------------------
export interface GoalCard {
  goal_id: string;
  goal_name: string;
  target_amount: number;
  target_date: string; // YYYY-MM-DD
  current_saved: number;
  progress_percent: number;
  status: GoalStatus;
}

// ----------------------------------------------------------
// 3.2 ChatPreview — ô chat preview trên dashboard
// ----------------------------------------------------------
export interface ChatPreview {
  session_id: string;
  last_message: string;
  unread_count: number;
}

// ----------------------------------------------------------
// 3.3 ChatAction — action button trong chat
// ----------------------------------------------------------

/** Payload Plan A: tăng tiết kiệm hàng tháng */
export interface PlanAPayload {
  strategy: 'increase_savings';
  amount: number;           // VND tăng thêm mỗi tháng
  duration_months?: number;
}

/** Payload Plan B: gia hạn deadline */
export interface PlanBPayload {
  strategy: 'extend_deadline';
  months: number;           // Số tháng gia hạn
  new_target_date?: string; // YYYY-MM-DD (optional, tính sẵn)
}

export interface ChatAction {
  type: ChatActionType;
  label: string;
  /** plan_a → PlanAPayload | plan_b → PlanBPayload | khác → Record */
  payload: PlanAPayload | PlanBPayload | Record<string, unknown>;
}

// ----------------------------------------------------------
// 3.4 ChatMessage — tin nhắn trong tab Agent
// ----------------------------------------------------------
export interface ChatMessage {
  message_id: string;
  role: ChatRole;
  text: string;
  actions?: ChatAction[];
}

// ----------------------------------------------------------
// 3.5 RecommendationOptions
// ----------------------------------------------------------
export interface DeadlineExtensionOption {
  new_target_date: string; // YYYY-MM-DD
  delay_days: number;
}

export interface IncomeAugmentationOption {
  required_extra_income_per_month: number;
}

export interface RecommendationOptions {
  recommended_actions: string[];
  deadline_extension_option?: DeadlineExtensionOption;
  income_augmentation_option?: IncomeAugmentationOption;
  /**
   * Khi gap_detected = true, BE điền đủ cả 2 field để FE render
   * 2 nút Plan A + Plan B trong cùng 1 chat reply.
   */
  plan_a_option?: PlanAPayload; // data cho nút Plan A
  plan_b_option?: PlanBPayload; // data cho nút Plan B
}

// ----------------------------------------------------------
// 3.6 ProgressGoal
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
// 3.7 ProgressAnalysis
// ----------------------------------------------------------
export interface ProgressAnalysis {
  gap_detected: boolean;
  gap_delta: number;
  gap_reason: GapReason;
  confidence_score: number;
  strategy_selected: StrategySelected;
  requires_manual_verification: boolean;
}

// ----------------------------------------------------------
// 3.8 ProgressUI
// ----------------------------------------------------------
export interface ProgressUI {
  banner_message: string;
  warning_level: WarningLevel;
  cta_buttons: string[];
}

// ----------------------------------------------------------
// Input action item (dashboard nút nhập dữ liệu)
// ----------------------------------------------------------
export interface InputAction {
  type: string;
  label: string;
}

// ----------------------------------------------------------
// 4.1 GET /api/dashboard
// ----------------------------------------------------------
export interface DashboardData {
  goals: GoalCard[];
  active_goal_id: string;
  chat_preview: ChatPreview;
  input_actions: InputAction[];
}
export type DashboardResponse = ApiResponse<DashboardData>;

// ----------------------------------------------------------
// 4.2 GET /api/goals/{goal_id}/progress
// ----------------------------------------------------------
export interface GoalProgressData {
  goal: ProgressGoal;
  analysis: ProgressAnalysis;
  recommendations: RecommendationOptions;
  ui: ProgressUI;
}
export type GoalProgressResponse = ApiResponse<GoalProgressData>;

// ----------------------------------------------------------
// 4.3 POST /api/chat/message
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
// 4.4 GET /api/chat/session/{session_id}
// ----------------------------------------------------------
export interface ChatSessionData {
  session_id: string;
  messages: ChatMessage[];
}
export type ChatSessionResponse = ApiResponse<ChatSessionData>;

// ----------------------------------------------------------
// 4.5 POST /api/goals
// ----------------------------------------------------------
export interface CreateGoalRequest {
  goal_name: string;
  goal_type: GoalType;
  target_amount: number;
  target_date: string; // YYYY-MM-DD
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

// ----------------------------------------------------------
// 4.6 POST /api/input-data
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
// 3.9 CashFlowPoint — điểm dữ liệu dòng tiền mỗi ngày
// ----------------------------------------------------------
export interface CashFlowPoint {
  date: string;    // YYYY-MM-DD
  income: number;  // Tổng thu trong ngày
  expense: number; // Tổng chi trong ngày
  net: number;     // income - expense (tính sẵn)
}

// ----------------------------------------------------------
// 4.7 GET /api/cashflow/weekly
// ----------------------------------------------------------
export interface CashFlowData {
  period_start: string; // YYYY-MM-DD — ngày đầu tuần
  period_end: string;   // YYYY-MM-DD — ngày cuối tuần
  points: CashFlowPoint[];
}
export type CashFlowResponse = ApiResponse<CashFlowData>;
