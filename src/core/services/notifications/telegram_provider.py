import os
import requests
from datetime import datetime
from .i_notification_provider import INotificationProvider
from .notification_message import NotificationMessage
from ...models.health_object import HealthObject, HealthStatus

class TelegramNotificationProvider(INotificationProvider):
    def __init__(self, bot_token: str, chat_id: str, priority_level: int = 1):
        self.bot_token = bot_token
        self.chat_id = str(chat_id)
        self._priority = priority_level

    @property
    def provider_id(self) -> str:
        return "telegram"

    @property
    def priority(self) -> int:
        return self._priority

    def send(self, message: NotificationMessage) -> bool:
        if not self.bot_token or not self.chat_id:
            return False

        try:
            if message.attachment_path and os.path.exists(message.attachment_path):
                url = f"https://api.telegram.org/bot{self.bot_token}/sendPhoto"
                caption = f"🚨 *{message.title}*\n{message.body}"
                with open(message.attachment_path, "rb") as f:
                    resp = requests.post(
                        url,
                        data={"chat_id": self.chat_id, "caption": caption, "parse_mode": "Markdown"},
                        files={"photo": f},
                        timeout=15
                    )
                    return resp.status_code == 200
            else:
                url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                text = f"🛡️ *{message.title}*\n{message.body}"
                resp = requests.post(
                    url,
                    json={"chat_id": self.chat_id, "text": text, "parse_mode": "Markdown"},
                    timeout=10
                )
                return resp.status_code == 200
        except Exception as e:
            print(f"[ERROR] TelegramNotificationProvider failure: {e}")
            return False

    def check_health(self) -> HealthObject:
        is_configured = bool(self.bot_token and self.chat_id)
        status = HealthStatus.HEALTHY if is_configured else HealthStatus.DEGRADED
        msg = "Telegram Bot Token & Chat ID active" if is_configured else "Unconfigured Token/Chat ID"
        
        return HealthObject(
            component_name="NotificationProvider:Telegram",
            status=status,
            message=msg,
            last_check=datetime.utcnow().isoformat()
        )
