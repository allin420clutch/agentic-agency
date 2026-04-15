import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            './src/agents/shopify-marketer/session_data',
            headless=False,
            # This makes the browser look like a standard Linux Chrome user
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = await context.new_page()
        await page.goto('https://admin.shopify.com/store/rb-enterprises/products')
        print("LOGIN NOW. Once you see your PRODUCTS (not the error), close the window.")
        await asyncio.sleep(600) # 10 minutes to be safe

asyncio.run(run())
