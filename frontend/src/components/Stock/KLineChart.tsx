import { useEffect, useState, useMemo, useCallback } from "react";
import ReactECharts from "echarts-for-react";
import { fetchKLine, fetchIndicators } from "../../utils/api";
import type { KLineItem } from "../../stores/stockStore";
import { useThemeStore } from "../../stores/themeStore";
import { IoExpand, IoContract } from "react-icons/io5";

type Period = "daily" | "weekly" | "monthly";
const LABELS: Record<Period, string> = { daily: "日K", weekly: "周K", monthly: "月K" };

function getChartColors(theme: "dark" | "light") {
  const isDark = theme === "dark";
  return {
    axisLine: isDark ? "rgba(255,255,255,0.05)" : "rgba(0,0,0,0.06)",
    splitLine: isDark ? "rgba(255,255,255,0.03)" : "rgba(0,0,0,0.04)",
    label: isDark ? "#6e6e6e" : "#8e8e8e",
    tooltipBg: isDark ? "#252525" : "#ffffff",
    tooltipBorder: isDark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.10)",
    tooltipText: isDark ? "#ececec" : "#1d1d1f",
    segmentBg: isDark ? "rgba(255,255,255,0.03)" : "rgba(0,0,0,0.04)",
    activeBg: isDark ? "rgba(255,255,255,0.10)" : "rgba(0,0,0,0.08)",
    activeText: isDark ? "#ffffff" : "#1d1d1f",
    inactiveText: isDark ? "rgba(255,255,255,0.30)" : "rgba(0,0,0,0.35)",
    hoverText: isDark ? "rgba(255,255,255,0.65)" : "rgba(0,0,0,0.55)",
  };
}

