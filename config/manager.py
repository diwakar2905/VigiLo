# config/manager.py
import json
import os
from config.schema import AppConfig, TelegramConfig, SecurityConfig, CameraConfig
from utils.system import get_config_path
from security.crypt import encrypt_data, decrypt_data

class ConfigManager:
    def __init__(self, config_path=None):
        self.config_path = config_path if config_path else get_config_path()
        self.config = self.load()

    def load(self):
        """Loads config.json from disk, decrypting sensitive credentials using DPAPI if encrypted."""
        if not os.path.exists(self.config_path):
            return AppConfig()
        
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            tg_data = data.get("telegram", {})
            sec_data = data.get("security", {})
            cam_data = data.get("camera", {})

            # Decrypt sensitive credentials using DPAPI (falls back to plaintext if not encrypted)
            token = decrypt_data(tg_data.get("bot_token", "YOUR_BOT_TOKEN"))
            chat_id = decrypt_data(tg_data.get("chat_id", "YOUR_CHAT_ID"))

            telegram = TelegramConfig(
                bot_token=token,
                chat_id=chat_id
            )
            
            security = SecurityConfig(
                failed_attempt_threshold=sec_data.get("failed_attempt_threshold", 2),
                event_id=sec_data.get("event_id", 4625),
                check_interval_seconds=sec_data.get("check_interval_seconds", 0.1)
            )
            
            camera = CameraConfig(
                device_index=cam_data.get("device_index", 0)
            )

            return AppConfig(telegram=telegram, security=security, camera=camera)
        except Exception as e:
            print(f"[ERROR] Failed to load config: {e}. Using defaults.")
            return AppConfig()

    def save(self, app_config):
        """Encrypts sensitive credentials via DPAPI and saves configuration to config.json."""
        try:
            data = app_config.to_dict()
            
            # Encrypt credentials before writing to disk
            data["telegram"]["bot_token"] = encrypt_data(app_config.telegram.bot_token)
            data["telegram"]["chat_id"] = encrypt_data(app_config.telegram.chat_id)
            
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            self.config = app_config
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save config: {e}")
            return False
