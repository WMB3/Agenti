import asyncio
import time
from unittest.mock import patch, MagicMock, AsyncMock
from backend.ingestion.scrapers.playwright_scraper import PlaywrightScraper

class MockGenaiClient:
    def __init__(self, *args, **kwargs):
        self.models = MockModels()
        self.aio = MockAio()

class MockModels:
    def generate_content(self, *args, **kwargs):
        time.sleep(2) # Simulating synchronous network block
        mock_response = MagicMock()
        mock_response.text = '[]'
        return mock_response

class MockAioModels:
    async def generate_content(self, *args, **kwargs):
        await asyncio.sleep(2) # Simulating async network wait
        mock_response = MagicMock()
        mock_response.text = '[]'
        return mock_response

class MockAio:
    def __init__(self):
        self.models = MockAioModels()

async def background_task():
    # A task that runs frequently to check if event loop is blocked
    start_time = time.time()
    for _ in range(10):
        await asyncio.sleep(0.2)
    end_time = time.time()
    return end_time - start_time

@patch('backend.ingestion.scrapers.playwright_scraper.genai.Client', new=MockGenaiClient)
@patch('backend.ingestion.scrapers.playwright_scraper.async_playwright')
async def run_benchmark(mock_playwright):

    # Mock playwright objects
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    mock_page.evaluate.return_value = "dummy content" * 100
    mock_browser = AsyncMock()
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page

    mock_p = AsyncMock()
    mock_p.chromium.launch.return_value = mock_browser
    mock_playwright.return_value.__aenter__.return_value = mock_p

    scraper = PlaywrightScraper(api_key="dummy")

    # We want the background task to run while fetch_from_url runs generate_content.
    # Since fetch_from_url awaits things, it will yield to the event loop.
    # Once it hits the synchronous time.sleep(2) in MockModels, it will block.

    # Let's override the sleep to make it fast but still yield
    original_sleep = asyncio.sleep
    async def fast_sleep(delay):
        if delay > 0.5: # only fast forward long sleeps
            await original_sleep(0.01)
        else:
            await original_sleep(delay)

    with patch('backend.ingestion.scrapers.playwright_scraper.asyncio.sleep', new=fast_sleep):
        task1 = asyncio.create_task(scraper.fetch_from_url("http://example.com"))
        task2 = asyncio.create_task(background_task())

        start = time.time()
        try:
            await task1
        except Exception as e:
            print("Error in scraper:", e)
        end = time.time()
        bg_time = await task2

        print(f"Scraping took: {end - start:.2f}s")
        print(f"Background task (expected ~2.0s without blocking) took: {bg_time:.2f}s")
        print(f"Event loop block delay (approx bg_time - 2.0s): {bg_time - 2.0:.2f}s")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
