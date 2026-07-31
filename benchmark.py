import asyncio
import time
from unittest.mock import patch, MagicMock, AsyncMock

# We will mock playwright and genai to avoid actual network calls and browser launches.
from backend.ingestion.scrapers.playwright_scraper import PlaywrightScraper

async def run_benchmark():
    scraper = PlaywrightScraper(api_key="TEST_KEY")

    # We want to call fetch_from_url 5 times concurrently.
    urls = [f"http://example.com/{i}" for i in range(5)]

    # Mock playwright
    mock_playwright = AsyncMock()
    mock_browser = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()

    mock_playwright.chromium.launch.return_value = mock_browser
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page

    # Let's make page.evaluate return some dummy text
    mock_page.evaluate.return_value = "dummy text " * 100

    # Mock genai client
    # First we need to handle the import and instantiation
    with patch("backend.ingestion.scrapers.playwright_scraper.async_playwright", return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_playwright))), \
         patch("backend.ingestion.scrapers.playwright_scraper.genai.Client") as MockClient:

        # Simulate blocking generation
        def mock_generate_content(*args, **kwargs):
            time.sleep(1) # Block for 1 second
            mock_response = MagicMock()
            mock_response.text = '[{"title": "Test Car", "year": 2020}]'
            return mock_response

        async def mock_aio_generate_content(*args, **kwargs):
            await asyncio.sleep(1) # Non-blocking for 1 second
            mock_response = MagicMock()
            mock_response.text = '[{"title": "Test Car", "year": 2020}]'
            return mock_response

        instance = MockClient.return_value
        instance.models.generate_content.side_effect = mock_generate_content

        # Also mock aio in case we use it
        instance.aio = AsyncMock()
        instance.aio.models.generate_content.side_effect = mock_aio_generate_content

        start_time = time.time()

        # Run concurrently
        tasks = [scraper.fetch_from_url(url) for url in urls]
        await asyncio.gather(*tasks)

        end_time = time.time()

        print(f"Total time taken: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
