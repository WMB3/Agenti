import asyncio
import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

from fastapi import Body
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch

from main import app, scraper
from ingestion.scrapers.playwright_scraper import PlaywrightScraper
from google import genai

async def run_benchmark():
    # Make sure api key is set inside the class instance so it passes the check
    scraper.api_key = "test-key"
    num_requests = 10

    # Let's patch `async_playwright` so we don't actually open browsers
    with patch('ingestion.scrapers.playwright_scraper.async_playwright') as mock_playwright:
        mock_p = AsyncMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()

        mock_playwright.return_value.__aenter__.return_value = mock_p
        mock_p.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        mock_page.evaluate.return_value = "Fake content " * 1000

        # Create a mock for google.genai.Client to simulate slow synchronous/asynchronous calls
        class MockModels:
            def generate_content(self, model, contents, config=None):
                time.sleep(1) # simulate slow synchronous blocking
                mock_response = MagicMock()
                mock_response.text = '[]'
                return mock_response

        class MockAioModels:
            async def generate_content(self, model, contents, config=None):
                await asyncio.sleep(1) # simulate slow asynchronous waiting
                mock_response = MagicMock()
                mock_response.text = '[]'
                return mock_response

        class MockAio:
            def __init__(self):
                self.models = MockAioModels()

        class MockGenaiClient:
            def __init__(self, api_key=None):
                self.models = MockModels()
                self.aio = MockAio()

        with patch('ingestion.scrapers.playwright_scraper.genai.Client', new=MockGenaiClient):
            # Patch asyncio.sleep so we don't wait for human hesitation delays
            with patch('ingestion.scrapers.playwright_scraper.asyncio.sleep', new_callable=AsyncMock):

                async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                    payloads = [
                        {"url": f"https://example.com/car/{i}"} for i in range(num_requests)
                    ]

                    start_time = time.time()
                    response = await ac.post("/api/v1/batch_intercept", json=payloads)
                    end_time = time.time()

                    print(f"Status Code: {response.status_code}")
                    print(f"Total time for {num_requests} requests: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    os.environ['GEMINI_API_KEY'] = 'test-key'
    asyncio.run(run_benchmark())
