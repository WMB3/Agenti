import math
from typing import List

def calculate_shannon_entropy(bid_prices: List[float]) -> float:
    """
    Shannon Entropy calculation to measure bidding war intensity.
    Measures the uncertainty/information density of bid prices.
    """
    if not bid_prices:
        return 0.0

    # Calculate price change probabilities
    price_counts = {}
    for price in bid_prices:
        price_counts[price] = price_counts.get(price, 0) + 1

    total_bids = len(bid_prices)
    entropy = 0.0
    for count in price_counts.values():
        p = count / total_bids
        entropy -= p * math.log2(p)

    return entropy

def detect_high_entropy_war(bid_prices: List[float], threshold: float = 1.5) -> bool:
    """Returns True if the bidding war intensity (entropy) exceeds the threshold."""
    return calculate_shannon_entropy(bid_prices) > threshold
