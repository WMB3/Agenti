import re
import asyncio

class MockConsole:
    def append_stdout(self, message):
        print(message)

live_log_console = MockConsole()

async def analyze_bids(items, vehicle_model, threshold):
    for item in items:
        title = (await item.locator('.item-title a').inner_text()).strip()
        if vehicle_model in title:
            price_text = await item.locator('.detail-item.price span').inner_text()

            # FIX: Ensure clean_price_text is not empty before converting to int
            clean_price_text = re.sub(r'[^\d]', '', price_text)

            # Making sure we only convert to int if it actually consists of digits
            current_bid = int(clean_price_text) if clean_price_text.isdigit() else 0

            if current_bid > threshold:
                live_log_console.append_stdout(f"[SAFETY STOP] Current bid {current_bid} OMR has exceeded threshold {threshold} OMR.\n")
