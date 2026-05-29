import { useEffect, useState } from "react";
import { fetchStockNews } from "../../utils/api";

interface NI { title: string; content: string; time: string; source: string; url: string; error?: string; }

export default function StockNews({ code }: { code: string }) {
  const [news, setNews] = useState<NI[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => { let c = false; setLoading(true); fetchStockNews(code, 8).then((d) => { if (!c) setNews(d.filter((n) => !n.error)); }).catch(() => {}).finally(() => { if (!c) setLoading(false); }); return () => { c = true; }; }, [code]);
  if (loading) return <div style={{textAlign:"center",padding:"8px 0",fontSize:14,color:"var(--text-muted)"}}>加载新闻...</div>;
  if (!news.length) return <div style={{textAlign:"center",padding:"8px 0",fontSize:14,color:"var(--text-muted)"}}>暂无新闻</div>;

  return (
    <div style={{display:"flex",flexDirection:"column",gap:8}}>
      {news.map((item, i) => (
        <a key={i} href={item.url} target="_blank" rel="noopener noreferrer"
          style={{
            display:"block", borderRadius:12, padding:"12px 14px",
            background:"var(--bg-surface)", border:"1px solid var(--border-card)",
            textDecoration:"none", transition:"background 120ms ease-out",
          }}>
          <div style={{fontSize:14,fontWeight:500,lineHeight:1.4,marginBottom:6,color:"var(--text-secondary)"}}>{item.title}</div>
          {item.content && <div style={{fontSize:12,lineHeight:1.5,marginBottom:6,color:"var(--text-muted)",overflow:"hidden",textOverflow:"ellipsis",display:"-webkit-box",WebkitLineClamp:2,WebkitBoxOrient:"vertical"}}>{item.content}</div>}
          <div style={{display:"flex",alignItems:"center",gap:8,fontSize:10,color:"var(--text-muted)"}}>{item.source && <span>{item.source}</span>}{item.time && <span>{item.time}</span>}</div>
        </a>
      ))}
    </div>
  );
}
