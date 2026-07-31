import asyncio
import time
from unittest.mock import patch, MagicMock, AsyncMock
import logging

logging.basicConfig(level=logging.ERROR)

class DummyResponse:
    def __init__(self, text):
        self.text = text

# We will mock genai.Client
from backend.ingestion.scrapers.playwright_scraper import PlaywrightScraper

async def run_benchmark():
    scraper = PlaywrightScraper(api_key="dummy_key", model_id="dummy_model")

    num_concurrent = 3
    urls = [f"http://example.com/dummy{i}" for i in range(num_concurrent)]

    start_time = time.time()

    # We mock playwright to make the setup fast
    with patch("backend.ingestion.scrapers.playwright_scraper.async_playwright") as mock_pw, \
         patch("backend.ingestion.scrapers.playwright_scraper.genai.Client") as mock_client_cls, \
         patch("backend.ingestion.scrapers.playwright_scraper.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:

        # Setup mock playwright
        mock_p = AsyncMock()
        mock_pw.return_value.__aenter__.return_value = mock_p

        mock_browser = AsyncMock()
        mock_p.chromium.launch.return_value = mock_browser

        mock_context = AsyncMock()
        mock_browser.new_context.return_value = mock_context

        mock_page = AsyncMock()
        mock_context.new_page.return_value = mock_page

        # Setup evaluate to return enough text
        mock_page.evaluate.return_value = "dummy content " * 100

        # Setup the mock client
        mock_client = MagicMock()
        mock_client_cls.return_value = mock_client

        # Setup generate_content to simulate a slow API call (1 second)
        # For the baseline, generate_content is synchronous, so it will block
        def sync_slow_generate(*args, **kwargs):
            time.sleep(1.0)
            return DummyResponse('[{"id":"1", "title":"car", "estimated_retail_value": 1000, "estimated_repairs": 100, "auction_fees": 10}]')

        mock_client.models.generate_content.side_effect = sync_slow_generate

        # Also setup async generate_content for the optimized version
        async def async_slow_generate(*args, **kwargs):
            await asyncio.sleep(1.0)
            return DummyResponse('[{"id":"1", "title":"car", "estimated_retail_value": 1000, "estimated_repairs": 100, "auction_fees": 10}]')

        # We need aio.models.generate_content
        mock_aio = MagicMock()
        mock_aio_models = MagicMock()
        mock_aio_models.generate_content = AsyncMock(side_effect=async_slow_generate)
        mock_aio.models = mock_aio_models
        mock_client.aio = mock_aio

        tasks = [scraper.fetch_from_url(url) for url in urls]
        await asyncio.gather(*tasks)

    end_time = time.time()
    duration = end_time - start_time
    print(f"Total time for {num_concurrent} concurrent calls: {duration:.2f} seconds")

if __name__ == "__main__":
    # We must ensure playwright is installed for the scraper to import and run
    # so we will assume the environment is okay since pytest passed earlier.
    asyncio.run(run_benchmark())
