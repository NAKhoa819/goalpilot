// ============================================================
// cashFlowCoordinator.ts
// GET /api/cashflow/weekly
// ============================================================

import type { CashFlowResponse } from './types';
import { MOCK_CASH_FLOW } from './mockData';

/**
 * Lấy dữ liệu dòng tiền 7 ngày gần nhất.
 *
 * @param goalId - (tuỳ chọn) lọc theo goal cụ thể
 *
 * TODO: swap sang fetch thật khi BE sẵn sàng:
 *   const url = '/api/cashflow/weekly' + (goalId ? `?goal_id=${goalId}` : '');
 *   const res = await fetch(url);
 *   return res.json();
 */
export async function getCashFlow(goalId?: string): Promise<CashFlowResponse> {
  await delay(350);

  // goalId nhận vào nhưng mock data hiện không phân biệt theo goal.
  // Khi swap sang BE thật, query param sẽ được truyền đúng.
  void goalId;

  return {
    success: true,
    data: MOCK_CASH_FLOW,
  };
}

// ---------------------------------------------------------------------------
function delay(ms: number) {
  return new Promise<void>((resolve) => setTimeout(resolve, ms));
}
