# GPT-Style UI Overhaul Plan

## Context
修改前端UI以匹配参考图 `ChatGPT Image 2026年5月25日 22_54_22.png` 的GPT风格。

## Reference Image Analysis (1536×1024px)
- **Sidebar**: ~290px wide, bg `#11141a`
- **Main area**: bg `#1a1d23` (flat, no gradient)
- **Elevated surfaces**: `#21242a` (cards, input, suggestion tiles)
- **Text primary**: `#ececec`, secondary: `#b4b4b4`
- **No noise texture, no gradient on body**

## Files to Modify

### 1. `frontend/src/index.css` — Design tokens + base styles
- Replace CSS custom properties with reference colors
- Remove body gradient + noise texture → flat `#1a1d23`
- Update scrollbar, selection, placeholder styles

### 2. `frontend/src/components/Layout/AppLayout.tsx`
- Sidebar width: 244px → 260px

### 3. `frontend/src/components/Layout/Sidebar.tsx`
- Background: `#1a1a1a` → `#11141a`
- All rgba overlays → solid hex colors
- Adjust spacing, borders

### 4. `frontend/src/components/Chat/ChatWindow.tsx`
- Welcome area: update colors
- Suggestion cards: update surface color, borders
- Messages area: update spacing

### 5. `frontend/src/components/Chat/ChatInput.tsx`
- Input container: update surface color, border
- Send button: update colors

### 6. `frontend/src/components/Chat/MessageBubble.tsx`
- User bubble: update background color

### 7. `frontend/src/components/Stock/StockPanel.tsx`
- Panel background, card wrappers

## Verification
- Run `npx vite` dev server
- Compare visual output with reference image
