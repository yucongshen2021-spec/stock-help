import { IoAdd, IoTrashOutline, IoBarChartOutline, IoSunnyOutline, IoMoonOutline } from "react-icons/io5";
import { useChatStore } from "../../stores/chatStore";
import { useThemeStore } from "../../stores/themeStore";
import WatchList from "../Stock/WatchList";

export default function Sidebar({ onToggle, onInsightToggle, insightOpen }: {
  onToggle: () => void; onInsightToggle: () => void; insightOpen: boolean;
}) {
  const conversations = useChatStore((s) => s.conversations);
  const activeId = useChatStore((s) => s.activeConversationId);
  const createConversation = useChatStore((s) => s.createConversation);
  const setActive = useChatStore((s) => s.setActiveConversation);
  const deleteConversation = useChatStore((s) => s.deleteConversation);
  const theme = useThemeStore((s) => s.theme);
  const toggleTheme = useThemeStore((s) => s.toggleTheme);

  const sb: React.CSSProperties = {
    background: "var(--bg-sidebar)",
    borderRight: "1px solid var(--border-subtle)",
  };

  return (
    <aside className="h-full flex flex-col select-none" style={sb}>
      {/* Header */}
      <div className="px-3 pt-3 pb-2 flex items-center justify-between">
        <button onClick={onToggle}
          className="flex items-center gap-2.5 px-1.5 py-1.5 rounded-lg transition-colors duration-150"
          style={{color:"var(--text-secondary)"}}
          onMouseEnter={e => (e.currentTarget as HTMLElement).style.background = "var(--bg-surface-hover)"}
          onMouseLeave={e => (e.currentTarget as HTMLElement).style.background = "transparent"}>
          <div className="w-6 h-6 rounded-md flex items-center justify-center" style={{background:"var(--bg-icon)"}}>
            <IoBarChartOutline size={14} style={{color:"var(--text-secondary)"}} />
          </div>
          <span className="text-sm font-medium">股票AI助手</span>
        </button>
      </div>

      {/* New Chat */}
      <div className="px-3 pb-3">
        <button onClick={createConversation}
          className="w-full flex items-center gap-3 text-sm transition-colors"
          style={{
            height:40, borderRadius:12, padding:"0 12px",
            background:"transparent", border:"1px solid var(--border-btn)",
            color:"var(--text-secondary)",
          }}
          onMouseEnter={e => {
            const t = e.currentTarget as HTMLElement;
            t.style.background = "var(--bg-surface-hover)";
            t.style.color = "var(--text-primary)";
          }}
          onMouseLeave={e => {
            const t = e.currentTarget as HTMLElement;
            t.style.background = "transparent";
            t.style.color = "var(--text-secondary)";
          }}>
          <IoAdd size={16} /><span>新对话</span>
        </button>
      </div>

      {/* History */}
      <div className="flex-1 overflow-y-auto px-3">
        <div className="px-3 py-2 text-xs font-medium" style={{color:"var(--text-muted)"}}>历史会话</div>
        {conversations.length === 0 ? (
          <div className="px-3 py-8 text-center text-xs" style={{color:"var(--text-muted)"}}>暂无记录</div>
        ) : (
          <div className="space-y-0.5">
            {conversations.map((conv) => (
              <div key={conv.id} onClick={() => setActive(conv.id)}
                className="group flex items-center rounded-xl cursor-pointer transition-colors duration-150 text-sm"
                style={{
                  height:36, padding:"0 12px", borderRadius:10,
                  color: conv.id === activeId ? "var(--text-primary)" : "var(--text-secondary)",
                  background: conv.id === activeId ? "var(--bg-surface-active)" : "transparent",
                }}
                onMouseEnter={e => {
                  if (conv.id !== activeId) (e.currentTarget as HTMLElement).style.background = "var(--bg-surface-hover)";
                }}
                onMouseLeave={e => {
                  if (conv.id !== activeId) (e.currentTarget as HTMLElement).style.background = "transparent";
                }}>
                <span className="truncate flex-1">{conv.title}</span>
                <button onClick={(e) => { e.stopPropagation(); deleteConversation(conv.id); }}
                  className="opacity-0 group-hover:opacity-100 transition-all duration-150 ml-2 shrink-0 p-0.5"
                  style={{color:"var(--text-tertiary)"}} aria-label="删除">
                  <IoTrashOutline size={13} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Watchlist */}
      <div style={{borderTop:"1px solid var(--border-subtle)"}}><WatchList /></div>

      {/* Bottom */}
      <div style={{borderTop:"1px solid var(--border-subtle)"}} className="px-3 py-3 flex flex-col gap-0.5">
        <button onClick={onInsightToggle}
          className="w-full flex items-center gap-3 rounded-xl text-sm transition-colors duration-150"
          style={{
            height:36, padding:"0 12px",
            color: insightOpen ? "var(--text-primary)" : "var(--text-secondary)",
            background: insightOpen ? "var(--bg-surface-active)" : "transparent",
          }}
          onMouseEnter={e => { if (!insightOpen) (e.currentTarget as HTMLElement).style.background = "var(--bg-surface-hover)"; }}
          onMouseLeave={e => { if (!insightOpen) (e.currentTarget as HTMLElement).style.background = "transparent"; }}>
          <IoBarChartOutline size={15} /><span>股票面板</span></button>
        <button onClick={toggleTheme}
          className="w-full flex items-center gap-3 rounded-xl text-sm transition-colors duration-150"
          style={{ height:36, padding:"0 12px", color:"var(--text-secondary)" }}
          onMouseEnter={e => (e.currentTarget as HTMLElement).style.background = "var(--bg-surface-hover)"}
          onMouseLeave={e => (e.currentTarget as HTMLElement).style.background = "transparent"}>
          {theme === "dark" ? <IoSunnyOutline size={15} /> : <IoMoonOutline size={15} />}
          <span>{theme === "dark" ? "亮色模式" : "暗色模式"}</span></button>
      </div>
    </aside>
  );
}
