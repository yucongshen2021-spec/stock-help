import { useStockStore } from "../../stores/stockStore";
import StockQuote from "./StockQuote";
import StockSearch from "./StockSearch";
import KLineChart from "./KLineChart";
import TechnicalSummary from "./TechnicalSummary";
import StockNews from "./StockNews";

export default function StockPanel() {
  const selectedStock = useStockStore((s) => s.selectedStock);
  const setSelectedStock = useStockStore((s) => s.setSelectedStock);
  const quotes = useStockStore((s) => s.watchlistQuotes);

  return (
    <aside className="h-full flex flex-col overflow-y-auto select-none"
      style={{
        background:"var(--bg-surface)",
        borderLeft:"1px solid var(--border-subtle)",
      }}>
      <div style={{padding:"16px 16px 12px 16px"}}><StockSearch /></div>

      {!selectedStock ? (
        <div className="flex-1 flex items-center justify-center" style={{padding:"0 16px 16px 16px"}}>
          <div className="text-center">
            <p style={{color:"var(--text-muted)", fontSize:14, marginBottom:4}}>选择股票查看详情</p>
            <p style={{color:"var(--text-muted)", fontSize:13}}>搜索代码或从自选股选择</p>
          </div>
        </div>
      ) : (
        <div style={{padding:"0 16px 16px 16px", display:"flex", flexDirection:"column", gap:16}}>
          {[
            <StockQuote key="quote" code={selectedStock} onClose={() => setSelectedStock(null)} />,
            <TechnicalSummary key="tech" code={selectedStock} />,
            <KLineChart key="chart" code={selectedStock} name={quotes[selectedStock]?.name || selectedStock} />,
            <StockNews key="news" code={selectedStock} />,
          ].map((child, i) => (
            <div key={i} style={{
              borderRadius:14, padding:14,
              background:"var(--bg-surface)",
              border:"1px solid var(--border-card)",
            }}>
              {child}
            </div>
          ))}
        </div>
      )}
    </aside>
  );
}
