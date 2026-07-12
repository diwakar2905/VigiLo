# config/saver.py
import json
import os
import tempfile
import hashlib
from config.exceptions import SaverError
from config.defaults import CURRENT_CONFIG_VERSION
from config.backup import ConfigBackupManager
from security.crypt import encrypt_data
from logs.logger import logger

class ConfigSaver:
    @staticmethod
    def save(config_path, app_config):
        """Creates backup, encrypts credentials, serializes data, writes config atomically, and updates SHA256 meta."""
        backup_mgr = ConfigBackupManager(config_path)
        
        # 1. Automatic backup before save
        if os.path.exists(config_path):
            backup_mgr.create_backup()
            
        try:
            # 2. Convert configuration to dict
            data = app_config.to_dict()
            data["version"] = CURRENT_CONFIG_VERSION
            
            # 3. Encrypt credentials via DPAPI
            data["telegram"]["bot_token"] = encrypt_data(app_config.telegram.bot_token)
            data["telegram"]["chat_id"] = encrypt_data(app_config.telegram.chat_id)
            
            # 4. Perform atomic write
            dir_name = os.path.dirname(os.path.abspath(config_path))
            if not os.path.exists(dir_name):
                os.makedirs(dir_name, exist_ok=True)
                
            with tempfile.NamedTemporaryFile("w", dir=dir_name, suffix=".tmp", delete=False, encoding="utf-8") as tf:
                json.dump(data, tf, indent=4)
                tf.flush()
                os.fsync(tf.fileno())
                temp_name = tf.name
                
            os.replace(temp_name, config_path)
            
            # 5. Generate and write the new integrity metadata file
            h = hashlib.sha256()
            with open(config_path, 'rb') as f:
                while chunk := f.read(8192):
                    h.update(chunk)
            file_hash = h.hexdigest()
            
            meta_path = f"{config_path}.meta"
            meta_data = {
                "version": CURRENT_CONFIG_VERSION,
                "sha256": file_hash,
                "timestamp": os.path.getmtime(config_path)
            }
            
            with open(meta_path, "w", encoding="utf-8") as mf:
                json.dump(meta_data, mf, indent=4)

            return True
        except Exception as e:
            if 'temp_name' in locals() and os.path.exists(temp_name):
                try:
                    os.remove(temp_name)
                except Exception:
                    pass
            raise SaverError(f"Failed to save configuration: {e}")
