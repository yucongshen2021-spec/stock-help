import { useState, useRef, useEffect } from "react";
import { IoSearch } from "react-icons/io5";
import { fetchStockSearch } from "../../utils/api";
import { useStockStore } from "../../stores/stockStore";

export default function StockSearch() {
  const [q, setQ] = useState("");
  const [r, setR] = useState<{ code: string; name: string }[]>([]);
  const [open, setOpen] = useState(false);
  const [searching, setSearching] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const timer = useRef<ReturnType<typeof setTimeout>>(undefined);
  const select = useStockStore((s) => s.setSelectedStock);

  useEffect(() => {
    const h = (e: MouseEvent) => { if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false); };
    document.addEventListener("mousedown", h); return () => document.removeEventListener("mousedown", h);
  }, []);

  const search = (v: string) => {
    setQ(v); if (timer.current) clearTimeout(timer.current);
    if (!v.trim()) { setR([]); setOpen(false); return; }
    timer.current = setTimeout(async () => {
      setSearching(true);
      try { const d = await fetchStockSearch(v.trim()); setR(d); setOpen(true); } catch { setR([]); }
      finally { setSearching(false); }
    }, 300);
  };

  return (
    <div ref={ref} style={{position:"relative"}}>
      <div style={{
        display:"flex", alignItems:"center", gap:10, borderRadius:16,
        padding:"0 14px", height:38, transition:"all 120ms ease-out",
        background:"var(--bg-input)", border:"1px solid var(--border-input)",
      }}>
        <IoSearch size={14} style={{color:"var(--text-tertiary)", flexShrink:0}} />
        <input value={q} onChange={(e) => search(e.target.value)}
          onFocus={() => { if (r.length) setOpen(true); }}
          placeholder="搜索股票..."
          style={{
            background:"transparent", outline:"none", border:"none",
            width:"100%", fontSize:14, color:"var(--text-primary)", fontFamily:"inherit",
          }} />
        {searching && <span style={{color:"var(--text-muted)", fontSize:11}}>...</span>}
      </div>
      {open && r.length > 0 && (
        <div style={{
          position:"absolute", top:"100%", left:0, right:0, marginTop:6,
          borderRadius:14, overflow:"hidden", zIndex:50, maxHeight:208, overflowY:"auto",
          background:"var(--bg-dropdown)", border:"1px solid var(--border-input)",
          boxShadow:"var(--shadow-dropdown)",
        }}>
          {r.map((item) => (
            <button key={item.code} onClick={() => { select(item.code); setOpen(false); setQ(""); }}
              style={{
                width:"100%", display:"flex", alignItems:"center", justifyContent:"space-between",
                padding:"10px 16px", background:"transparent", border:"none",
                color:"var(--text-secondary)", cursor:"pointer", textAlign:"left",
                transition:"background 120ms ease-out",
              }}
              onMouseEnter={e => (e.currentTarget as HTMLElement).style.background = "var(--bg-surface-hover)"}
              onMouseLeave={e => (e.currentTarget as HTMLElement).style.background = "transparent"}>
              <span style={{fontSize:14}}>{item.name}</span>
              <span style={{fontSize:12, color:"var(--text-tertiary)"}}>{item.code}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
