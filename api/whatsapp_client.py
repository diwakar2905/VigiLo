# api/whatsapp_client.py
"""WhatsApp Business API client implementing NotificationInterface."""

from __future__ import annotations
import os
import requests
import mimetypes
from logs.logger import logger
from api.notification_interface import NotificationInterface


class WhatsAppClient(NotificationInterface):
    """Client for sending text and media alerts via WhatsApp Business Cloud API.

    Parameters
    ----------
    phone_number_id:
        The WhatsApp Business Sender Phone Number ID.
    access_token:
        The Facebook Graph API access token (Bearer).
    recipient_phone:
        The destination phone number (with country code, e.g. '15550199999').
    """

    def __init__(
        self, phone_number_id: str, access_token: str, recipient_phone: str
    ) -> None:
        self.phone_number_id = str(phone_number_id).strip()
        self.access_token = str(access_token).strip()
        self.recipient_phone = str(recipient_phone).strip()
        self.base_url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}"

    def _is_configured(self) -> bool:
        """Helper to check if client has valid credentials configured."""
        if (
            not self.phone_number_id
            or not self.access_token
            or not self.recipient_phone
            or "YOUR_PHONE_NUMBER_ID" in self.phone_number_id
            or "YOUR_ACCESS_TOKEN" in self.access_token
        ):
            return False
        return True

    def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
        """Sends a text message to the recipient's phone number."""
        if not self._is_configured():
            logger.warning(
                "WhatsApp credentials not fully configured. Skipping message upload."
            )
            return False

        url = f"{self.base_url}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": self.recipient_phone,
            "type": "text",
            "text": {"body": text},
        }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=15)
            if resp.status_code in (200, 201):
                return True
            logger.error(
                f"WhatsApp send_message failed: HTTP {resp.status_code} - {resp.text}"
            )
        except Exception as e:
            logger.error(f"WhatsApp send_message exception: {e}")
        return False

    def _upload_media(self, file_path: str, mime_type: str) -> str | None:
        """Uploads a local media file to Facebook Graph and returns its media ID."""
        if not os.path.exists(file_path):
            logger.error(f"WhatsApp: Media file does not exist: {file_path}")
            return None

        url = f"{self.base_url}/media"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
        }
        data = {
            "messaging_product": "whatsapp",
        }

        try:
            with open(file_path, "rb") as f:
                files = {
                    "file": (os.path.basename(file_path), f, mime_type),
                }
                resp = requests.post(
                    url, headers=headers, data=data, files=files, timeout=45
                )
                if resp.status_code in (200, 201):
                    return resp.json().get("id")
                logger.error(
                    f"WhatsApp media upload failed: HTTP {resp.status_code} - {resp.text}"
                )
        except Exception as e:
            logger.error(f"WhatsApp media upload exception: {e}")
        return None

    def _send_media_message(
        self, media_type: str, media_id: str, caption: str | None = None
    ) -> bool:
        """Sends a message referencing an uploaded media ID."""
        url = f"{self.base_url}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        media_payload: dict = {"id": media_id}
        if caption and media_type in ("image", "document"):
            media_payload["caption"] = caption

        payload = {
            "messaging_product": "whatsapp",
            "to": self.recipient_phone,
            "type": media_type,
            media_type: media_payload,
        }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=20)
            if resp.status_code in (200, 201):
                return True
            logger.error(
                f"WhatsApp send media message failed: HTTP {resp.status_code} - {resp.text}"
            )
        except Exception as e:
            logger.error(f"WhatsApp send media message exception: {e}")
        return False

    def send_photo(self, image_path: str, caption: str | None = None) -> bool:
        """Uploads and sends a photo alert."""
        if not self._is_configured():
            logger.warning(
                "WhatsApp credentials not configured. Skipping photo upload."
            )
            return False

        mime_type, _ = mimetypes.guess_type(image_path)
        if not mime_type:
            mime_type = "image/jpeg"

        media_id = self._upload_media(image_path, mime_type)
        if media_id:
            return self._send_media_message("image", media_id, caption)
        return False

    def send_audio(self, audio_path: str, caption: str | None = None) -> bool:
        """Uploads and sends an audio recording alert."""
        if not self._is_configured():
            logger.warning(
                "WhatsApp credentials not configured. Skipping audio upload."
            )
            return False

        mime_type, _ = mimetypes.guess_type(audio_path)
        if not mime_type:
            mime_type = "audio/mpeg"

        media_id = self._upload_media(audio_path, mime_type)
        if media_id:
            # WhatsApp doesn't support caption inside the audio payload, so we send it as a subsequent text message if set
            success = self._send_media_message("audio", media_id)
            if success and caption:
                self.send_message(caption)
            return success
        return False

    def send_document(self, doc_path: str, caption: str | None = None) -> bool:
        """Uploads and sends a document alert (e.g. PDF report)."""
        if not self._is_configured():
            logger.warning(
                "WhatsApp credentials not configured. Skipping document upload."
            )
            return False

        mime_type, _ = mimetypes.guess_type(doc_path)
        if not mime_type:
            mime_type = "application/pdf"

        media_id = self._upload_media(doc_path, mime_type)
        if media_id:
            return self._send_media_message("document", media_id, caption)
        return False
