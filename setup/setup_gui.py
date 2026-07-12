# setup/setup_gui.py (Backward Compatibility Wrapper)
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.manager import ConfigManager
from config.schema import TelegramConfig

def setup_telegram():
    print("=== Anti-Theft Telegram Setup (Legacy Wrapper) ===")
    bot_token = input("Enter your Telegram Bot Token: ").strip()
    chat_id = input("Enter your Telegram Chat ID: ").strip()

    mgr = ConfigManager()
    mgr.config.telegram = TelegramConfig(bot_token=bot_token, chat_id=chat_id)
    if mgr.save(mgr.config):
        print("[✓] Telegram configuration saved.")
    else:
        print("[X] Failed to save configuration.")

if __name__ == "__main__":
    setup_telegram()
