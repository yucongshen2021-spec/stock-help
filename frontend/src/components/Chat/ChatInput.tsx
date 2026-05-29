import { useState, useRef, useEffect } from "react";
import { IoArrowUp } from "react-icons/io5";

export default function ChatInput({ onSend, disabled }: { onSend: (msg: string) => void; disabled?: boolean }) {
  const [value, setValue] = useState("");
  const ta = useRef<HTMLTextAreaElement>(null);
  const has = value.trim().length > 0;

  useEffect(() => {
    const el = ta.current; if (!el) return;
    el.style.height = "auto"; el.style.height = Math.min(el.scrollHeight, 160) + "px";
  }, [value]);

  const submit = () => { if (!has || disabled) return; onSend(value.trim()); setValue(""); };

  return (
    <div className="shrink-0" style={{padding:"0 32px 24px 32px"}}>
      <div style={{maxWidth:760, margin:"0 auto", position:"relative"}}>
        <div style={{
          display:"flex", alignItems:"flex-end", gap:12,
          minHeight:64,
          background:"var(--bg-input)",
          borderRadius:22,
          border:"1px solid var(--border-input)",
          boxShadow:"var(--shadow-input)",
          padding:"14px 18px",
        }}>
          <textarea ref={ta} value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); submit(); } }}
            placeholder="输入股票代码或问题..."
            disabled={disabled} rows={1}
            style={{
              flex:1, background:"transparent", outline:"none",
              resize:"none", lineHeight:1.5, alignSelf:"center",
              fontSize:16, color:"var(--text-primary)", maxHeight:160,
              border:"none", fontFamily:"inherit",
            }} />
          <button onClick={submit} disabled={!has || disabled}
            style={{
              width:36, height:36, minWidth:36, borderRadius:"50%",
              border:"none", cursor: has && !disabled ? "pointer" : "default",
              background: has && !disabled ? "var(--bg-send-btn)" : "var(--bg-input)",
              color: has && !disabled ? "var(--text-primary)" : "var(--text-muted)",
              display:"flex", alignItems:"center", justifyContent:"center",
              transition:"background 120ms ease-out",
            }}
            onMouseEnter={e => {
              if (has && !disabled) (e.currentTarget as HTMLElement).style.background = "var(--bg-send-btn-hover)";
            }}
            onMouseLeave={e => {
              if (has && !disabled) (e.currentTarget as HTMLElement).style.background = "var(--bg-send-btn)";
            }}
            aria-label="发送">
            <IoArrowUp size={20} />
          </button>
        </div>
        <p style={{textAlign:"center", marginTop:12, fontSize:12, color:"var(--text-muted)"}}>
          AI 分析仅供参考，不构成投资建议
        </p>
      </div>
    </div>
  );
}
