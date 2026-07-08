from pydantic import BaseModel
import pytest
from httpx import AsyncClient, ASGITransport
from main import app, CarEvaluation
from ingestion.models import AuctionItem
from unittest.mock import AsyncMock, patch, MagicMock

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

# ... [other tests]
