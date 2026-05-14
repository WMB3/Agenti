import asyncio
import time
from unittest.mock import patch, MagicMock, AsyncMock

async def run_benchmark():
    from backend.ingestion.scrapers.playwright_scraper import PlaywrightScraper

    scraper = PlaywrightScraper(api_key="dummy")

    # Mock the page evaluate and others
    async def mock_evaluate(*args, **kwargs):
        return '{"id": "1", "title": "Car"}' * 1000 # Make it long enough

    mock_page = AsyncMock()
    mock_page.evaluate = mock_evaluate
    mock_context = AsyncMock()
    mock_context.new_page.return_value = mock_page
    mock_browser = AsyncMock()
    mock_browser.new_context.return_value = mock_context
    mock_chromium = AsyncMock()
    mock_chromium.launch.return_value = mock_browser

    mock_p = MagicMock()
    mock_p.chromium = mock_chromium

    mock_async_playwright = MagicMock()
    mock_async_playwright.return_value.__aenter__.return_value = mock_p

    # Mock genai client
    class MockResponse:
        text = '[{"id": "1", "title": "Car", "estimated_retail_value": 10000, "estimated_repairs": 1000, "auction_fees": 100, "current_bid": 5000}]'

    def mock_generate_content(*args, **kwargs):
        time.sleep(1)  # Simulate blocking network call
        return MockResponse()

    async def mock_async_generate_content(*args, **kwargs):
        await asyncio.sleep(1) # Simulate non-blocking network call
        return MockResponse()

    # We need to mock genai.Client
    with patch('backend.ingestion.scrapers.playwright_scraper.async_playwright', mock_async_playwright), \
         patch('backend.ingestion.scrapers.playwright_scraper.asyncio.sleep', AsyncMock()), \
         patch('backend.ingestion.scrapers.playwright_scraper.genai.Client') as MockClient:

        mock_instance = MockClient.return_value
        mock_instance.models.generate_content = mock_generate_content
        mock_instance.aio.models.generate_content = mock_async_generate_content

        start_time = time.time()

        # Run 5 concurrent fetches
        tasks = [scraper.fetch_from_url("http://example.com") for _ in range(5)]
        await asyncio.gather(*tasks)

        end_time = time.time()
        print(f"Time taken for 5 concurrent requests: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
