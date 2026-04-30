import os
import logging
import json
import random
import asyncio
from typing import List
from playwright.async_api import async_playwright
from google import genai
from google.genai import types
from ..base import ScraperSource
from ..models import AuctionItem, Bid

logger = logging.getLogger(__name__)

class PlaywrightScraper(ScraperSource):
    def __init__(self, api_key: str = None, model_id: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_id = model_id or os.getenv("MODEL_ID", "gemini-1.5-flash")

    @property
    def source_name(self) -> str:
        return "playwright_gemini_scraper"

    async def _human_hesitation(self, page):
        """Ghost-Standard: Behavioral Ghosting"""
        # Randomized scroll and jitter
        scroll_amount = random.randint(100, 600)
        await page.mouse.wheel(0, scroll_amount)
        # Jitter Modulation: adding 200ms to 1500ms of random delay
        await asyncio.sleep(random.uniform(0.2, 1.5))

        viewport = page.viewport_size
        if viewport:
            x = random.randint(0, viewport['width'])
            y = random.randint(0, viewport['height'])
            # Human-like mouse move
            await page.mouse.move(x, y, steps=random.randint(5, 15))
            await asyncio.sleep(random.uniform(0.1, 0.5))

    async def fetch_items(self) -> List[AuctionItem]:
        raise NotImplementedError("Use fetch_from_url with a URL.")

    async def fetch_from_url(self, url: str) -> List[AuctionItem]:
        if not self.api_key:
            raise Exception("GEMINI_API_KEY is not set.")

        async with async_playwright() as p:
            # Ghost-Standard: JA3/TLS Fingerprint Randomization via context headers and args
            browser = await p.chromium.launch(
                headless=True, 
                args=[
                    "--no-sandbox", 
                    "--disable-setuid-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                    "--window-position=0,0",
                    "--ignore-certificate-errors",
                    "--ignore-certificate-errors-spki-list",
                    "--user-agent=Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36"
                ]
            )
            
            # Shadow-Layer: Morphing User-Agent and Viewport
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
                viewport={"width": random.randint(375, 414), "height": random.randint(812, 896)},
                is_mobile=True,
                has_touch=True,
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1"
                }
            )
            
            # Stealth: Injecting webdriver bypass script
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

            page = await context.new_page()
            logger.info(f"Initiating Ghost-Intercept (Evasion Active): {url}")
            
            try:
                # Add random delay before navigation
                await asyncio.sleep(random.uniform(1.0, 3.0))
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                
                # Behavioral Ghosting: Recursive Jitter
                for _ in range(random.randint(2, 5)):
                    await self._human_hesitation(page)
                
                # Wait for content with randomized timeout
                if "opensooq.com" in url:
                    await page.wait_for_selector("li.listItem", timeout=30000)
                elif "olxoman" in url or "dubizzle.com.om" in url:
                    await page.wait_for_selector("div[data-aut-id='itemCard']", timeout=30000)
                else:
                    await asyncio.sleep(random.uniform(5, 8))

                text_content = await page.evaluate("document.body.innerText")
                
                if not text_content or len(text_content.strip()) < 300:
                    raise Exception("Page content insufficient or blocked.")

                client = genai.Client(api_key=self.api_key)
                
                # Financial Forensics Prompt (strictly following the 15% safety buffer directive)
                prompt = f"""
                Extract car listing details from the following marketplace text (Oman market).
                Return a list of objects with:
                - id (string)
                - title (string)
                - year (number)
                - mileage (string)
                - damage (string or "N/A")
                - current_bid (number)
                - currency (string, usually OMR)
                - lot_number (string or "N/A")
                - image_url (string)
                - estimated_retail_value (number)
                - estimated_repairs (number)
                - auction_fees (number)
                
                RAW TEXT FROM {url}:
                {text_content[:15000]}
                """

                response = await client.aio.models.generate_content(
                    model=self.model_id,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                    )
                )
                
                raw_items = json.loads(response.text)
                if not isinstance(raw_items, list):
                    if isinstance(raw_items, dict):
                        for key in raw_items:
                            if isinstance(raw_items[key], list):
                                raw_items = raw_items[key]
                                break
                
                items = []
                for ri in raw_items:
                    retail_val = float(ri.get('estimated_retail_value', 0))
                    repairs = float(ri.get('estimated_repairs', 0))
                    fees = float(ri.get('auction_fees', 0))

                    # Financial Forensics: (Retail_Value * 0.8) - (Estimated_Repairs * 1.15) - Auction_Fees
                    adjusted_repairs = repairs * 1.15
                    max_bid = (retail_val * 0.8) - adjusted_repairs - fees

                    current_bid = float(ri.get('current_bid', ri.get('currentBid', 0)))
                    total_cost = current_bid + adjusted_repairs + fees
                    roi = ((retail_val - total_cost) / total_cost * 100) if total_cost > 0 else 0

                    item = AuctionItem(
                        id=str(ri.get('id', ri.get('lot_number', '0'))),
                        title=ri.get('title', 'Unknown Vehicle'),
                        year=int(ri.get('year', 0)) if str(ri.get('year', '0')).isdigit() else 0,
                        mileage=str(ri.get('mileage', 'Unknown')),
                        damage=str(ri.get('damage', 'None')),
                        current_bid=current_bid,
                        currency=ri.get('currency', 'OMR'),
                        lot_number=str(ri.get('lot_number', 'Unknown')),
                        image_url=ri.get('image_url', ri.get('image', "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=600")),
                        estimated_retail_value=retail_val,
                        estimated_repairs=adjusted_repairs,
                        auction_fees=fees,
                        max_bid=max_bid,
                        roi_percentage=roi,
                        source=f"web_scraper:{url}",
                        raw_data=ri
                    )
                    items.append(item)
                    
                return items

            except Exception as e:
                logger.error(f"Playwright Ghost-Scraper Failed: {e}")
                raise e
            finally:
                await browser.close()
