from typing import List, Dict, Type
from .base import BaseSource, FileSource, ScraperSource, ApiSource
from .models import AuctionItem

class IngestionManager:
    def __init__(self):
        self._sources: Dict[str, BaseSource] = {}

    def register_source(self, source: BaseSource):
        """Register a data source instance."""
        self._sources[source.source_name] = source

    def get_source(self, name: str) -> BaseSource:
        """Get a registered source by name."""
        if name not in self._sources:
            raise ValueError(f"Source '{name}' not registered.")
        return self._sources[name]

    async def fetch_from_all(self) -> List[AuctionItem]:
        """Fetch items from all registered sources."""
        all_items = []
        for source in self._sources.values():
            try:
                items = await source.fetch_items()
                all_items.extend(items)
            except NotImplementedError:
                # Some sources might require specific parameters like file_path or url
                continue
            except Exception as e:
                print(f"Error fetching from {source.source_name}: {e}")
        return all_items

    async def fetch_from_url(self, source_name: str, url: str) -> List[AuctionItem]:
        source = self.get_source(source_name)
        if isinstance(source, ScraperSource):
            return await source.fetch_from_url(url)
        raise TypeError(f"Source '{source_name}' does not support URL scraping.")

    async def fetch_from_file(self, source_name: str, file_path: str) -> List[AuctionItem]:
        source = self.get_source(source_name)
        if isinstance(source, FileSource):
            return await source.fetch_from_file(file_path)
        raise TypeError(f"Source '{source_name}' does not support file imports.")

    async def fetch_from_api(self, source_name: str, endpoint: str, **params) -> List[AuctionItem]:
        source = self.get_source(source_name)
        if isinstance(source, ApiSource):
            return await source.fetch_from_api(endpoint, **params)
        raise TypeError(f"Source '{source_name}' does not support API fetching.")
