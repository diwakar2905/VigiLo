import requests
from datetime import datetime
from .i_notification_provider import INotificationProvider
from .notification_message import NotificationMessage
from ...models.health_object import HealthObject, HealthStatus

class WebhookNotificationProvider(INotificationProvider):
    def __init__(self, webhook_url: str, priority_level: int = 2):
        self.webhook_url = webhook_url
        self._priority = priority_level

    @property
    def provider_id(self) -> str:
        return "webhook"

    @property
    def priority(self) -> int:
        return self._priority

    def send(self, message: NotificationMessage) -> bool:
        if not self.webhook_url:
            return False

        try:
            payload = {
                "title": message.title,
                "body": message.body,
                "severity": message.severity,
                "timestamp": message.timestamp,
                "metadata": message.metadata
            }
            resp = requests.post(self.webhook_url, json=payload, timeout=10)
            return resp.status_code in [200, 201, 202, 204]
        except Exception as e:
            print(f"[ERROR] WebhookNotificationProvider failure: {e}")
            return False

    def check_health(self) -> HealthObject:
        is_configured = bool(self.webhook_url)
        status = HealthStatus.HEALTHY if is_configured else HealthStatus.DEGRADED
        msg = "Webhook URL Endpoint active" if is_configured else "Unconfigured Webhook URL"
        return HealthObject(
            component_name="NotificationProvider:Webhook",
            status=status,
            message=msg,
            last_check=datetime.utcnow().isoformat()
        )
