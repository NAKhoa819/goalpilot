// ============================================================
// index.ts — Public API của coordinator layer
//
// Cách dùng:
//   import { getDashboard, getGoalProgress, createGoal } from '@/coordinator';
//   import type { GoalCard, DashboardResponse } from '@/coordinator';
// ============================================================

// --- Functions ---
export { getDashboard } from './dashboardCoordinator';
export { getGoalProgress, createGoal } from './goalCoordinator';
export { postChatMessage, getChatSession } from './chatCoordinator';
export { postInputData } from './inputDataCoordinator';

// --- Types ---
export type {
  // Base
  ApiResponse,
  ApiErrorResponse,

  // Enums
  GoalStatus,
  WarningLevel,
  StrategySelected,
  InputSource,
  GoalType,
  ChatRole,
  ChatActionType,
  GapReason,

  // Data objects
  GoalCard,
  ChatPreview,
  ChatAction,
  ChatMessage,
  RecommendationOptions,
  DeadlineExtensionOption,
  IncomeAugmentationOption,
  ProgressGoal,
  ProgressAnalysis,
  ProgressUI,
  InputAction,

  // Request / Response types
  DashboardData,
  DashboardResponse,
  GoalProgressData,
  GoalProgressResponse,
  PostChatMessageRequest,
  ChatMessageData,
  ChatMessageResponse,
  ChatSessionData,
  ChatSessionResponse,
  CreateGoalRequest,
  CreateGoalData,
  CreateGoalResponse,
  ManualCategoryItem,
  ManualInputPayload,
  TransactionItem,
  OcrInputPayload,
  InputDataRequest,
  InputDataData,
  InputDataResponse,
} from './types';

// --- Mock data (optional, dùng cho testing / Storybook) ---
export {
  MOCK_DASHBOARD,
  MOCK_GOAL_PROGRESS,
  MOCK_GOAL_PROGRESS_MAP,
  MOCK_CHAT_REPLY,
  MOCK_CHAT_SESSION,
  MOCK_CREATE_GOAL,
  MOCK_INPUT_DATA,
} from './mockData';
