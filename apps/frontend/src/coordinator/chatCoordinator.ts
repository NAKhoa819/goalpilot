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
  StrategyResponse,
} from './types';
import { MOCK_STRATEGY_RESPONSE, MOCK_CHAT_SESSION } from './mockData';

// ---------------------------------------------------------------------------
// Transform StrategyResponse → ChatMessage text + actions array
// ---------------------------------------------------------------------------
function buildChatReplyFromStrategy(sr: StrategyResponse): {
  text: string;
  actions: ChatAction[];
} {
  // Nối reasoning + bullet points từ remediation_steps
  const bulletList = sr.remediation_steps.map((s) => `• ${s}`).join('\n');
  const text = `${sr.reasoning}\n\n${bulletList}`;

  // Map strategy → action button(s)
  let actions: ChatAction[] = [];
  if (sr.strategy === 'A') {
    actions = [{ type: 'A', label: 'Cost Optimization', payload: {} }];
  } else if (sr.strategy === 'B') {
    actions = [{ type: 'B', label: 'Goal Re-alignment', payload: {} }];
  }
  // strategy === 'None' → actions = [] (không hiện nút)

  return { text, actions };
}

/**
 * Gửi tin nhắn user cho agent và nhận reply.
 *
 * TODO: swap sang fetch thật khi BE sẵn sàng:
 *   const res = await fetch('/api/chat/message', {
 *     method: 'POST',
 *     headers: { 'Content-Type': 'application/json' },
 *     body: JSON.stringify(payload),
 *   });
 *   const json = await res.json();
 *   // json.data.strategy_response là StrategyResponse
 *   const { text, actions } = buildChatReplyFromStrategy(json.data.strategy_response);
 */
export async function postChatMessage(
  payload: PostChatMessageRequest,
): Promise<ChatMessageResponse> {
  // Simulate agent thinking time
  await delay(600);

  const { text, actions } = buildChatReplyFromStrategy(MOCK_STRATEGY_RESPONSE);

  return {
    success: true,
    data: {
      session_id: payload.session_id,
      reply: {
        message_id: `m_${Date.now()}`, // unique mỗi lần — tránh duplicate key
        role: 'assistant',
        text,
        actions,
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
