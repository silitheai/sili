import asyncio
import os
import json
from playwright.async_api import async_playwright
from typing import Dict, Any, Optional

USER_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "browser_sessions")

async def browser_avatar(action: str, url: str = "", params: Optional[Dict[str, Any]] = None) -> str:
    """
    Sili V14 Browser Avatar: Interactive Human-like Browsing.
    Actions: 
    - 'navigate': Go to a URL and return title/summary.
    - 'click': Click a selector.
    - 'type': Type text into a selector.
    - 'screenshot': Take a screenshot for the Vision layer.
    - 'login_hint': Open headed browser for manual login (user support).
    """
    if params is None:
        params = {}

    async with async_playwright() as p:
        # Use persistent context to save cookies/sessions
        browser_type = p.chromium
        headless = params.get("headless", True)
        
        context = await browser_type.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=headless,
            viewport={'width': 1280, 'height': 720}
        )
        
        page = context.pages[0] if context.pages else await context.new_page()
        
        try:
            if action == "navigate":
                await page.goto(url, wait_until="networkidle")
                title = await page.title()
                return f"Successfully navigated to {url}. Page Title: {title}"

            elif action == "click":
                selector = params.get("selector")
                await page.click(selector)
                return f"Clicked selector: {selector}"

            elif action == "type":
                selector = params.get("selector")
                text = params.get("text")
                await page.fill(selector, text)
                return f"Typed '{text}' into {selector}"

            elif action == "screenshot":
                path = params.get("path", "browser_snapshot.png")
                abs_path = os.path.join(os.getcwd(), path)
                await page.screenshot(path=abs_path)
                return f"Screenshot saved to {abs_path}"

            elif action == "login_hint":
                # Opens headed browser for user to log in manually if needed
                await page.goto(url)
                print(f"[BROWSER AVATAR] Headed browser opened for manual intervention at {url}")
                # Keep it open for a bit
                await asyncio.sleep(60)
                return "Manual login window closed after 60s."

            else:
                return f"Error: Unknown action '{action}'"

        except Exception as e:
            return f"Error in Browser Avatar: {str(e)}"
        finally:
            await context.close()

def execute(action: str, url: str = "", params: Optional[Dict[str, Any]] = None) -> str:
    """Entry point for Sili Tool Loader."""
    return asyncio.run(browser_avatar(action, url, params))
