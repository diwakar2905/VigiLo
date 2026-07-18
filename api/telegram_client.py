from __future__ import annotations
import requests
from logs.logger import logger
from api.notification_interface import NotificationInterface


class TelegramClient(NotificationInterface):
    def __init__(self, bot_token, chat_id):
        self.bot_token = bot_token
        self.chat_id = str(chat_id)
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_message(self, text, parse_mode="Markdown"):
        """Sends a text message to Telegram. Returns True if successful, False otherwise."""
        if not self.bot_token or not self.chat_id or "YOUR_BOT_TOKEN" in self.bot_token:
            logger.warning(
                "Telegram credentials not configured. Skipping message upload."
            )
            return False

        url = f"{self.base_url}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": text, "parse_mode": parse_mode}
        try:
            resp = requests.post(url, json=payload, timeout=15)
            if resp.status_code == 200:
                return True
            logger.error(
                f"Telegram send_message failed: HTTP {resp.status_code} - {resp.text}"
            )
        except Exception as e:
            logger.error(f"Telegram send_message exception: {e}")
        return False

    def send_photo(self, image_path, caption=None):
        """Sends a photo to Telegram. Returns True if successful, False otherwise."""
        if not self.bot_token or not self.chat_id or "YOUR_BOT_TOKEN" in self.bot_token:
            logger.warning(
                "Telegram credentials not configured. Skipping photo upload."
            )
            return False

        url = f"{self.base_url}/sendPhoto"
        try:
            with open(image_path, "rb") as img:
                files = {"photo": img}
                data = {"chat_id": self.chat_id}
                if caption:
                    data["caption"] = caption
                resp = requests.post(url, data=data, files=files, timeout=30)
                if resp.status_code == 200:
                    return True
                logger.error(
                    f"Telegram send_photo failed: HTTP {resp.status_code} - {resp.text}"
                )
        except Exception as e:
            logger.error(f"Telegram send_photo exception: {e}")
        return False

    def send_audio(self, audio_path, caption=None):
        """Sends an audio file to Telegram. Returns True if successful, False otherwise."""
        if not self.bot_token or not self.chat_id or "YOUR_BOT_TOKEN" in self.bot_token:
            logger.warning(
                "Telegram credentials not configured. Skipping audio upload."
            )
            return False

        url = f"{self.base_url}/sendAudio"
        try:
            with open(audio_path, "rb") as audio:
                files = {"audio": audio}
                data = {"chat_id": self.chat_id}
                if caption:
                    data["caption"] = caption
                resp = requests.post(url, data=data, files=files, timeout=60)
                if resp.status_code == 200:
                    return True
                logger.error(
                    f"Telegram send_audio failed: HTTP {resp.status_code} - {resp.text}"
                )
        except Exception as e:
            logger.error(f"Telegram send_audio exception: {e}")
        return False

    def send_document(self, doc_path, caption=None):
        """Sends a document file to Telegram. Returns True if successful, False otherwise."""
        if not self.bot_token or not self.chat_id or "YOUR_BOT_TOKEN" in self.bot_token:
            logger.warning(
                "Telegram credentials not configured. Skipping document upload."
            )
            return False

        url = f"{self.base_url}/sendDocument"
        try:
            with open(doc_path, "rb") as doc:
                files = {"document": doc}
                data = {"chat_id": self.chat_id}
                if caption:
                    data["caption"] = caption
                resp = requests.post(url, data=data, files=files, timeout=60)
                if resp.status_code == 200:
                    return True
                logger.error(
                    f"Telegram send_document failed: HTTP {resp.status_code} - {resp.text}"
                )
        except Exception as e:
            logger.error(f"Telegram send_document exception: {e}")
        return False
