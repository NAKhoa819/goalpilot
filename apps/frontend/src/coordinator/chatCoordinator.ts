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
import { MOCK_CHAT_REPLY, MOCK_CHAT_SESSION } from './mockData';

/**
 * Gửi tin nhắn user cho agent và nhận reply.
 *
 * TODO: swap sang fetch thật khi BE sẵn sàng:
 *   const res = await fetch('/api/chat/message', {
 *     method: 'POST',
 *     headers: { 'Content-Type': 'application/json' },
 *     body: JSON.stringify(payload),
 *   });
 *   return res.json();
 */
export async function postChatMessage(
  payload: PostChatMessageRequest,
): Promise<ChatMessageResponse> {
  // Simulate agent thinking time
  await delay(600);

  return {
    success: true,
    data: {
      session_id: payload.session_id,
      reply: {
        ...MOCK_CHAT_REPLY.reply,
        message_id: `m_${Date.now()}`, // unique mỗi lần — tránh duplicate key
        text: MOCK_CHAT_REPLY.reply.text,
      },
    },
  };
}

/**
 * Load lịch sử chat khi user mở tab Agent.
 *
 * TODO: swap sang fetch thật khi BE sẵn sàng:
 *   const res = await fetch(`/api/chat/session/${sessionId}`);
 *   return res.json();
 */
export async function getChatSession(sessionId: string): Promise<ChatSessionResponse> {
  await delay(300);

  return {
    success: true,
    data: {
      ...MOCK_CHAT_SESSION,
      session_id: sessionId,
    },
  };
}

// ---------------------------------------------------------------------------
export async function handleFileUpload(sourceType: 'camera' | 'gallery' | 'link'): Promise<{ success: boolean }> {
  await delay(500);
  console.log(`[chatCoordinator] handleFileUpload from: ${sourceType}`);
  return { success: true };
}

export async function handleActionSelection(action: ChatAction): Promise<{ success: boolean }> {
  await delay(500);
  console.log('[API BINDING] Bắn dữ liệu lên BE:', action.type, action.payload);
  return { success: true };
}

// ---------------------------------------------------------------------------
function delay(ms: number) {
  return new Promise<void>((resolve) => setTimeout(resolve, ms));
}
