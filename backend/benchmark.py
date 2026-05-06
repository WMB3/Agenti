import asyncio
import time
from unittest.mock import MagicMock, AsyncMock
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestion.scrapers.playwright_scraper import PlaywrightScraper

_original_sleep = asyncio.sleep

async def run_benchmark():
    scraper = PlaywrightScraper(api_key="dummy", model_id="dummy")

    import google.genai as genai

    class MockModels:
        def generate_content(self, *args, **kwargs):
            time.sleep(1)  # blocking sleep
            response = MagicMock()
            response.text = '[{"id": "1", "title": "car", "current_bid": 100}]'
            return response

    class MockAioModels:
        async def generate_content(self, *args, **kwargs):
            # simulate async network delay
            await _original_sleep(1)
            response = MagicMock()
            response.text = '[{"id": "1", "title": "car", "current_bid": 100}]'
            return response

    class MockAio:
        def __init__(self):
            self.models = MockAioModels()

    class MockClient:
        def __init__(self, *args, **kwargs):
            self.models = MockModels()
            self.aio = MockAio()

    genai.Client = MockClient

    from playwright.async_api import async_playwright

    class MockPage:
        async def goto(self, *args, **kwargs):
            pass
        async def wait_for_selector(self, *args, **kwargs):
            pass
        async def evaluate(self, *args, **kwargs):
            return "dummy text" * 100
        @property
        def mouse(self):
            m = MagicMock()
            m.wheel = AsyncMock()
            m.move = AsyncMock()
            return m
        @property
        def viewport_size(self):
            return {"width": 1000, "height": 1000}

    class MockContext:
        async def add_init_script(self, *args, **kwargs):
            pass
        async def new_page(self, *args, **kwargs):
            return MockPage()

    class MockBrowser:
        async def new_context(self, *args, **kwargs):
            return MockContext()
        async def close(self):
            pass

    class MockChromium:
        async def launch(self, *args, **kwargs):
            return MockBrowser()

    class MockPlaywrightContextManager:
        async def __aenter__(self):
            p = MagicMock()
            p.chromium = MockChromium()
            return p
        async def __aexit__(self, *args):
            pass

    import ingestion.scrapers.playwright_scraper
    ingestion.scrapers.playwright_scraper.async_playwright = lambda: MockPlaywrightContextManager()

    # We patch only sleep in the scraper module safely, actually we shouldn't patch it globally if possible.
    # We can just patch random.uniform to return 0.001 and random.randint to return 1 to avoid long sleeps
    import random
    random.uniform = lambda a, b: 0.001
    random.randint = lambda a, b: 1

    start_time = time.time()

    tasks = [scraper.fetch_from_url("http://example.com") for _ in range(5)]
    await asyncio.gather(*tasks)

    end_time = time.time()
    print(f"Time taken for 5 concurrent requests: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
