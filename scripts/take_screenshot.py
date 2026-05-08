import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("http://localhost:8000/", wait_until="networkidle")
        await page.wait_for_timeout(3000) # Wait 3 seconds for animations/data
        out_path = "/Users/prashantkumar/Desktop/Luna_Aura/paper_assets/dashboard_screenshot.png"
        await page.screenshot(path=out_path, full_page=True)
        await browser.close()
        print(f"Screenshot saved to {out_path}")

asyncio.run(main())