export default function KLineChart({ code, name }: { code: string; name: string }) {
  const [period, setPeriod] = useState<Period>("daily");
  const [data, setData] = useState<KLineItem[]>([]);
  const [ind, setInd] = useState<{
    ma5: (number | null)[];
    ma10: (number | null)[];
    ma20: (number | null)[];
    ma60: (number | null)[];
    macd: { dif: number[]; dea: number[]; bar: number[] };
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [fullscreen, setFullscreen] = useState(false);
  const theme = useThemeStore((s) => s.theme);

  const exitFullscreen = useCallback(() => setFullscreen(false), []);

  useEffect(() => {
    if (!fullscreen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setFullscreen(false);
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [fullscreen]);

  useEffect(() => {
    let c = false;
    setLoading(true);
    Promise.all([fetchKLine(code, period, 120), fetchIndicators(code, 120)])
      .then(([k, i]) => {
        if (!c) {
          setData(k);
          setInd(i);
        }
      })
      .catch(() => {})
      .finally(() => {
        if (!c) setLoading(false);
      });
    return () => {
      c = true;
    };
  }, [code, period]);

  const dates = data.map((d) => d.date);
  const ohlc = data.map((d) => [d.open, d.close, d.low, d.high]);
  const vols = data.map((d) => d.volume);

  const option = useMemo(() => {
    const c = getChartColors(theme);
    return {
      backgroundColor: "transparent",
      animation: false,
      tooltip: {
        trigger: "axis",
        axisPointer: { type: "cross" },
        backgroundColor: c.tooltipBg,
        borderColor: c.tooltipBorder,
        textStyle: { color: c.tooltipText, fontSize: 11 },
      },
      grid: [
        { left: 44, right: 8, top: 12, height: "44%" },
        { left: 44, right: 8, top: "55%", height: "12%" },
        { left: 44, right: 8, top: "72%", height: "17%" },
      ],
      xAxis: [
        {
          type: "category",
          data: dates,
          gridIndex: 0,
          axisLine: { lineStyle: { color: c.axisLine } },
          axisLabel: { show: false },
          axisTick: { show: false },
        },
        {
          type: "category",
          data: dates,
          gridIndex: 1,
          axisLine: { lineStyle: { color: c.axisLine } },
          axisLabel: { show: false },
          axisTick: { show: false },
        },
        {
          type: "category",
          data: ind?.macd?.dif
            ? dates.slice(dates.length - ind.macd.dif.length)
            : dates,
          gridIndex: 2,
          axisLine: { lineStyle: { color: c.axisLine } },
          axisLabel: {
            color: c.label,
            fontSize: 9,
            formatter: (v: string) => v.slice(5),
          },
          axisTick: { show: false },
        },
      ],
      yAxis: [
        {
          scale: true,
          gridIndex: 0,
          splitLine: { lineStyle: { color: c.splitLine } },
          axisLine: { show: false },
          axisLabel: { color: c.label, fontSize: 9 },
        },
        {
          scale: true,
          gridIndex: 1,
          splitLine: { show: false },
          axisLine: { show: false },
          axisLabel: { show: false },
        },
        {
          scale: true,
          gridIndex: 2,
          splitLine: { lineStyle: { color: c.splitLine } },
          axisLine: { show: false },
          axisLabel: { color: c.label, fontSize: 9 },
        },
      ],
      dataZoom: [
        { type: "inside", xAxisIndex: [0, 1, 2], start: 55, end: 100 },
      ],
      series: [
        {
          name: "K",
          type: "candlestick",
          data: ohlc,
          xAxisIndex: 0,
          yAxisIndex: 0,
          itemStyle: {
            color: "#ef5350",
            color0: "#26a69a",
            borderColor: "#ef5350",
            borderColor0: "#26a69a",
          },
        },
        ...(ind
          ? [
              {
                name: "MA5",
                type: "line",
                data: ind.ma5,
                xAxisIndex: 0,
                yAxisIndex: 0,
                smooth: true,
                symbol: "none",
                lineStyle: { width: 1, color: "#ffb74d" },
              },
              {
                name: "MA10",
                type: "line",
                data: ind.ma10,
                xAxisIndex: 0,
                yAxisIndex: 0,
                smooth: true,
                symbol: "none",
                lineStyle: { width: 1, color: "#4fc3f7" },
              },
              {
                name: "MA20",
                type: "line",
                data: ind.ma20,
                xAxisIndex: 0,
                yAxisIndex: 0,
                smooth: true,
                symbol: "none",
                lineStyle: { width: 1, color: "#ce93d8" },
              },
              {
                name: "MA60",
                type: "line",
                data: ind.ma60,
                xAxisIndex: 0,
                yAxisIndex: 0,
                smooth: true,
                symbol: "none",
                lineStyle: { width: 1, color: "#a5d6a7" },
              },
            ]
          : []),
        {
          name: "VOL",
          type: "bar",
          data: vols.map((v, i) => ({
            value: v,
            itemStyle: {
              color:
                ohlc[i] && ohlc[i][1] >= ohlc[i][0]
                  ? "rgba(239,83,80,0.2)"
                  : "rgba(38,166,154,0.2)",
            },
          })),
          xAxisIndex: 1,
          yAxisIndex: 1,
        },
        ...(ind?.macd
          ? [
              {
                name: "MACD",
                type: "bar",
                data: ind.macd.bar.map((v) => ({
                  value: v,
                  itemStyle: {
                    color:
                      v >= 0
                        ? "rgba(239,83,80,0.35)"
                        : "rgba(38,166,154,0.35)",
                  },
                })),
                xAxisIndex: 2,
                yAxisIndex: 2,
              },
              {
                name: "DIF",
                type: "line",
                data: ind.macd.dif,
                xAxisIndex: 2,
                yAxisIndex: 2,
                symbol: "none",
                lineStyle: { width: 1, color: "#ffb74d" },
              },
              {
                name: "DEA",
                type: "line",
                data: ind.macd.dea,
                xAxisIndex: 2,
                yAxisIndex: 2,
                symbol: "none",
                lineStyle: { width: 1, color: "#4fc3f7" },
              },
            ]
          : []),
      ],
    };
  }, [dates, ohlc, vols, ind, theme]);

  const chartHeight = fullscreen ? "calc(100vh - 80px)" : 320;

  const controls = (
    <div className="flex items-center justify-between mb-3">
      <h3 className="text-sm font-medium" style={{ color: "var(--text-secondary)" }}>{name}</h3>
      <div className="flex items-center gap-2">
        <div
          className="flex gap-0.5 rounded-lg p-0.5"
          style={{ background: "var(--bg-surface-hover)" }}
        >
          {(Object.keys(LABELS) as Period[]).map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className="px-2.5 py-1 rounded-md text-xs font-medium transition-colors duration-150"
              style={{
                color: period === p ? "var(--text-primary)" : "var(--text-muted)",
                background: period === p ? "var(--bg-surface-active)" : "transparent",
              }}
            >
              {LABELS[p]}
            </button>
          ))}
        </div>
        <button
          onClick={() => setFullscreen((v) => !v)}
          className="p-1.5 rounded-md transition-colors duration-150"
          style={{ color: "var(--text-tertiary)" }}
          onMouseEnter={(e) => {
            const t = e.currentTarget as HTMLElement;
            t.style.background = "var(--bg-surface-hover)";
            t.style.color = "var(--text-secondary)";
          }}
          onMouseLeave={(e) => {
            const t = e.currentTarget as HTMLElement;
            t.style.background = "transparent";
            t.style.color = "var(--text-tertiary)";
          }}
          title={fullscreen ? "退出全屏" : "全屏"}
        >
          {fullscreen ? <IoContract size={14} /> : <IoExpand size={14} />}
        </button>
      </div>
    </div>
  );

  const chartBody = loading ? (
    <div className="flex items-center justify-center text-sm" style={{ height: "100%", color: "var(--text-muted)" }}>
      加载中...
    </div>
  ) : (
    <ReactECharts
      option={option}
      style={{ height: "100%", width: "100%" }}
      opts={{ renderer: "canvas" }}
    />
  );

  if (fullscreen) {
    return (
      <>
        {/* Inline placeholder to keep layout */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium" style={{ color: "var(--text-secondary)" }}>{name}</h3>
            <button
              onClick={exitFullscreen}
              className="p-1.5 rounded-md transition-colors duration-150"
              style={{ color: "var(--text-tertiary)" }}
              title="退出全屏"
            >
              <IoContract size={14} />
            </button>
          </div>
          <div style={{ height: 320, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <span className="text-sm" style={{ color: "var(--text-muted)" }}>全屏显示中...</span>
          </div>
        </div>

        {/* Fullscreen overlay */}
        <div style={{ position: "fixed", inset: 0, zIndex: 100, background: "var(--bg-main)" }}>
          <div style={{ padding: "20px 24px", height: "100%", display: "flex", flexDirection: "column" }}>
            {controls}
            <div style={{ flex: 1, minHeight: 0 }}>
              {chartBody}
            </div>
          </div>
        </div>
      </>
    );
  }

  return (
    <div>
      {controls}
      <div style={{ height: chartHeight }}>
        {chartBody}
      </div>
    </div>
  );
}
