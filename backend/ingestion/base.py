from abc import ABC, abstractmethod
from typing import List
from .models import AuctionItem

class BaseSource(ABC):
    @property
    @abstractmethod
    def source_name(self) -> str:
        """Unique identifier for this data source."""
        pass

    @abstractmethod
    async def fetch_items(self) -> List[AuctionItem]:
        """Fetch and normalize items from the source."""
        pass

class FileSource(BaseSource):
    @abstractmethod
    async def fetch_from_file(self, file_path: str) -> List[AuctionItem]:
        """Fetch and normalize items from a local file."""
        pass

class ScraperSource(BaseSource):
    @abstractmethod
    async def fetch_from_url(self, url: str) -> List[AuctionItem]:
        """Scrape and normalize items from a URL."""
        pass

class ApiSource(BaseSource):
    @abstractmethod
    async def fetch_from_api(self, endpoint: str, **params) -> List[AuctionItem]:
        """Fetch and normalize items from a REST/GraphQL API."""
        pass
