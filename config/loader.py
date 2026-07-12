# config/loader.py
import json
import os
import hashlib
from config.exceptions import LoaderError
from config.schema import AppConfig, TelegramConfig, SecurityConfig, CameraConfig
from config.migration import ConfigMigrator
from config.backup import ConfigBackupManager
from security.crypt import decrypt_data
from logs.logger import logger

class ConfigLoader:
    @staticmethod
    def load(config_path):
        """Loads configuration, validates integrity, rolls back to backups on corruption, and returns AppConfig."""
        backup_mgr = ConfigBackupManager(config_path)
        
        if not os.path.exists(config_path):
            # Attempt to restore from backup if file is missing but backups exist
            logger.warning(f"ConfigLoader: Active configuration missing at {config_path}. Checking backups...")
            if backup_mgr.restore_latest_valid_backup():
                logger.info("ConfigLoader: Restored configuration from backup successfully.")
            else:
                logger.info("ConfigLoader: No backup found. Instantiating default configuration.")
                return AppConfig()

        # 1. Integrity Verification Checks
        is_corrupted = False
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as je:
            logger.error(f"ConfigLoader: Active configuration file is corrupted (invalid JSON): {je}")
            is_corrupted = True

        if not is_corrupted:
            # Check SHA-256 hash against metadata file if it exists to detect unexpected modifications
            meta_path = f"{config_path}.meta"
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, "r", encoding="utf-8") as mf:
                        meta = json.load(mf)
                    expected_hash = meta.get("sha256", "")
                    
                    # Calculate actual hash
                    h = hashlib.sha256()
                    with open(config_path, 'rb') as f:
                        while chunk := f.read(8192):
                            h.update(chunk)
                    actual_hash = h.hexdigest()
                    
                    if actual_hash != expected_hash:
                        logger.error(f"ConfigLoader: Integrity violation detected! Expected: {expected_hash}, Actual: {actual_hash}")
                        # In enterprise scenarios, we attempt backup restoration or log warning.
                        # We will log it and try to restore from a backup.
                        is_corrupted = True
                except Exception as me:
                    logger.warning(f"ConfigLoader: Failed to verify config metadata: {me}")

        # 2. Trigger Restore on Corruption
        if is_corrupted:
            logger.warning("ConfigLoader: Attempting to restore configuration from backups...")
            if backup_mgr.restore_latest_valid_backup():
                # Re-load from restored file
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception as e:
                    raise LoaderError(f"Failed to load configuration after restoration: {e}")
            else:
                logger.critical("ConfigLoader: Active config is corrupted and no backups could be restored. Using defaults.")
                return AppConfig()

        try:
            # 3. Run migrations
            data = ConfigMigrator.migrate(data)
            
            tg_data = data.get("telegram", {})
            sec_data = data.get("security", {})
            cam_data = data.get("camera", {})
            
            # 4. Decrypt credentials using DPAPI
            raw_token = tg_data.get("bot_token", "YOUR_BOT_TOKEN")
            raw_chat_id = tg_data.get("chat_id", "YOUR_CHAT_ID")
            
            token = decrypt_data(raw_token)
            chat_id = decrypt_data(raw_chat_id)
            
            # 5. Construct schemas
            telegram = TelegramConfig(bot_token=token, chat_id=chat_id)
            security = SecurityConfig(
                failed_attempt_threshold=sec_data.get("failed_attempt_threshold", 2),
                event_id=sec_data.get("event_id", 4625),
                check_interval_seconds=sec_data.get("check_interval_seconds", 0.1)
            )
            camera = CameraConfig(device_index=cam_data.get("device_index", 0))
            
            return AppConfig(telegram=telegram, security=security, camera=camera)
        except Exception as e:
            raise LoaderError(f"Failed to parse configuration schema values: {e}")
