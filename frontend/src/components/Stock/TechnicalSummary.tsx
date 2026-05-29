import { useEffect, useState } from "react";
import { fetchAnalysis } from "../../utils/api";
import { IoTrendingUp, IoTrendingDown, IoRemove } from "react-icons/io5";

interface AD { latest_price: number; ma5: number; ma10: number; ma20: number; ma60: number; ma_pattern: string; macd_signal: string; dif: number; dea: number; volume_trend: string; price_5d_change: number; price_10d_change: number; high_20d: number; low_20d: number; price_position_20d: number; error?: string; }

export default function TechnicalSummary({ code }: { code: string }) {
  const [d, setD] = useState<AD | null>(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => { let c = false; setLoading(true); fetchAnalysis(code).then((r) => { if (!c) setD(r); }).catch(() => {}).finally(() => { if (!c) setLoading(false); }); return () => { c = true; }; }, [code]);
  if (loading) return <div style={{textAlign:"center",padding:"8px 0",fontSize:14,color:"var(--text-muted)"}}>分析中...</div>;
  if (!d || d.error) return <div style={{textAlign:"center",padding:"8px 0",fontSize:14,color:"var(--text-muted)"}}>{d?.error || "无法分析"}</div>;

  const bull = d.ma_pattern.includes("多头") || d.ma_pattern.includes("偏强");
  const bear = d.ma_pattern.includes("空头") || d.ma_pattern.includes("偏弱");

  return (
    <div>
      <div style={{display:"flex",alignItems:"center",gap:8,marginBottom:12,padding:"8px 12px",borderRadius:12,background:"var(--bg-surface)",border:"1px solid var(--border-card)"}}>
        {bull ? <IoTrendingUp size={15} className="text-up" /> : bear ? <IoTrendingDown size={15} className="text-down" /> : <IoRemove size={15} style={{color:"var(--text-muted)"}} />}
        <span style={{fontSize:14,fontWeight:600,color:bull?"var(--color-up)":bear?"var(--color-down)":"var(--text-secondary)"}}>{d.ma_pattern}</span>
      </div>
      <div style={{display:"flex",flexDirection:"column",gap:8}}>
        {[["MACD 信号",d.macd_signal],["量能趋势",d.volume_trend],["近5日",`${d.price_5d_change>=0?"+":""}${d.price_5d_change}%`,d.price_5d_change>=0?"text-up":"text-down"],["近10日",`${d.price_10d_change>=0?"+":""}${d.price_10d_change}%`,d.price_10d_change>=0?"text-up":"text-down"],["20日位置",`${d.price_position_20d}%`],["20日高/低",`${d.high_20d} / ${d.low_20d}`]].map(([label,value,color]) => (
          <div key={label as string} style={{display:"flex",justifyContent:"space-between"}}>
            <span style={{fontSize:12,color:"var(--text-tertiary)"}}>{label}</span>
            <span style={{fontSize:12,color:color?undefined:"var(--text-secondary)"}} className={color as string || ""}>{value as string}</span></div>
        ))}
        <div style={{paddingTop:10,marginTop:4,display:"grid",gridTemplateColumns:"1fr 1fr",columnGap:12,rowGap:6,borderTop:"1px solid var(--border-card)"}}>
          {[["MA5",d.ma5],["MA10",d.ma10],["MA20",d.ma20],["MA60",d.ma60]].map(([label,value]) => (
            <div key={label} style={{display:"flex",justifyContent:"space-between"}}>
              <span style={{fontSize:12,color:"var(--text-tertiary)"}}>{label}</span>
              <span style={{fontSize:12,color:d.latest_price>=(value as number)?"var(--color-up)":"var(--color-down)"}}>{value as number}</span></div>
          ))}
        </div>
      </div>
    </div>
  );
}
