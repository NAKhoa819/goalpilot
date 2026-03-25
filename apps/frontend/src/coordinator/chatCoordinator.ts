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

export async function handleActionSelection(action: ChatAction): Promise<{ success: boolean }> {
  console.log('[API BINDING] Thực thi action:', action.type, action.payload);

  if (action.type === 'create_goal') {
    const payload = action.payload as any; // Type assertion to bypass strict generic checking for MVP
    return fetchJson<{ success: boolean }>('/api/goals', {
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
  }

  // Phase 1: Các hành động khác (A, B) chưa có endpoint thật
  return { success: true };
}

// ---------------------------------------------------------------------------
function delay(ms: number) {
  return new Promise<void>((resolve) => setTimeout(resolve, ms));
}
