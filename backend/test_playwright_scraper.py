import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from ingestion.scrapers.playwright_scraper import PlaywrightScraper
from ingestion.models import AuctionItem

@pytest.fixture
def mock_genai_response():
    return """
    [
        {
            "id": "lot123",
            "title": "2020 Toyota Camry",
            "year": 2020,
            "mileage": "45000",
            "damage": "Front End",
            "current_bid": 5000,
            "currency": "OMR",
            "lot_number": "lot123",
            "image_url": "http://example.com/image.jpg",
            "estimated_retail_value": 15000,
            "estimated_repairs": 3000,
            "auction_fees": 200
        }
    ]
    """

@pytest.mark.asyncio
async def test_scraper_missing_api_key():
    # Force api_key to be None even if the environment variable is set
    with patch("os.getenv", return_value=None):
        scraper = PlaywrightScraper(api_key=None)
        # Should raise an exception because GEMINI_API_KEY is not set
        with pytest.raises(Exception, match="GEMINI_API_KEY is not set."):
            await scraper.fetch_from_url("http://example.com")


@pytest.mark.asyncio
@patch("ingestion.scrapers.playwright_scraper.genai.Client")
@patch("ingestion.scrapers.playwright_scraper.async_playwright")
async def test_scraper_success(mock_async_playwright, mock_genai_client, mock_genai_response):
    # Mocking async_playwright
    mock_browser = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()

    # The setup of async_playwright context manager
    mock_p_instance = AsyncMock()
    mock_p_instance.chromium.launch = AsyncMock(return_value=mock_browser)
    mock_async_playwright.return_value.__aenter__.return_value = mock_p_instance

    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_context.new_page = AsyncMock(return_value=mock_page)

    mock_page.evaluate = AsyncMock(return_value="Some big text to scrape that represents the whole document page " * 100)

    # Mocking genai Client
    mock_client_instance = MagicMock()
    mock_genai_client.return_value = mock_client_instance
    mock_response = MagicMock()
    mock_response.text = mock_genai_response
    mock_client_instance.models.generate_content.return_value = mock_response

    # Injecting fake API key so it passes the key check
    scraper = PlaywrightScraper(api_key="fake-api-key")

    items = await scraper.fetch_from_url("https://opensooq.com/fake-car")

    assert len(items) == 1
    item = items[0]
    assert isinstance(item, AuctionItem)
    assert item.id == "lot123"
    assert item.title == "2020 Toyota Camry"
    assert item.year == 2020
    assert item.current_bid == 5000.0
    assert item.estimated_retail_value == 15000.0
    assert pytest.approx(item.estimated_repairs, 0.01) == 3450.0  # 3000 * 1.15
    assert item.auction_fees == 200.0
    assert pytest.approx(item.max_bid, 0.01) == 8350.0  # (15000 * 0.8) - 3450 - 200
    assert round(item.roi_percentage, 2) == 73.41  # ((15000 - (5000 + 3450 + 200)) / (5000 + 3450 + 200)) * 100 = (6350 / 8650) * 100 = 73.41

    # Verify that playwright was closed
    mock_browser.close.assert_called_once()
