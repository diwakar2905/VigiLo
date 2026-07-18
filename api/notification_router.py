# api/notification_router.py
"""Composite Router for dispatching alerts to Telegram and WhatsApp."""

from __future__ import annotations
from api.notification_interface import NotificationInterface
from api.whatsapp_client import WhatsAppClient
from logs.logger import logger


class NotificationRouter(NotificationInterface):
    """Routes alerts to all active channels (Telegram and WhatsApp Business API)."""

    def __init__(self, config, telegram_client) -> None:
        self.config = config
        self.telegram = telegram_client

        # Initialize WhatsApp Client
        w_config = getattr(config, "whatsapp", None)
        if w_config:
            self.whatsapp = WhatsAppClient(
                phone_number_id=w_config.phone_number_id,
                access_token=w_config.access_token,
                recipient_phone=w_config.recipient_phone,
            )
        else:
            self.whatsapp = None

    def _whatsapp_enabled(self) -> bool:
        w_config = getattr(self.config, "whatsapp", None)
        if w_config and w_config.enabled:
            return True
        return False

    def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """Dispatches text messages to active channels."""
        tg_res = self.telegram.send_message(text, parse_mode)

        if self._whatsapp_enabled() and self.whatsapp:
            try:
                self.whatsapp.send_message(text, parse_mode)
            except Exception as e:
                logger.error(
                    f"NotificationRouter: Failed to send WhatsApp message: {e}"
                )

        return tg_res

    def send_photo(self, image_path: str, caption: str | None = None) -> bool:
        """Dispatches photo alerts to active channels."""
        tg_res = self.telegram.send_photo(image_path, caption)

        if self._whatsapp_enabled() and self.whatsapp:
            try:
                self.whatsapp.send_photo(image_path, caption)
            except Exception as e:
                logger.error(f"NotificationRouter: Failed to send WhatsApp photo: {e}")

        return tg_res

    def send_audio(self, audio_path: str, caption: str | None = None) -> bool:
        """Dispatches audio alerts to active channels."""
        tg_res = self.telegram.send_audio(audio_path, caption)

        if self._whatsapp_enabled() and self.whatsapp:
            try:
                self.whatsapp.send_audio(audio_path, caption)
            except Exception as e:
                logger.error(f"NotificationRouter: Failed to send WhatsApp audio: {e}")

        return tg_res

    def send_document(self, doc_path: str, caption: str | None = None) -> bool:
        """Dispatches document/PDF files to active channels."""
        tg_res = self.telegram.send_document(doc_path, caption)

        if self._whatsapp_enabled() and self.whatsapp:
            try:
                self.whatsapp.send_document(doc_path, caption)
            except Exception as e:
                logger.error(
                    f"NotificationRouter: Failed to send WhatsApp document: {e}"
                )

        return tg_res
