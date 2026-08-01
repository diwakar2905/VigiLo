from abc import ABC, abstractmethod
from .notification_message import NotificationMessage
from ...models.health_object import HealthObject

class INotificationProvider(ABC):
    """Interface for all notification delivery providers (Telegram, Webhook, Email, Discord)."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        pass

    @property
    @abstractmethod
    def priority(self) -> int:
        pass

    @abstractmethod
    def send(self, message: NotificationMessage) -> bool:
        pass

    @abstractmethod
    def check_health(self) -> HealthObject:
        pass
