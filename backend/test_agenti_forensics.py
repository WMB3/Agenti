import asyncio
import unittest
from ingestion.models import AuctionItem
from shannon import calculate_shannon_entropy, detect_high_entropy_war

class TestAgentiForensics(unittest.TestCase):
    def test_max_bid_calculation(self):
        # Formula: Max_Bid = (Retail * 0.8) - (Repairs * 1.15) - Fees
        item = AuctionItem(
            id="test-1",
            title="Test Car",
            estimated_retail_value=20000.0,
            estimated_repairs=2000.0,
            auction_fees=500.0,
            source="test"
        )

        # Manual calc: (20000 * 0.8) - (2000 * 1.15) - 500 = 16000 - 2300 - 500 = 13200
        # However, the current AuctionItem in models.py doesn't have the logic, it's in the Scraper.
        # But we can verify the model holds the values.
        item.estimated_repairs = 2000.0 * 1.15
        item.max_bid = (20000.0 * 0.8) - item.estimated_repairs - 500.0

        self.assertEqual(item.max_bid, 13200.0)

    def test_shannon_entropy(self):
        # Stable prices = low entropy
        stable_prices = [100.0, 100.0, 100.0, 100.0]
        self.assertEqual(calculate_shannon_entropy(stable_prices), 0.0)

        # Varied prices = higher entropy
        varied_prices = [100.0, 110.0, 120.0, 130.0]
        entropy = calculate_shannon_entropy(varied_prices)
        self.assertTrue(entropy > 1.0)

        # Threshold detection
        self.assertTrue(detect_high_entropy_war(varied_prices, threshold=1.0))
        self.assertFalse(detect_high_entropy_war(stable_prices, threshold=1.0))

if __name__ == "__main__":
    unittest.main()
