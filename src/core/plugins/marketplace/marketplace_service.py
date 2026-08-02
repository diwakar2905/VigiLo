from dataclasses import dataclass, field
from typing import List, Dict, Optional
from src.core.interfaces.i_service import IService
from sdk.vigi_sdk import PluginManifest

@dataclass
class MarketplaceItem:
    manifest: PluginManifest
    download_url: str
    publisher_verified: bool
    rating: float
    downloads_count: int

class MarketplaceService(IService):
    def __init__(self):
        self._catalog: Dict[str, MarketplaceItem] = {}
        self._initialized = False

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def shutdown(self) -> None:
        self._catalog.clear()
        self._initialized = False

    def register_item(self, item: MarketplaceItem) -> None:
        self._catalog[item.manifest.plugin_id] = item

    def search_catalog(self, query: str = "") -> List[MarketplaceItem]:
        if not query:
            return list(self._catalog.values())
        q = query.lower()
        return [
            item for item in self._catalog.values()
            if q in item.manifest.name.lower() or q in item.manifest.description.lower()
        ]

    def verify_publisher_signature(self, item: MarketplaceItem) -> bool:
        return item.publisher_verified and bool(item.manifest.signature)
