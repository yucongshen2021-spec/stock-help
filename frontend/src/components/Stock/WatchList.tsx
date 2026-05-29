import { useEffect } from "react";
import { IoClose } from "react-icons/io5";
import { useStockStore } from "../../stores/stockStore";
import { fetchStockQuote } from "../../utils/api";
import { formatPrice, formatPercent } from "../../utils/format";

export default function WatchList() {
  const wl = useStockStore((s) => s.watchlist);
  const quotes = useStockStore((s) => s.watchlistQuotes);
  const setQ = useStockStore((s) => s.setWatchlistQuote);
  const select = useStockStore((s) => s.setSelectedStock);
  const remove = useStockStore((s) => s.removeFromWatchlist);

  useEffect(() => {
    if (!wl.length) return; let c = false;
    const load = async () => { for (const code of wl) { if (c) break; try { const d = await fetchStockQuote(code); if (!c) setQ(code, d); } catch {} } };
    load(); const iv = setInterval(load, 30000); return () => { c = true; clearInterval(iv); };
  }, [wl, setQ]);

  return (
    <div style={{padding:"12px 12px"}}>
      <div style={{color:"var(--text-muted)", fontSize:11, fontWeight:500, marginBottom:8, padding:"0 4px", letterSpacing:"0.02em"}}>自选股</div>
      {!wl.length ? (
        <div style={{textAlign:"center", padding:"12px 0", fontSize:12, color:"var(--text-muted)"}}>暂无自选股</div>
      ) : (
        <div className="space-y-0.5">
          {wl.map((code) => {
            const q = quotes[code]; const up = (q?.change_pct ?? 0) >= 0;
            return (
              <div key={code} className="group"
                style={{
                  width:"100%", display:"flex", alignItems:"center", gap:4,
                  padding:"2px 0",
                }}>
                <button onClick={() => select(code)}
                  style={{
                    width:"100%", display:"flex", alignItems:"center", justifyContent:"space-between",
                    padding:"6px 8px", borderRadius:8, color:"var(--text-secondary)",
                    background:"transparent", border:"none", cursor:"pointer", textAlign:"left",
                  }}
                  onMouseEnter={e => (e.currentTarget as HTMLElement).style.background = "var(--bg-surface-hover)"}
                  onMouseLeave={e => (e.currentTarget as HTMLElement).style.background = "transparent"}>
                  <div style={{minWidth:0}}>
                    <div style={{fontSize:12, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap"}}>{q?.name || code}</div>
                    <div style={{fontSize:10, color:"var(--text-muted)"}}>{code}</div>
                  </div>
                  {q && (
                    <div style={{textAlign:"right", marginLeft:12, flexShrink:0}}>
                      <div style={{fontSize:12, fontWeight:500, color: up ? "var(--color-up)" : "var(--color-down)"}}>{formatPrice(q.price)}</div>
                      <div style={{fontSize:10, color: up ? "var(--color-up)" : "var(--color-down)"}}>{formatPercent(q.change_pct)}</div>
                    </div>
                  )}
                </button>
                <button
                  onClick={() => remove(code)}
                  aria-label={`删除${code}`}
                  className="opacity-0 group-hover:opacity-100 transition-opacity"
                  style={{
                    width:22, height:22, flexShrink:0, borderRadius:6, border:"none",
                    background:"transparent", color:"var(--text-tertiary)", cursor:"pointer",
                    display:"flex", alignItems:"center", justifyContent:"center",
                  }}
                  onMouseEnter={e => (e.currentTarget as HTMLElement).style.background = "var(--bg-surface-hover)"}
                  onMouseLeave={e => (e.currentTarget as HTMLElement).style.background = "transparent"}>
                  <IoClose size={14} />
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
