import hmac
import hashlib
import json
import requests
from dataclasses import dataclass
from typing import Dict, List, Optional
from src.core.interfaces.i_service import IService
from src.core.events.event_bus import EventBus, VigiLoEvent

@dataclass
class WebhookSubscription:
    webhook_id: str
    target_url: str
    secret: str
    subscribed_events: List[str]

class WebhookEngine(IService):
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self._subscriptions: Dict[str, WebhookSubscription] = {}
        self._event_sub_id: Optional[str] = None
        self._initialized = False

    def initialize(self) -> bool:
        self._event_sub_id = self.event_bus.subscribe("*", self._on_event_published)
        self._initialized = True
        return True

    def shutdown(self) -> None:
        if self._event_sub_id:
            self.event_bus.unsubscribe("*", self._event_sub_id)
        self._subscriptions.clear()
        self._initialized = False

    def register_webhook(self, webhook_id: str, target_url: str, secret: str, subscribed_events: List[str]) -> None:
        self._subscriptions[webhook_id] = WebhookSubscription(
            webhook_id=webhook_id,
            target_url=target_url,
            secret=secret,
            subscribed_events=subscribed_events
        )

    def compute_hmac_signature(self, payload_bytes: bytes, secret: str) -> str:
        return hmac.new(secret.encode('utf-8'), payload_bytes, hashlib.sha256).hexdigest()

    def _on_event_published(self, event: VigiLoEvent) -> None:
        for sub in self._subscriptions.values():
            if "*" in sub.subscribed_events or event.event_type in sub.subscribed_events:
                self.dispatch_to_subscriber(sub, event)

    def dispatch_to_subscriber(self, sub: WebhookSubscription, event: VigiLoEvent) -> bool:
        payload = {
            "event_id": event.event_id,
            "event_type": event.event_type,
            "timestamp": event.timestamp,
            "data": event.data
        }
        raw_json = json.dumps(payload, sort_keys=True).encode('utf-8')
        signature = self.compute_hmac_signature(raw_json, sub.secret)

        headers = {
            "Content-Type": "application/json",
            "X-VigiLo-Signature": f"sha256={signature}",
            "X-VigiLo-Event": event.event_type
        }

        try:
            resp = requests.post(sub.target_url, data=raw_json, headers=headers, timeout=10)
            return resp.status_code in [200, 201, 202, 204]
        except Exception as e:
            print(f"[ERROR] WebhookEngine dispatch failed for '{sub.webhook_id}': {e}")
            return False
