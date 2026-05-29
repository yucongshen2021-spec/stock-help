# Apple Light Theme + Full Feature Panel — Design Spec

Date: 2026-05-24

## Summary

Transform the current dark tech theme into an Apple-style bright interface per DESIGN.md. Make the right stock panel always visible so all features (search, quote, K-line, technical summary, news) are one glance away instead of hidden behind a click on watchlist.

## Color Migration

| Token | Old (Dark) | New (Apple) |
|---|---|---|
| canvas (main bg) | `#0a0e1a` | `#f5f5f7` |
| card bg | `rgba(15,20,35,0.65)` | `#ffffff` |
| sidebar bg | `rgba(8,11,20,0.4)` | `#fafafc` |
| topnav bg | `rgba(8,11,20,0.8)` | `#ffffff` |
| primary | `#00d4ff` | `#0066cc` |
| primary-focus | `#00e5ff` | `#0071e3` |
| ink (text) | `#e8eaed` | `#1d1d1f` |
| ink-dim | `#9aa0b0` | `#333333` |
| ink-muted | `#5c6378` | `#7a7a7a` |
| border | `rgba(0,212,255,0.12)` | `#e0e0e0` |
| up (涨) | `#00e676` | `#34c759` |
| down (跌) | `#ff5252` | `#ff3b30` |
| surface-dark | `#080b14` | (removed) |

Remove utilities: `.bg-grid`, `.glass`, `.glass-glow`, `.glow-ring`, `.glow-accent`, `.float-card`.

## Layout Changes

### Before
```
TopNav | Sidebar(256px) | ChatWindow(flex-1) | StockPanel(384px, conditional)
```
StockPanel only renders when `stockPanelOpen && selectedStock`.

### After
```
TopNav | Sidebar(260px) | ChatWindow(flex-1) | RightPanel(360px, always visible)
```
RightPanel always renders. When no stock selected, shows a "welcome" placeholder with feature preview cards.

## Component Changes

### 1. `index.css` — Full rewrite
- Replace all `@theme` color tokens
- Remove `.bg-grid`, `.glass`, `.glass-glow`, `.glow-ring`, `.glow-accent`, `.float-card`
- Add Apple-style utilities: `.card-white` (white bg + hairline border + 18px radius)
- Body bg becomes `#f5f5f7`

### 2. `TopNav.tsx`
- bg `#ffffff`, border-b `#e0e0e0`
- Logo icon: `#0066cc`
- Text: `#1d1d1f`

### 3. `Sidebar.tsx`
- bg `#fafafc`, border-r `#e0e0e0`
- New chat button: Action Blue pill (`#0066cc` bg, white text)
- Active conversation: `#f5f5f7` bg + left 3px `#0066cc` bar
- Text: `#1d1d1f` / dim: `#333333` / muted: `#7a7a7a`

### 4. `AppLayout.tsx`
- Remove `.bg-grid` class

### 5. `App.tsx`
- `rightPanel={<StockPanel />}` → rightPanel always present (StockPanel handles its own empty state)

### 6. `StockPanel.tsx` — Major refactor
- Remove conditional `if (!stockPanelOpen || !selectedStock) return null`
- Always render: when no stock selected, show feature overview cards
- When stock selected, show current detailed view
- Empty state: 3 preview cards (实时行情, K线图, 技术分析) with search bar on top

### 7. `ChatWindow.tsx`
- bg `#f5f5f7`
- Empty state icon: white circle bg (not glow)
- Title color: `#1d1d1f`

### 8. `MessageBubble.tsx`
- User: `#0066cc` at ~10% opacity bg, right aligned
- Assistant: white card `#ffffff` + 1px `#e0e0e0` border, no glass

### 9. `ChatInput.tsx`
- White pill bg + `#e0e0e0` border
- Focus: `#0066cc` border + subtle focus ring

### 10. `StockQuote.tsx`, `KLineChart.tsx`, `TechnicalSummary.tsx`, `StockNews.tsx`, `StockSearch.tsx`
- White card containers
- Text colors updated to Apple palette
- ECharts: light background, adjust axis/label colors

### 11. `WatchList.tsx`
- Light theme colors
- Price colors: `#34c759` / `#ff3b30`

### 12. `SettingsPanel.tsx`
- White modal bg + hairline border
- Input focus: `#0066cc`
- Model buttons: Apple pill style

### 13. `MarkdownRenderer.tsx`
- Code blocks: light bg, dark text
- Tables: light border
- Links: `#0066cc`

## Files to Modify

1. `frontend/src/index.css` — full color/system rewrite
2. `frontend/src/App.tsx` — minor layout change
3. `frontend/src/components/Layout/AppLayout.tsx` — remove bg-grid
4. `frontend/src/components/Layout/TopNav.tsx` — light theme
5. `frontend/src/components/Layout/Sidebar.tsx` — light theme
6. `frontend/src/components/Chat/ChatWindow.tsx` — light theme, empty state
7. `frontend/src/components/Chat/MessageBubble.tsx` — light theme
8. `frontend/src/components/Chat/ChatInput.tsx` — light theme
9. `frontend/src/components/Chat/MarkdownRenderer.tsx` — light theme
10. `frontend/src/components/Stock/StockPanel.tsx` — always visible + empty state
11. `frontend/src/components/Stock/StockQuote.tsx` — light theme
12. `frontend/src/components/Stock/StockSearch.tsx` — light theme
13. `frontend/src/components/Stock/KLineChart.tsx` — light theme + ECharts
14. `frontend/src/components/Stock/TechnicalSummary.tsx` — light theme
15. `frontend/src/components/Stock/StockNews.tsx` — light theme
16. `frontend/src/components/Stock/WatchList.tsx` — light theme
17. `frontend/src/components/Settings/SettingsPanel.tsx` — light theme

## Behavior

- Right panel is ALWAYS visible (360px)
- When no stock selected: shows "功能总览" placeholder with search + feature cards
- When stock selected: shows full quote + K-line + technical + news stack (existing behavior)
- Clicking "X" on quote returns to overview (does not hide panel)
- Watchlist click still opens that stock in the panel

## What Does NOT Change

- Store logic (zustand stores remain untouched)
- API layer (utils/api.ts unchanged)
- Backend (no changes)
- Markdown renderer logic (only color tokens)
- ECharts option structure (only theme colors for bg/axis/labels)
