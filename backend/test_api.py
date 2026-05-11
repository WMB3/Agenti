import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from ingestion.models import AuctionItem
from unittest.mock import AsyncMock, patch

@pytest.fixture
def test_app():
    return app

@pytest.fixture
def dummy_item():
    return AuctionItem(
        id="test-1",
        title="Test Car",
        estimated_retail_value=20000.0,
        estimated_repairs=2000.0,
        auction_fees=500.0,
        source="test"
    )


@pytest.mark.asyncio
async def test_health_check(test_app):
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "online", "system": "NEXUS Omni"}

@pytest.mark.asyncio
@patch('main.scraper.fetch_from_url', new_callable=AsyncMock)
async def test_intercept_success(mock_fetch, test_app, dummy_item):
    mock_fetch.return_value = [dummy_item]

    payload = {"url": "https://example.com/car/123"}
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/intercept", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == "test-1"
    assert data[0]["title"] == "Test Car"
    mock_fetch.assert_called_once_with("https://example.com/car/123")

@pytest.mark.asyncio
async def test_intercept_missing_url(test_app):
    payload = {}
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/intercept", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "URL is required"

@pytest.mark.asyncio
@patch('main.scraper.fetch_from_url', new_callable=AsyncMock)
async def test_intercept_failure(mock_fetch, test_app):
    mock_fetch.side_effect = Exception("Failed to scrape")

    payload = {"url": "https://example.com/bad"}
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/intercept", json=payload)

    assert response.status_code == 500
    assert "Ghost-Intercept failed" in response.json()["detail"]

@pytest.mark.asyncio
@patch('main.scraper.fetch_from_url', new_callable=AsyncMock)
async def test_batch_intercept(mock_fetch, test_app, dummy_item):
    # Setup mock to return different things for different URLs
    # For simplicity, returning the same item, but we will test it returns a list of lists.
    mock_fetch.return_value = [dummy_item]

    payloads = [
        {"url": "https://example.com/car/1"},
        {"url": "https://example.com/car/2"}
    ]

    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/batch_intercept", json=payloads)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert isinstance(data[0], list)
    assert len(data[0]) == 1
    assert data[0][0]["id"] == "test-1"

    # Assert fetch_from_url was called twice
    assert mock_fetch.call_count == 2
    mock_fetch.assert_any_call("https://example.com/car/1")
    mock_fetch.assert_any_call("https://example.com/car/2")

@pytest.mark.asyncio
@patch('main.scraper.fetch_from_url', new_callable=AsyncMock)
async def test_batch_intercept_partial_failure(mock_fetch, test_app, dummy_item):
    # One succeeds, one fails
    async def side_effect(url):
        if url == "https://example.com/car/1":
            return [dummy_item]
        else:
            raise Exception("Failed")

    mock_fetch.side_effect = side_effect

    payloads = [
        {"url": "https://example.com/car/1"},
        {"url": "https://example.com/car/2"}
    ]

    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        response = await ac.post("/api/v1/batch_intercept", json=payloads)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2

    # First one succeeded
    assert isinstance(data[0], list)
    assert len(data[0]) == 1
    assert data[0][0]["id"] == "test-1"

    # Second one failed and returns empty list per logic in main.py
    assert data[1] == []

@pytest.mark.asyncio
@patch('main.gemini_client', None, create=True)
async def test_analyze_vehicle_gemini_not_configured(test_app):
    payload = {
        "make": "Toyota",
        "model": "Camry",
        "year": 2018,
        "mileage": 50000,
        "damage": "None"
    }
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        response = await ac.post("/api/analyze", json=payload)

    assert response.status_code == 500
    assert response.json()["detail"] == "Gemini client not configured."

@pytest.mark.asyncio
@patch('main.gemini_client', create=True)
async def test_analyze_vehicle_success(mock_gemini, test_app):
    # Mocking google-genai aio client to return a controlled CarEvaluation object
    class DummyCarEvaluation:
        def model_dump(self):
            return {
                "estimated_retail_value": 25000.0,
                "estimated_repairs": 1000.0,
                "confidence_score": 0.9,
                "notes": "Good condition"
            }

    mock_response = AsyncMock()
    mock_response.parsed = DummyCarEvaluation()
    mock_gemini.aio.models.generate_content = AsyncMock(return_value=mock_response)

    payload = {
        "make": "Honda",
        "model": "Civic",
        "year": 2020,
        "mileage": 30000,
        "damage": "Minor scratches"
    }
    async with AsyncClient(transport=ASGITransport(app=test_app), base_url="http://test") as ac:
        response = await ac.post("/api/analyze", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
