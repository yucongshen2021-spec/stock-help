import { useState, useCallback, useRef, useEffect } from "react";
import Sidebar from "./Sidebar";
import { useStockStore } from "../../stores/stockStore";

const PANEL_MIN = 280;
const PANEL_MAX = 600;

export default function AppLayout({ children, rightPanel }: { children: React.ReactNode; rightPanel?: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [panelWidth, setPanelWidth] = useState(320);
  const insightOpen = useStockStore((s) => s.stockPanelOpen);
  const setInsightOpen = useStockStore((s) => s.setStockPanelOpen);
  const dragging = useRef(false);
  const dragStartX = useRef(0);
  const dragStartW = useRef(0);

  const onMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    dragging.current = true;
    dragStartX.current = e.clientX;
    dragStartW.current = panelWidth;
    document.body.style.cursor = "col-resize";
    document.body.style.userSelect = "none";
  }, [panelWidth]);

  useEffect(() => {
    const onMouseMove = (e: MouseEvent) => {
      if (!dragging.current) return;
      const delta = dragStartX.current - e.clientX;
      const next = Math.min(PANEL_MAX, Math.max(PANEL_MIN, dragStartW.current + delta));
      setPanelWidth(next);
    };
    const onMouseUp = () => {
      dragging.current = false;
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };
    document.addEventListener("mousemove", onMouseMove);
    document.addEventListener("mouseup", onMouseUp);
    return () => {
      document.removeEventListener("mousemove", onMouseMove);
      document.removeEventListener("mouseup", onMouseUp);
    };
  }, []);

  return (
    <div className="h-full flex">
      {/* Left Sidebar — 240px fixed */}
      <div
        className="shrink-0 h-full transition-[width] duration-150 ease-out overflow-hidden"
        style={{ width: sidebarOpen ? 240 : 0 }}
      >
        <Sidebar
          onToggle={() => setSidebarOpen((prev) => !prev)}
          onInsightToggle={() => setInsightOpen(!insightOpen)}
          insightOpen={insightOpen}
        />
      </div>

      {/* Center — flex-grow, primary focus */}
      <main className="flex-1 flex flex-col min-w-0 relative">
        {children}
      </main>

      {/* Right Panel — resizable */}
      {rightPanel && insightOpen && (
        <div className="flex shrink-0 h-full">
          {/* Drag handle */}
          <div
            onMouseDown={onMouseDown}
            className="w-[4px] h-full shrink-0 transition-colors duration-150"
            style={{
              cursor: "col-resize",
              background: "transparent",
            }}
            onMouseEnter={(e) => {
              (e.currentTarget as HTMLElement).style.background = "var(--color-link)";
            }}
            onMouseLeave={(e) => {
              (e.currentTarget as HTMLElement).style.background = "transparent";
            }}
          />
          <div style={{ width: panelWidth, minWidth: 0 }} className="h-full">
            {rightPanel}
          </div>
        </div>
      )}
    </div>
  );
}
