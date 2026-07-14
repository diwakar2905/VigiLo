# service/commander.py (Backward Compatibility Wrapper)
import sys
import os
import threading
from logs.logger import logger

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.telegram_polling import TelegramPollingService
from api.telegram_client import TelegramClient
from config.manager import ConfigManager

_polling_service = None
_stop_event = threading.Event()

def init_commander(config_dict, captures_dir):
    """Legacy initializer that maps parameters to the new TelegramPollingService."""
    global _polling_service
    mgr = ConfigManager()
    
    # Override credentials if explicitly passed via config_dict
    if config_dict and 'telegram' in config_dict:
        mgr.config.telegram.bot_token = config_dict['telegram'].get('bot_token', mgr.config.telegram.bot_token)
        mgr.config.telegram.chat_id = config_dict['telegram'].get('chat_id', mgr.config.telegram.chat_id)
        
    client = TelegramClient(mgr.config.telegram.bot_token, mgr.config.telegram.chat_id)
    _polling_service = TelegramPollingService(
        telegram_client=client,
        app_config=mgr.config,
        captures_dir=captures_dir
    )
    logger.info("Legacy Commander initialized and mapped to modern services.")

def start_commander_loop():
    """Legacy loop launcher starting the polling service."""
    if _polling_service:
        _polling_service.start(_stop_event)
    else:
        logger.error("Legacy Commander: start_commander_loop called before init_commander.")
