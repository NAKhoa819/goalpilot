// ============================================================
// inputDataCoordinator.ts
// POST /api/input-data
// ============================================================

import type { InputDataRequest, InputDataResponse } from './types';
import { MOCK_INPUT_DATA } from './mockData';

/**
 * Nhập dữ liệu từ dashboard (manual, OCR, SMS, file).
 *
 * TODO: swap sang fetch thật khi BE sẵn sàng:
 *   const res = await fetch('/api/input-data', {
 *     method: 'POST',
 *     headers: { 'Content-Type': 'application/json' },
 *     body: JSON.stringify(payload),
 *   });
 *   return res.json();
 */
export async function postInputData(payload: InputDataRequest): Promise<InputDataResponse> {
  await delay(500);

  // Adjust imported_count based on source for more realistic mock
  const importedCount =
    payload.source === 'ocr' || payload.source === 'sms' || payload.source === 'file'
      ? 3
      : 1;

  return {
    success: true,
    message: 'Input data processed successfully',
    data: {
      ...MOCK_INPUT_DATA,
      imported_count: importedCount,
    },
  };
}

// ---------------------------------------------------------------------------
function delay(ms: number) {
  return new Promise<void>((resolve) => setTimeout(resolve, ms));
}
