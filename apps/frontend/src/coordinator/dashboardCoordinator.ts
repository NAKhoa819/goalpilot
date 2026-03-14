// ============================================================
// dashboardCoordinator.ts
// GET /api/dashboard
// ============================================================

import type { DashboardResponse } from './types';
import { MOCK_DASHBOARD } from './mockData';

/**
 * Lấy toàn bộ dữ liệu cần để render dashboard lần đầu.
 *
 * TODO: swap sang fetch thật khi BE sẵn sàng:
 *   const res = await fetch('/api/dashboard');
 *   return res.json();
 */
export async function getDashboard(): Promise<DashboardResponse> {
  // Simulate network latency
  await delay(300);

  return {
    success: true,
    data: MOCK_DASHBOARD,
  };
}

// ---------------------------------------------------------------------------
function delay(ms: number) {
  return new Promise<void>((resolve) => setTimeout(resolve, ms));
}
