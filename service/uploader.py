# service/uploader.py (Backward Compatibility Wrapper)
from api.telegram_client import TelegramClient
from config.manager import ConfigManager

def send_image(image_path):
    """Legacy wrapper delegating Telegram photo upload to api/telegram_client.py."""
    mgr = ConfigManager()
    client = TelegramClient(mgr.config.telegram.bot_token, mgr.config.telegram.chat_id)
    client.send_photo(image_path, caption="🚨 Failed login detected on Windows device")
