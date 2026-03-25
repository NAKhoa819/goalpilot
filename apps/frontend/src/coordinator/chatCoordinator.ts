// ============================================================
// chatCoordinator.ts
// POST /api/chat/message
// GET  /api/chat/session/{session_id}
// ============================================================

import type {
  PostChatMessageRequest,
  ChatMessageResponse,
  ChatSessionResponse,
  ChatAction,
  GoalActionRequest,
  GoalActionResponse,
  ActionSelectionResult,
} from './types';
import { fetchJson } from './apiClient';

export async function postChatMessage(
  payload: PostChatMessageRequest,
): Promise<ChatMessageResponse> {
  return fetchJson<ChatMessageResponse>('/api/chat/message', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}

/**
 * Load lịch sử chat khi user mở tab Agent.
 */
export async function getChatSession(sessionId: string): Promise<ChatSessionResponse> {
  return fetchJson<ChatSessionResponse>(`/api/chat/session/${sessionId}`);
}

// ---------------------------------------------------------------------------
export async function handleFileUpload(sourceType: 'camera' | 'gallery' | 'link'): Promise<{ success: boolean }> {
  await delay(500);
  console.log(`[chatCoordinator] handleFileUpload from: ${sourceType}`);
  return { success: true };
}

export async function handleActionSelection(
  action: ChatAction,
  sessionId: string,
): Promise<ActionSelectionResult> {
  console.log('[API BINDING] Thực thi action:', action.type, action.payload);

  if (action.type === 'create_goal') {
    const payload = action.payload as any; // Type assertion to bypass strict generic checking for MVP
    await fetchJson<{ success: boolean }>('/api/goals', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        goal_name: payload.goal_name || 'New Goal',
        goal_type: payload.goal_type || 'custom',
        target_amount: payload.target_amount || 0,
        target_date: payload.target_date || '2026-12-31',
        created_from: 'chat'
      }),
    });
    return {
      success: true,
      should_post_chat: true,
      should_refresh_dashboard: true,
    };
  }

  if (action.type === 'A' || action.type === 'B') {
    const goalId = typeof action.payload.goal_id === 'string' ? action.payload.goal_id : '';
    const response = await fetchJson<GoalActionResponse>(`/api/goals/${goalId}/actions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        action,
      } satisfies GoalActionRequest),
    });

    return {
      success: response.success,
      should_post_chat: false,
      should_refresh_dashboard: response.data.should_refresh_dashboard,
      reply: response.data.reply,
    };
  }

  return { success: true, should_post_chat: true };
}

// ---------------------------------------------------------------------------
function delay(ms: number) {
  return new Promise<void>((resolve) => setTimeout(resolve, ms));
}
