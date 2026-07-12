# config/manager.py
import os
import sys
from config.schema import AppConfig
from utils.system import get_config_path
from config.loader import ConfigLoader
from config.saver import ConfigSaver
from config.validator import ConfigValidator
from config.cache import ConfigCache
from config.exceptions import ConfigError
from logs.logger import logger

class ConfigManager:
    _cache = ConfigCache()

    def __init__(self, config_path=None):
        self.config_path = config_path if config_path else get_config_path()
        self.config = self.load()

    def load(self):
        """Loads configuration utilizing cache, migrations, env/cli precedence, and validation."""
        cached = self._cache.get()
        if cached:
            return cached
            
        try:
            cfg = ConfigLoader.load(self.config_path)
            
            # Resolve precedence: Env variables and Command line options override config file values
            cfg = self._resolve_precedence(cfg)
            
            # Run validator checks
            ConfigValidator.validate(cfg)
            
            # Freeze the configuration snapshot to make it immutable
            cfg.freeze()
            
            self._cache.set(cfg)
            return cfg
        except ConfigError as ce:
            logger.error(f"Configuration manager load warning: {ce}. Falling back to default settings.")
            default_cfg = AppConfig()
            default_cfg = self._resolve_precedence(default_cfg)
            default_cfg.freeze()
            self._cache.set(default_cfg)
            return default_cfg
        except Exception as e:
            logger.error(f"Unexpected configuration load error: {e}. Falling back to default settings.")
            default_cfg = AppConfig()
            default_cfg = self._resolve_precedence(default_cfg)
            default_cfg.freeze()
            self._cache.set(default_cfg)
            return default_cfg

    def save(self, app_config):
        """Validates configuration and writes it atomically to disk, invalidating cache."""
        try:
            # Validate before saving (we validate a mutable copy or before freezing)
            ConfigValidator.validate(app_config)
            ConfigSaver.save(self.config_path, app_config)
            
            # Clear cache and reload configuration to generate frozen immutable snapshot
            self._cache.clear()
            self.config = self.load()
            return True
        except ConfigError as ce:
            logger.error(f"Configuration manager save validation failed: {ce}")
            return False
        except Exception as e:
            logger.error(f"Unexpected configuration save error: {e}")
            return False

    def _resolve_precedence(self, config_obj):
        """Resolves precedence: Command Line > Environment Variables > Config File > Default Values."""
        tg = config_obj.telegram
        sec = config_obj.security
        cam = config_obj.camera
        
        # 1. Resolve environment variables
        if os.environ.get("VIGILO_BOT_TOKEN"):
            tg.bot_token = os.environ.get("VIGILO_BOT_TOKEN")
        if os.environ.get("VIGILO_CHAT_ID"):
            tg.chat_id = os.environ.get("VIGILO_CHAT_ID")
            
        if os.environ.get("VIGILO_FAILED_ATTEMPT_THRESHOLD"):
            try:
                sec.failed_attempt_threshold = int(os.environ.get("VIGILO_FAILED_ATTEMPT_THRESHOLD"))
            except ValueError:
                pass
        if os.environ.get("VIGILO_EVENT_ID"):
            try:
                sec.event_id = int(os.environ.get("VIGILO_EVENT_ID"))
            except ValueError:
                pass
        if os.environ.get("VIGILO_CHECK_INTERVAL_SECONDS"):
            try:
                sec.check_interval_seconds = float(os.environ.get("VIGILO_CHECK_INTERVAL_SECONDS"))
            except ValueError:
                pass
        if os.environ.get("VIGILO_DEVICE_INDEX"):
            try:
                cam.device_index = int(os.environ.get("VIGILO_DEVICE_INDEX"))
            except ValueError:
                pass

        # 2. Resolve Command line arguments
        args = sys.argv
        for i, arg in enumerate(args):
            if arg == "--bot-token" and i + 1 < len(args):
                tg.bot_token = args[i + 1]
            elif arg.startswith("--bot-token="):
                tg.bot_token = arg.split("=", 1)[1]
                
            if arg == "--chat-id" and i + 1 < len(args):
                tg.chat_id = args[i + 1]
            elif arg.startswith("--chat-id="):
                tg.chat_id = arg.split("=", 1)[1]

            if arg == "--failed-attempt-threshold" and i + 1 < len(args):
                try:
                    sec.failed_attempt_threshold = int(args[i + 1])
                except ValueError:
                    pass
            elif arg.startswith("--failed-attempt-threshold="):
                try:
                    sec.failed_attempt_threshold = int(arg.split("=", 1)[1])
                except ValueError:
                    pass

            if arg == "--event-id" and i + 1 < len(args):
                try:
                    sec.event_id = int(args[i + 1])
                except ValueError:
                    pass
            elif arg.startswith("--event-id="):
                try:
                    sec.event_id = int(arg.split("=", 1)[1])
                except ValueError:
                    pass

            if arg == "--check-interval-seconds" and i + 1 < len(args):
                try:
                    sec.check_interval_seconds = float(args[i + 1])
                except ValueError:
                    pass
            elif arg.startswith("--check-interval-seconds="):
                try:
                    sec.check_interval_seconds = float(arg.split("=", 1)[1])
                except ValueError:
                    pass

            if arg == "--device-index" and i + 1 < len(args):
                try:
                    cam.device_index = int(args[i + 1])
                except ValueError:
                    pass
            elif arg.startswith("--device-index="):
                try:
                    cam.device_index = int(arg.split("=", 1)[1])
                except ValueError:
                    pass
                    
        return config_obj
