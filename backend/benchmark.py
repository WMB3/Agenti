import asyncio
import time
from unittest.mock import AsyncMock, patch, MagicMock

import ingestion.scrapers.playwright_scraper as ps

class FakeClient:
    def __init__(self, api_key):
        self.models = MagicMock()
        self.aio = MagicMock()

        # Mock blocking generate_content
        def mock_gc(*args, **kwargs):
            time.sleep(1) # simulate 1s blocking call
            class Resp:
                text = '[]'
            return Resp()
        self.models.generate_content.side_effect = mock_gc

        # Mock async generate_content
        async def mock_gc_async(*args, **kwargs):
            await asyncio.sleep(1) # simulate 1s async call
            class Resp:
                text = '[]'
            return Resp()
        self.aio.models.generate_content = AsyncMock(side_effect=mock_gc_async)


async def run_benchmark():
    scraper = ps.PlaywrightScraper(api_key="dummy")

    # We will use asyncio.sleep instead of asyncio.sleep(random.uniform) to speed up test
    async def mock_sleep(*args, **kwargs): pass

    class MockPage:
        async def goto(self, *args, **kwargs): pass
        async def wait_for_selector(self, *args, **kwargs): pass
        async def evaluate(self, *args, **kwargs): return "1" * 400

        # mock mouse things
        class MockMouse:
            async def wheel(self, *args, **kwargs): pass
            async def move(self, *args, **kwargs): pass
        mouse = MockMouse()
        @property
        def viewport_size(self): return {"width": 100, "height": 100}

    class MockContext:
        async def add_init_script(self, *args, **kwargs): pass
        async def new_page(self, *args, **kwargs): return MockPage()

    class MockBrowser:
        async def new_context(self, *args, **kwargs): return MockContext()
        async def close(self, *args, **kwargs): pass

    class MockChromium:
        async def launch(self, *args, **kwargs): return MockBrowser()

    class MockPlaywrightContext:
        @property
        def chromium(self): return MockChromium()
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): pass

    def mock_playwright():
        return MockPlaywrightContext()

    with patch('ingestion.scrapers.playwright_scraper.async_playwright', side_effect=mock_playwright):
        with patch('ingestion.scrapers.playwright_scraper.asyncio.sleep', new_callable=AsyncMock) as ms:
            ms.side_effect = mock_sleep
            with patch('google.genai.Client', side_effect=FakeClient):
                start = time.time()
                tasks = [scraper.fetch_from_url("http://example.com") for _ in range(3)]
                await asyncio.gather(*tasks)
                end = time.time()
                print(f"Total time for 3 concurrent fetches: {end - start:.2f} seconds")

asyncio.run(run_benchmark())
