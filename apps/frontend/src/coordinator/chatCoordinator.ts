// ============================================================
// chatCoordinator.ts
// POST /api/chat/message
// GET  /api/chat/session/{session_id}
// ============================================================

import type {
  PostChatMessageRequest,
  ChatMessageResponse,
  ChatSessionResponse,
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
        // Echo user message context vào reply text để dễ debug
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
function delay(ms: number) {
  return new Promise<void>((resolve) => setTimeout(resolve, ms));
}
