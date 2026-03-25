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
  RecommendationConfirmationPayload,
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

export async function getChatSession(sessionId: string): Promise<ChatSessionResponse> {
  return fetchJson<ChatSessionResponse>(`/api/chat/session/${sessionId}`);
}

// ---------------------------------------------------------------------------
export async function handleFileUpload(
  sourceType: 'camera' | 'gallery' | 'link',
): Promise<{ success: boolean }> {
  await delay(500);
  console.log(`[chatCoordinator] handleFileUpload from: ${sourceType}`);
  return { success: true };
}

export async function handleActionSelection(
  action: ChatAction,
  sessionId: string,
): Promise<ActionSelectionResult> {
  console.log('[API BINDING] execute action:', action.type, action.payload);

  if (action.type === 'create_goal') {
    const payload = action.payload as Record<string, unknown>;
    await fetchJson<{ success: boolean }>('/api/goals', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        goal_name: payload.goal_name || 'New Goal',
        goal_type: payload.goal_type || 'custom',
        target_amount: payload.target_amount || 0,
        target_date: payload.target_date || '2026-12-31',
        created_from: 'chat',
      }),
    });
    return {
      success: true,
      should_post_chat: true,
      should_refresh_dashboard: true,
    };
  }

  const recommendedAction = unwrapConfirmedRecommendation(action);
  if (recommendedAction) {
    const goalId = typeof recommendedAction.payload.goal_id === 'string'
      ? recommendedAction.payload.goal_id
      : '';
    const response = await fetchJson<GoalActionResponse>(`/api/goals/${goalId}/actions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        action: recommendedAction,
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
function unwrapConfirmedRecommendation(action: ChatAction): ChatAction | null {
  if (action.type === 'A' || action.type === 'B') {
    return action;
  }

  if (action.type !== 'accept') {
    return null;
  }

  const payload = action.payload as RecommendationConfirmationPayload;
  if (
    payload.action !== 'confirm_recommended_plan'
    || (payload.action_type !== 'A' && payload.action_type !== 'B')
    || !payload.action_payload
  ) {
    return null;
  }

  return {
    type: payload.action_type,
    label: payload.action_label || action.label,
    payload: payload.action_payload,
  };
}

function delay(ms: number) {
  return new Promise<void>((resolve) => setTimeout(resolve, ms));
}
