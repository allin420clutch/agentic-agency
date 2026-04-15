import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Launch browser with a persistent folder
        context = await p.chromium.launch_persistent_context(
            './src/agents/shopify-marketer/session_data', 
            headless=False
        )
        page = await context.new_page()
        await page.goto('https://admin.shopify.com')
        print("LOG IN MANUALLY NOW AND COMPLETE 2FA.")
        print("Once you see your Shopify Dashboard, close the browser window.")
        # Keep browser open until you close it manually
        await asyncio.sleep(300) 

asyncio.run(run())
