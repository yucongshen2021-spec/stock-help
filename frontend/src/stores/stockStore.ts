import { create } from "zustand";

export interface StockQuote {
  code: string;
  name: string;
  price: number | null;
  change_pct: number | null;
  change_amt: number | null;
  volume: number | null;
  amount: number | null;
  high: number | null;
  low: number | null;
  open: number | null;
  prev_close: number | null;
  turnover_rate: number | null;
  pe_ratio: number | null;
  total_market_cap: number | null;
}

export interface KLineItem {
  date: string;
  open: number;
  close: number;
  high: number;
  low: number;
  volume: number;
  amount: number;
  turnover: number;
}

interface StockState {
  watchlist: string[];
  watchlistQuotes: Record<string, StockQuote>;
  selectedStock: string | null;
  stockPanelOpen: boolean;

  addToWatchlist: (code: string) => void;
  removeFromWatchlist: (code: string) => void;
  setWatchlistQuote: (code: string, quote: StockQuote) => void;
  setSelectedStock: (code: string | null) => void;
  setStockPanelOpen: (open: boolean) => void;
}

const loadWatchlist = (): string[] => {
  try {
    const saved = localStorage.getItem("watchlist");
    return saved ? JSON.parse(saved) : [];
  } catch {
    return [];
  }
};

const saveWatchlist = (list: string[]) => {
  localStorage.setItem("watchlist", JSON.stringify(list));
};

export const useStockStore = create<StockState>((set) => ({
  watchlist: loadWatchlist(),
  watchlistQuotes: {},
  selectedStock: null,
  stockPanelOpen: false,

  addToWatchlist: (code) =>
    set((s) => {
      if (s.watchlist.includes(code)) return s;
      const next = [...s.watchlist, code];
      saveWatchlist(next);
      return { watchlist: next };
    }),

  removeFromWatchlist: (code) =>
    set((s) => {
      const next = s.watchlist.filter((c) => c !== code);
      saveWatchlist(next);
      return { watchlist: next };
    }),

  setWatchlistQuote: (code, quote) =>
    set((s) => ({
      watchlistQuotes: { ...s.watchlistQuotes, [code]: quote },
    })),

  setSelectedStock: (code) =>
    set({ selectedStock: code, stockPanelOpen: code !== null }),

  setStockPanelOpen: (open) => set({ stockPanelOpen: open }),
}));
