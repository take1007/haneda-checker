import asyncio
from playwright.async_api import async_playwright
import requests
import os

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
URL = "https://hnd-rsv.aeif.or.jp/airport2/app/toppage"

TARGET_DATES = ["2025/07/07", "2025/07/15", "2025/07/20", "2025/07/21", "2025/07/22", "2025/07/23", "2025/07/24"]
AVAILABLE_CLASSES = ["konzatsu", "yoyaku", "empty", "vacant"]

P2_NEXT_BUTTON_SELECTOR = '#cal00_next'
P3_NEXT_BUTTON_SELECTOR = '#cal10_next'
P2_JULY_CALENDAR = '#cal00'
P3_JULY_CALENDAR = '#cal10'

async def check_section(page, section, next_sel, cal_sel):
    await page.locator(next_sel).wait_for(state="visible", timeout=10000)
    await page.click(next_sel)
    await page.wait_for_timeout(3000)
    results = []
    for d in TARGET_DATES:
        el = await page.query_selector(f'{cal_sel} td[id$="{d}"]')
        if el and await el.get_attribute("class") in AVAILABLE_CLASSES:
            results.append((section, d))
    return results

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(URL)
        res = []
        res += await check_section(page, "P2", P2_NEXT_BUTTON_SELECTOR, P2_JULY_CALENDAR)
        res += await check_section(page, "P3", P3_NEXT_BUTTON_SELECTOR, P3_JULY_CALENDAR)
        await browser.close()

    if res:
        msg = "🚗 空きあり！\n" + "\n".join(f"{s} → {d}" for s, d in res) + f"\n▶ {URL}"
        requests.post(DISCORD_WEBHOOK_URL, json={"content": msg})

if __name__ == "__main__":
    asyncio.run(main())
