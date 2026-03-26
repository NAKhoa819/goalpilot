export const USD_MULTIPLIER = 1.065;

export function toUsdDisplay(value: number): number {
  return value * USD_MULTIPLIER;
}

export function formatCompactUsd(value: number): string {
  const usd = toUsdDisplay(value);
  const abs = Math.abs(usd);
  const sign = usd < 0 ? '-' : '';

  if (abs >= 1_000_000) {
    return `${sign}$${(abs / 1_000_000).toFixed(1)}M`;
  }

  if (abs >= 1_000) {
    return `${sign}$${(abs / 1_000).toFixed(0)}K`;
  }

  return `${sign}$${abs.toFixed(0)}`;
}
