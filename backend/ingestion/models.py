from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Bid(BaseModel):
    bidder_id: str
    amount: float
    currency: str = "USD"
    timestamp: datetime = Field(default_factory=datetime.now)

class AuctionItem(BaseModel):
    id: str
    title: str
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    mileage: Optional[str] = "Unknown"
    damage: Optional[str] = "None"
    current_bid: float = 0.0
    currency: str = "USD"
    lot_number: str = "Unknown"
    image_url: str = "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=600"

    # Financial Forensics: Pioneer Mode
    estimated_retail_value: float = 0.0
    estimated_repairs: float = 0.0
    auction_fees: float = 0.0
    max_bid: float = 0.0
    roi_percentage: float = 0.0

    source: str
    raw_data: Optional[dict] = None
    bids: List[Bid] = []

class Signal(BaseModel):
    market_id: str
    outcome: str
    amount: float
    max_price: float
    confidence_score: float

class MarketResolution(BaseModel):
    market_id: str
    token_id: str
    outcome: str

class TradeStatus(BaseModel):
    status: str
    market: str
    action: str
    reasoning: str
