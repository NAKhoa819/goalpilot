// ============================================================
// goalCoordinator.ts
// GET /api/goals/{goal_id}/progress
// POST /api/goals
// ============================================================

import type {
  GoalProgressResponse,
  CreateGoalRequest,
  CreateGoalResponse,
} from './types';
import { MOCK_GOAL_PROGRESS_MAP, MOCK_GOAL_PROGRESS, MOCK_CREATE_GOAL } from './mockData';

/**
 * Lấy dữ liệu tiến trình chi tiết của một goal.
 *
 * TODO: swap sang fetch thật khi BE sẵn sàng:
 *   const res = await fetch(`/api/goals/${goalId}/progress`);
 *   return res.json();
 */
export async function getGoalProgress(goalId: string): Promise<GoalProgressResponse> {
  await delay(300);

  // Trả mock data theo goalId nếu có, fallback về g001
  const data = MOCK_GOAL_PROGRESS_MAP[goalId] ?? MOCK_GOAL_PROGRESS;

  return {
    success: true,
    data,
  };
}

/**
 * Tạo goal mới.
 *
 * TODO: swap sang fetch thật khi BE sẵn sàng:
 *   const res = await fetch('/api/goals', {
 *     method: 'POST',
 *     headers: { 'Content-Type': 'application/json' },
 *     body: JSON.stringify(payload),
 *   });
 *   return res.json();
 */
export async function createGoal(payload: CreateGoalRequest): Promise<CreateGoalResponse> {
  await delay(400);

  return {
    success: true,
    message: 'Goal created successfully',
    data: {
      ...MOCK_CREATE_GOAL,
      goal_name: payload.goal_name,
    },
  };
}

// ---------------------------------------------------------------------------
function delay(ms: number) {
  return new Promise<void>((resolve) => setTimeout(resolve, ms));
}
