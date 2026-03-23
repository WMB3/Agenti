import aiohttp
from typing import List
from ..base import ApiSource
from ..models import AuctionItem

class RestApiSource(ApiSource):
    @property
    def source_name(self) -> str:
        return "rest_api"

    async def fetch_items(self) -> List[AuctionItem]:
        raise NotImplementedError("Use fetch_from_api with an endpoint.")

    async def fetch_from_api(self, endpoint: str, **params) -> List[AuctionItem]:
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint, params=params) as response:
                if response.status != 200:
                    raise Exception(f"API request failed with status {response.status}")
                
                data = await response.json()
                
                # Assume 'data' is a list of objects or contains a list
                if isinstance(data, dict):
                    # Try to find a list in common keys
                    for key in ['items', 'results', 'data']:
                        if key in data and isinstance(data[key], list):
                            data = data[key]
                            break
                
                if not isinstance(data, list):
                    raise ValueError("API did not return a list of items.")
                
                items = []
                for entry in data:
                    item = AuctionItem(
                        id=str(entry.get('id', 'Unknown')),
                        title=entry.get('title', entry.get('name', 'Untitled')),
                        make=entry.get('make'),
                        model=entry.get('model'),
                        year=int(entry.get('year', 0)),
                        mileage=str(entry.get('mileage', '0')),
                        damage=entry.get('damage', 'None'),
                        current_bid=float(entry.get('current_bid', entry.get('price', 0))),
                        currency=entry.get('currency', 'USD'),
                        lot_number=str(entry.get('lot_number', '0')),
                        image_url=entry.get('image_url', "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=600"),
                        source=f"api:{endpoint}",
                        raw_data=entry
                    )
                    items.append(item)
                return items
