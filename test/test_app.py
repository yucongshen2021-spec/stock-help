"""
Comprehensive app functionality test for 股票AI助手.
Tests layout, chat, stock search, right panel, settings.
"""
from playwright.sync_api import sync_playwright
import sys


def test_app():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            locale="zh-CN",
        )
        page = context.new_page()

        errors = []
        def log(msg):
            print(f"  {msg}")

        try:
            # ========== 1. Navigate and wait ==========
            log("Navigating to http://localhost:5199 ...")
            page.goto("http://localhost:5199", wait_until="domcontentloaded")
            page.wait_for_timeout(3000)  # wait for React/Vite to hydrate
            log("Page loaded")

            # ========== 2. Layout structure ==========
            log("--- Testing Layout Structure ---")

            # TopNav should exist
            header = page.locator("header")
            if header.count() > 0:
                log("PASS: TopNav header exists")
            else:
                errors.append("TopNav header not found")
                log("FAIL: TopNav header not found")

            # Sidebar should exist
            aside_elements = page.locator("aside")
            if aside_elements.count() >= 1:
                log(f"PASS: Found {aside_elements.count()} aside element(s)")
            else:
                errors.append("No aside (sidebar/panel) found")
                log("FAIL: No aside found")

            # "新对话" button in sidebar
            new_chat_btn = page.locator("button:has-text('新对话')")
            if new_chat_btn.count() > 0:
                log("PASS: '新对话' button found")
            else:
                errors.append("'新对话' button not found")
                log("FAIL: '新对话' button not found")

            # Right panel should always be visible now
            right_panel = page.locator("aside.w-\\[360px\\]")
            if right_panel.count() > 0:
                log("PASS: Right panel (360px) always visible")
            else:
                # try alternative selector
                aside_els = page.locator("aside")
                panel_found = False
                for i in range(aside_els.count()):
                    el = aside_els.nth(i)
                    box = el.bounding_box()
                    if box and box["x"] > 800:  # right side
                        panel_found = True
                        break
                if panel_found:
                    log("PASS: Right panel found (position-based)")
                else:
                    errors.append("Right panel not visible")
                    log("FAIL: Right panel not found")

            # ========== 3. Empty state - feature cards ==========
            log("--- Testing Right Panel Empty State ---")

            # When no stock selected, should see "功能总览"
            feature_title = page.locator("text=功能总览")
            if feature_title.count() > 0:
                log("PASS: '功能总览' empty state title visible")
            else:
                log("WARN: '功能总览' not visible (may need stock deselected)")

            # Should see search bar in right panel
            search_inputs = page.locator("input[placeholder='搜索股票...']")
            if search_inputs.count() > 0:
                log("PASS: Stock search input found in right panel")
            else:
                errors.append("Stock search input not found")
                log("FAIL: Stock search input not found")

            # Feature cards
            feature_cards = page.locator(".card-white")
            if feature_cards.count() >= 3:
                log(f"PASS: {feature_cards.count()} feature cards visible")
            else:
                log(f"WARN: {feature_cards.count()} card-white cards (expected 3+)")

            # ========== 4. Chat functionality ==========
            log("--- Testing Chat ---")

            # Empty state in chat window
            chat_empty_title = page.locator("text=股票AI助手")
            if chat_empty_title.count() > 0:
                log("PASS: Chat empty state title visible")
            else:
                log("WARN: Chat empty state title not found")

            # "开始对话" button
            start_chat_btn = page.locator("button:has-text('开始对话')")
            if start_chat_btn.count() > 0:
                log("PASS: '开始对话' button visible")
                start_chat_btn.first.click()
                page.wait_for_timeout(1000)
                log("Clicked '开始对话' - new conversation created")
            else:
                # Try clicking "新对话" in sidebar
                if new_chat_btn.count() > 0:
                    new_chat_btn.first.click()
                    page.wait_for_timeout(1000)
                    log("Clicked '新对话' - new conversation created")

            # Chat input should be visible now
            chat_input = page.locator("textarea[placeholder*='输入你的问题']")
            if chat_input.count() > 0:
                log("PASS: Chat input visible")
            else:
                errors.append("Chat input not visible after creating conversation")
                log("FAIL: Chat input not visible")

            # ========== 5. Settings Panel ==========
            log("--- Testing Settings Panel ---")

            # Find and click settings button (gear icon)
            settings_btn = page.locator("button[aria-label='设置']")
            if settings_btn.count() > 0:
                log("PASS: Settings button found")
                settings_btn.first.click()
                page.wait_for_timeout(500)

                # Settings modal should appear
                settings_title = page.locator("text=设置")
                if settings_title.count() > 0:
                    log("PASS: Settings modal opened")

                    # Check API Key input
                    api_key_input = page.locator("input[placeholder='sk-...']")
                    if api_key_input.count() > 0:
                        log("PASS: API Key input found")
                    else:
                        log("WARN: API Key input not found")

                    # Check model buttons
                    model_btns = page.locator("button:has-text('DeepSeek Chat')")
                    if model_btns.count() > 0:
                        log("PASS: Model buttons visible")
                    else:
                        log("WARN: Model buttons not found")

                    # Close settings
                    close_btn = page.locator("button:has-text('完成')")
                    if close_btn.count() > 0:
                        close_btn.first.click()
                        page.wait_for_timeout(500)
                        log("Settings closed")
                    else:
                        # Click outside to close
                        page.mouse.click(10, 10)
                        page.wait_for_timeout(500)
                else:
                    errors.append("Settings modal did not open")
                    log("FAIL: Settings modal did not open")
            else:
                errors.append("Settings button not found")
                log("FAIL: Settings button not found")

            # ========== 6. Stock Search ==========
            log("--- Testing Stock Search ---")

            # Type in the stock search input
            stock_search = page.locator("input[placeholder='搜索股票...']")
            if stock_search.count() > 0:
                stock_search.first.fill("茅台")
                page.wait_for_timeout(2000)  # wait for debounce + API

                # Check for dropdown results
                dropdown = page.locator("button:has-text('茅台')")
                if dropdown.count() > 0:
                    log(f"PASS: Stock search returned {dropdown.count()} result(s)")

                    # Click the first result
                    dropdown.first.click()
                    page.wait_for_timeout(1000)

                    # Now right panel should show stock details (not empty state)
                    feature_title_after = page.locator("text=功能总览")
                    if feature_title_after.count() == 0:
                        log("PASS: Feature overview replaced by stock details")
                    else:
                        log("WARN: Feature overview still visible after selecting stock")

                    # Should see stock quote section with a close button
                    close_stock_btn = page.locator("button[title='取消自选'], button svg")
                    if page.locator("text=今开").count() > 0:
                        log("PASS: Stock quote details loaded")
                    else:
                        log("WARN: Stock quote details may not have loaded")
                else:
                    log("WARN: No stock search results (backend may be unavailable)")
            else:
                log("SKIP: Stock search input not found")

            # ========== 7. Screenshots ==========
            log("--- Taking Screenshots ---")

            # Take screenshot of current state
            page.screenshot(path="test/screenshot_stock_detail.png")
            log("Saved: test/screenshot_stock_detail.png")

            # Go back to empty state if possible
            close_btn = page.locator("button svg")
            # Force navigate back to home
            page.goto("http://localhost:5199", wait_until="domcontentloaded")
            page.wait_for_timeout(3000)
            page.screenshot(path="test/screenshot_empty_state.png")
            log("Saved: test/screenshot_empty_state.png")

            # Full page screenshot
            page.screenshot(path="test/screenshot_full.png", full_page=True)
            log("Saved: test/screenshot_full.png")

            # ========== 8. Summary ==========
            print()
            if errors:
                print(f"FAIL: {len(errors)} error(s) found:")
                for e in errors:
                    print(f"  - {e}")
                sys.exit(1)
            else:
                print("PASS: All tests passed!")

        except Exception as e:
            print(f"\nERROR during testing: {e}")
            import traceback
            traceback.print_exc()
            try:
                page.screenshot(path="test/screenshot_error.png")
                log("Error screenshot saved: test/screenshot_error.png")
            except:
                pass
            sys.exit(1)
        finally:
            browser.close()


if __name__ == "__main__":
    test_app()
