import csv
from typing import List
from ..base import FileSource
from ..models import AuctionItem

class CSVImporter(FileSource):
    @property
    def source_name(self) -> str:
        return "csv_file"

    async def fetch_items(self) -> List[AuctionItem]:
        # Implementation of the abstract method from BaseSource
        # This can be used if we have a default CSV file or if we want to call fetch_from_file
        raise NotImplementedError("Use fetch_from_file with a path.")

    async def fetch_from_file(self, file_path: str) -> List[AuctionItem]:
        items = []
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Normalize mapping from CSV to AuctionItem
                item = AuctionItem(
                    id=row.get('id', row.get('Lot Number', 'Unknown')),
                    title=row.get('title', row.get('Vehicle Title', 'Untitled Item')),
                    make=row.get('make'),
                    model=row.get('model'),
                    year=int(row.get('year', 0)) if row.get('year') else 0,
                    mileage=row.get('mileage', '0'),
                    damage=row.get('damage', 'None'),
                    current_bid=float(row.get('current_bid', row.get('Bid', 0))),
                    currency=row.get('currency', 'USD'),
                    lot_number=row.get('lot_number', row.get('Lot', '0')),
                    image_url=row.get('image_url', "https://images.unsplash.com/photo-1552519507-da3b142c6e3d?w=600"),
                    source=f"{self.source_name}:{file_path}",
                    raw_data=row
                )
                items.append(item)
        return items
