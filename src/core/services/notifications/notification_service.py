import time
from typing import List, Dict
from ...interfaces.i_service import IService
from .i_notification_provider import INotificationProvider
from .notification_message import NotificationMessage
from ...models.health_object import HealthObject, HealthStatus

class NotificationService(IService):
    def __init__(self, max_retries: int = 3, backoff_factor: float = 1.5):
        self._providers: Dict[str, INotificationProvider] = {}
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self._initialized = False

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def shutdown(self) -> None:
        self._providers.clear()
        self._initialized = False

    def register_provider(self, provider: INotificationProvider) -> None:
        self._providers[provider.provider_id] = provider

    def unregister_provider(self, provider_id: str) -> None:
        if provider_id in self._providers:
            del self._providers[provider_id]

    def get_providers_sorted(self) -> List[INotificationProvider]:
        return sorted(self._providers.values(), key=lambda p: p.priority)

    def dispatch(self, message: NotificationMessage) -> bool:
        providers = self.get_providers_sorted()
        if not providers:
            print("[WARN] No notification providers registered.")
            return False

        for provider in providers:
            success = self._send_with_retry(provider, message)
            if success:
                return True
            print(f"[WARN] Provider '{provider.provider_id}' failed delivery. Degrading to fallback provider.")
        
        return False

    def _send_with_retry(self, provider: INotificationProvider, message: NotificationMessage) -> bool:
        delay = 0.5
        for attempt in range(1, self.max_retries + 1):
            if provider.send(message):
                return True
            if attempt < self.max_retries:
                time.sleep(delay)
                delay *= self.backoff_factor
        return False

    def check_all_providers_health(self) -> List[HealthObject]:
        return [p.check_health() for p in self._providers.values()]
