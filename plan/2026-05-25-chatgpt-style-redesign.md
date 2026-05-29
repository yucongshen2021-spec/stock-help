# ChatGPT-Style UI Redesign — Implementation Plan

Date: 2026-05-25

## Context

The current Apple-light-theme UI, while functional, doesn't match the professional AI assistant aesthetic users expect from modern chat applications like ChatGPT. The layout is too crowded (4 columns), the sidebar is light-colored, message bubbles have borders and avatars, and the stock panel permanently occupies 360px of screen width. This redesign transforms the interface into a ChatGPT-inspired professional AI assistant look while preserving all stock analysis features.

## Design Tokens

### Dark Sidebar
```
bg:           #171717
hover:        #2a2a2a
active:       #212121
text:         #ECECEC
text-muted:   #8E8E8E
divider:      rgba(255,255,255,0.06)
width:        260px (collapsed: 0px)
```

### Chat Area
```
bg:           #ffffff
message gap:  24px (space-y-6)
max-width:    max-w-3xl (768px)
body text:    15px, line-height 1.6
```

### Message Bubbles
```
User:     bg-[#F4F4F4], rounded-[18px], no border, no avatar
          max-w-[75%], ml-auto, px-4 py-2.5
Assistant: no bubble, no border, no avatar, plain text on white
           text-15px leading-relaxed
```

### Chat Input
```
Container: bg-white, border-t border-[#e5e5e5], px-4 py-3
Input:     bg-[#F4F4F4], rounded-[26px], no border
           shadow: 0 2px 6px rgba(0,0,0,0.08)
           focus: shadow-[0_2px_6px_rgba(0,0,0,0.12)_0_0_0_1px_rgba(0,0,0,0.04)]
Send btn:  w-9 h-9 rounded-full
           empty: bg-[#d9d9d9] text-white
           active: bg-primary text-white
           transition: 0.15s ease
```

## Layout Change

```
Before:
| TopNav 40px                                         |
| Sidebar 256px | ChatWindow flex-1 | StockPanel 360px |

After:
| Sidebar 260px | ChatWindow flex-1 | StockPanel 380px (toggle) |
```

- **Remove TopNav entirely** — settings gear moves to sidebar footer
- **Sidebar** — dark, collapsible (toggle button), conversation history + watchlist
- **ChatWindow** — cleaner centered chat with borderless messages
- **StockPanel** — toggle via button in sidebar or chat area, slides in/out

## Files to Modify

### 1. `index.css` — Theme token updates
- Remove `--color-surface-dark: #fafafc`, replace with `--color-sidebar: #171717`
- Add sidebar text colors: `--color-sidebar-text: #ECECEC`, `--color-sidebar-muted: #8E8E8E`
- Add `--color-input-bg: #F4F4F4`
- Remove `card-white` utility (no longer needed)
- Update scrollbar for dark sidebar

### 2. `App.tsx` — Remove TopNav, add StockPanel toggle state
- Remove `<SettingsPanel />` import (move to sidebar)
- Pass `stockPanelOpen` state to AppLayout
- Keep SettingsPanel at root (or move into sidebar)

### 3. `AppLayout.tsx` — New layout without TopNav
- Remove TopNav import and render
- Add sidebar toggle state management
- StockPanel as toggle (read from stockStore.stockPanelOpen)

### 4. `Sidebar.tsx` — Dark theme, collapsible, settings access
- bg-[#171717], all text inverted to light colors
- Add collapse toggle button (hamburger icon)
- Add settings gear at bottom of sidebar
- Dark conversation list items with subtle active/hover states
- Collapsed state: width 0, only toggle button visible
- Transition: width 0.2s ease

### 5. `ChatWindow.tsx` — Borderless messages, larger text
- Remove avatar rendering from empty state
- Update empty state: simpler, no glow/ring effects
- Body text: 15px (update styles)
- Remove per-message avatar from active state rendering

### 6. `MessageBubble.tsx` — No borders, no avatars
- **Remove avatars entirely** (both user and assistant)
- User message: `bg-[#F4F4F4] rounded-[18px] max-w-[75%] ml-auto`
- Assistant message: **no bubble** — plain text, `text-[15px] leading-relaxed`
- Remove `MarkdownRenderer` wrapper div for assistant (just render inline)

### 7. `ChatInput.tsx` — Shadow instead of border
- Input container: remove `border-border`, add `shadow-[0_2px_6px_rgba(0,0,0,0.08)]`
- bg: `#F4F4F4` instead of `bg-surface-input`
- Focus: enhanced shadow, no colored ring
- Send button: `w-9 h-9 rounded-full`, transition bg-color 0.15s
- Send button empty: `bg-[#d9d9d9]`, active: `bg-primary`

### 8. `MarkdownRenderer.tsx` — Cleaner code blocks, larger text
- Code blocks: `bg-[#F7F7F7]`, no border
- Table styles: cleaner borders
- Body paragraph: 15px

### 9. `StockPanel.tsx` — Toggle slide-in
- Wider: 380px
- Add slide-in animation (transform + transition)
- Read `stockPanelOpen` from store
- When closed: `translate-x-full` or `w-0 overflow-hidden`
- Keep empty state and active state as-is but polish styling

### 10. `StockSearch.tsx`, `StockQuote.tsx`, `KLineChart.tsx`, `TechnicalSummary.tsx`, `StockNews.tsx`
- Minor polish: ensure card-white doesn't break (will be removed)
- Use direct styling instead of card-white utility
- Ensure K-line chart works when data is available

### 11. `SettingsPanel.tsx` — Cleaner modal, accessible from sidebar
- Remove TopNav gear icon trigger (now in sidebar)
- Keep modal styling but simplify

### 12. `WatchList.tsx` — Dark sidebar compatible
- All text light-colored
- Up/down colors still #34c759/#ff3b30

## Files NOT Modified
- `stores/chatStore.ts` — no changes
- `stores/stockStore.ts` — no changes
- `stores/settingsStore.ts` — no changes
- `utils/api.ts` — no changes
- `utils/format.ts` — no changes
- Backend files — no changes

## Verification

1. Build: `npm run build` (tsc + vite) passes with zero errors
2. Playwright E2E test:
   - App loads with dark sidebar and centered chat
   - Sidebar collapses/expands with toggle button
   - Create conversation → messages appear without avatars/borders
   - User message: gray pill, right-aligned
   - Assistant message: plain text, left-aligned
   - Input has shadow, not border
   - Send button transitions gray→blue when text entered
   - Stock panel toggles via sidebar button
3. Visual check: take screenshots at each state
4. Console: zero errors
