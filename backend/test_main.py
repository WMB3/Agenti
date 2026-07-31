import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from main import app, scraper

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "online", "system": "NEXUS Omni"}

@patch.object(scraper, 'fetch_from_url', new_callable=AsyncMock)
def test_handle_intercept_gemini_api_error(mock_fetch_from_url):
    # Setup mock to raise an exception
    mock_fetch_from_url.side_effect = Exception("Mock Gemini API Error")

    # Make the request
    payload = {"url": "https://example.com/mock-listing"}
    response = client.post("/api/v1/intercept", json=payload)

    # Verify response
    assert response.status_code == 500
    assert "Ghost-Intercept failed: Mock Gemini API Error" in response.json()["detail"]
    mock_fetch_from_url.assert_called_once_with("https://example.com/mock-listing")

@patch.object(scraper, 'fetch_from_url', new_callable=AsyncMock)
def test_handle_batch_intercept_gemini_api_error(mock_fetch_from_url):
    # Setup mock to raise an exception
    mock_fetch_from_url.side_effect = Exception("Mock Gemini API Error")

    # Make the request
    payloads = [{"url": "https://example.com/mock-listing1"}, {"url": "https://example.com/mock-listing2"}]
    response = client.post("/api/v1/batch_intercept", json=payloads)

    # Verify response
    assert response.status_code == 200
    assert response.json() == [[], []]
    assert mock_fetch_from_url.call_count == 2
