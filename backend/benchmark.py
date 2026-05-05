import asyncio
import time
from unittest.mock import patch, MagicMock, AsyncMock
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from ingestion.scrapers.playwright_scraper import PlaywrightScraper

async def run_benchmark():
    scraper = PlaywrightScraper(api_key="dummy")

    with patch('ingestion.scrapers.playwright_scraper.async_playwright') as mock_pw:
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        mock_page.evaluate.return_value = "dummy text " * 300
        mock_context.new_page.return_value = mock_page

        mock_browser = AsyncMock()
        mock_browser.new_context.return_value = mock_context

        mock_p = AsyncMock()
        mock_p.chromium.launch.return_value = mock_browser

        mock_pw.return_value.__aenter__.return_value = mock_p

        with patch('ingestion.scrapers.playwright_scraper.genai.Client') as mock_genai_client_class:
            mock_client_instance = MagicMock()

            def sync_generate_content(*args, **kwargs):
                time.sleep(1)
                mock_response = MagicMock()
                mock_response.text = '[]'
                return mock_response

            mock_client_instance.models.generate_content.side_effect = sync_generate_content

            async def async_generate_content(*args, **kwargs):
                await asyncio.sleep(1)
                mock_response = MagicMock()
                mock_response.text = '[]'
                return mock_response

            mock_aio = AsyncMock()
            mock_aio.models.generate_content.side_effect = async_generate_content
            mock_client_instance.aio = mock_aio

            mock_genai_client_class.return_value = mock_client_instance

            with patch('ingestion.scrapers.playwright_scraper.asyncio.sleep', new_callable=AsyncMock):
                start = time.time()
                tasks = [scraper.fetch_from_url("http://example.com") for _ in range(5)]
                await asyncio.gather(*tasks)
                duration = time.time() - start
                print(f"Time taken for 5 concurrent calls: {duration:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
