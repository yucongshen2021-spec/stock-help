export function formatNumber(n: number | null | undefined): string {
  if (n == null) return "--";
  if (Math.abs(n) >= 1e8) return (n / 1e8).toFixed(2) + "亿";
  if (Math.abs(n) >= 1e4) return (n / 1e4).toFixed(2) + "万";
  return n.toLocaleString("zh-CN", { maximumFractionDigits: 2 });
}

export function formatPercent(n: number | null | undefined): string {
  if (n == null) return "--";
  const sign = n >= 0 ? "+" : "";
  return `${sign}${n.toFixed(2)}%`;
}

export function formatPrice(n: number | null | undefined): string {
  if (n == null) return "--";
  return n.toFixed(2);
}
