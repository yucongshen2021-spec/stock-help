import { useEffect, useState } from "react";
import { fetchStockQuote } from "../../utils/api";
import { formatNumber, formatPercent, formatPrice } from "../../utils/format";
import type { StockQuote as SQ } from "../../stores/stockStore";
import { IoClose, IoAdd, IoRemove } from "react-icons/io5";
import { useStockStore } from "../../stores/stockStore";

export default function StockQuote({ code, onClose }: { code: string; onClose: () => void }) {
  const [q, setQ] = useState<SQ | null>(null);
  const [loading, setLoading] = useState(true);
  const wl = useStockStore((s) => s.watchlist);
  const add = useStockStore((s) => s.addToWatchlist);
  const rm = useStockStore((s) => s.removeFromWatchlist);
  const watched = wl.includes(code);

  useEffect(() => { let c = false; setLoading(true); fetchStockQuote(code).then((d) => { if (!c) setQ(d); }).catch(() => {}).finally(() => { if (!c) setLoading(false); }); return () => { c = true; }; }, [code]);
  if (loading) return <div style={{padding:"12px 0", textAlign:"center", fontSize:14, color:"var(--text-muted)"}}>加载中...</div>;
  if (!q) return <div style={{padding:"12px 0", textAlign:"center", fontSize:14, color:"var(--text-muted)"}}>无法加载行情</div>;

  const up = (q.change_pct ?? 0) >= 0;
  const rows = [["今开",formatPrice(q.open)],["昨收",formatPrice(q.prev_close)],["最高",formatPrice(q.high)],["最低",formatPrice(q.low)],["成交量",formatNumber(q.volume)],["成交额",formatNumber(q.amount)],["换手率",q.turnover_rate!=null?`${q.turnover_rate}%`:"--"],["市盈率",q.pe_ratio!=null?q.pe_ratio.toFixed(2):"--"]];

  return (
    <div>
      <div style={{display:"flex", alignItems:"flex-start", justifyContent:"space-between", marginBottom:12}}>
        <div>
          <div style={{fontSize:16, fontWeight:600, color:"var(--text-primary)"}}>{q.name}</div>
          <div style={{fontSize:12, marginTop:2, color:"var(--text-tertiary)"}}>{q.code}</div>
        </div>
        <div style={{display:"flex", alignItems:"center", gap:2}}>
          <button onClick={() => watched ? rm(code) : add(code)}
            style={{width:28, height:28, borderRadius:8, display:"flex", alignItems:"center", justifyContent:"center", color:"var(--text-tertiary)", background:"transparent", border:"none", cursor:"pointer"}}
            onMouseEnter={e => (e.currentTarget as HTMLElement).style.background = "var(--bg-surface-hover)"}
            onMouseLeave={e => (e.currentTarget as HTMLElement).style.background = "transparent"}
            title={watched ? "取消自选" : "加入自选"}>
            {watched ? <IoRemove size={13} /> : <IoAdd size={13} />}</button>
          <button onClick={onClose}
            style={{width:28, height:28, borderRadius:8, display:"flex", alignItems:"center", justifyContent:"center", color:"var(--text-tertiary)", background:"transparent", border:"none", cursor:"pointer"}}
            onMouseEnter={e => (e.currentTarget as HTMLElement).style.background = "var(--bg-surface-hover)"}
            onMouseLeave={e => (e.currentTarget as HTMLElement).style.background = "transparent"}>
            <IoClose size={13} /></button>
        </div>
      </div>
      <div style={{marginBottom:12}}>
        <span style={{fontSize:32, fontWeight:600, color: up ? "var(--color-up)" : "var(--color-down)"}}>{formatPrice(q.price)}</span>
        <div style={{display:"flex", alignItems:"center", gap:8, marginTop:4}}>
          <span style={{fontSize:14, fontWeight:500, color: up ? "var(--color-up)" : "var(--color-down)"}}>{formatPercent(q.change_pct)}</span>
          <span style={{fontSize:14, color: up ? "var(--color-up)" : "var(--color-down)"}}>{q.change_amt!=null?`${q.change_amt>=0?"+":""}${q.change_amt.toFixed(2)}`:"--"}</span>
        </div>
      </div>
      <div style={{display:"grid", gridTemplateColumns:"1fr 1fr", columnGap:12, rowGap:8}}>
        {rows.map(([label,value]) => (
          <div key={label} style={{display:"flex", justifyContent:"space-between"}}>
            <span style={{fontSize:12, color:"var(--text-tertiary)"}}>{label}</span>
            <span style={{fontSize:12, color:"var(--text-secondary)"}}>{value}</span></div>
        ))}
      </div>
    </div>
  );
}
