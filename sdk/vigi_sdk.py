from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class PluginManifest:
    plugin_id: str
    name: str
    version: str
    author: str
    description: str
    required_permissions: List[str]  # e.g., ["read_timeline", "dispatch_notification"]
    trust_level: str = "COMMUNITY"   # OFFICIAL, TRUSTED, COMMUNITY
    min_platform_version: str = "3.5.0"
    signature: Optional[str] = None

class IVigiLoSDKFacade(ABC):
    """Facade interface exposed to third-party plugins. Hides all core internals."""

    @abstractmethod
    def get_platform_version(self) -> str: pass

    @abstractmethod
    def get_device_state(self) -> str: pass

    @abstractmethod
    def get_timeline_events(self, limit: int = 50) -> List[Dict[str, Any]]: pass

    @abstractmethod
    def record_incident(self, event_type: str, severity: str, description: str) -> bool: pass

    @abstractmethod
    def send_notification(self, title: str, body: str, severity: str = "INFO") -> bool: pass

class IVigiLoPlugin(ABC):
    """Base class for all VigiLo extensions."""

    @property
    @abstractmethod
    def manifest(self) -> PluginManifest:
        pass

    @abstractmethod
    def on_load(self, sdk: IVigiLoSDKFacade) -> bool:
        pass

    @abstractmethod
    def on_unload(self) -> None:
        pass
