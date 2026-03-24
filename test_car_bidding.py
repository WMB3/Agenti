import asyncio
from unittest.mock import AsyncMock, MagicMock
from car_bidding_analytical_agent import analyze_bids, live_log_console

def test_analyze_bids_empty_price_text():
    # Setup mock items
    item_mock = MagicMock()

    # Setup locator('.item-title a').inner_text()
    title_locator_mock = AsyncMock()
    title_locator_mock.inner_text.return_value = "Toyota Camry 2020"

    # Setup locator('.detail-item.price span').inner_text()
    price_locator_mock = AsyncMock()
    # Simulate empty price text that was causing issues
    price_locator_mock.inner_text.return_value = "Contact for price"

    def locator_side_effect(selector):
        if selector == '.item-title a':
            return title_locator_mock
        elif selector == '.detail-item.price span':
            return price_locator_mock
        return AsyncMock()

    item_mock.locator.side_effect = locator_side_effect

    items = [item_mock]

    # Run the function
    asyncio.run(analyze_bids(items, "Toyota", 5000))

    # Since current_bid should default to 0 and 0 < 5000,
    # it should not print any safety stop logs.
    print("Test passed without exceptions!")

test_analyze_bids_empty_price_text()
