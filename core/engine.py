# core/engine.py
import threading
import time
from api.telegram_client import TelegramClient
from config.manager import ConfigManager
from logs.logger import logger
from utils.system import get_captures_dir
from core.event_monitor import EventLogMonitor
from core.shutdown_listener import ShutdownListener
from services.upload_queue import UploadQueueService
from services.telegram_polling import TelegramPollingService
from modules.camera import CameraModule
from security.privilege import acquire_named_mutex

class VigiLoEngine:
    def __init__(self, config_path=None):
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.config
        self.captures_dir = get_captures_dir()
        
        # Instantiate Telegram Client
        self.telegram_client = TelegramClient(
            bot_token=self.config.telegram.bot_token,
            chat_id=self.config.telegram.chat_id
        )
        
        # Shutdown event for thread lifecycle management
        self.stop_event = threading.Event()
        self.last_capture_time = 0
        self.capture_cooldown = 0.0 # Delay between captures in seconds
        self._service_mutex = None
        self._commander_mutex = None

    def capture_alert(self):
        """Callback triggered when failed login attempt threshold is reached."""
        logger.warning("[ALERT] Wrong Password Threshold Reached! Triggering camera capture...")
        now = time.time()
        if now - self.last_capture_time >= self.capture_cooldown:
            try:
                camera = CameraModule(device_index=self.config.camera.device_index)
                # 'alert_' prefix ensures the upload queue service picks it up automatically
                filepath = camera.execute(self.captures_dir, prefix="alert_")
                if filepath:
                    logger.info(f"Intruder photo saved to offline queue: {filepath}")
                else:
                    logger.error("Camera capture failed to write photo.")
            except Exception as e:
                logger.error(f"Exception during alert camera capture: {e}")
            self.last_capture_time = now
        else:
            logger.info("Camera capture alert suppressed on cooldown.")

    def send_shutdown_alert(self):
        """Direct alert notification sent to Telegram when Windows is shutting down."""
        logger.warning("[SHUTDOWN] System shutdown detected. Alerting user...")
        # Direct synchronous upload since the system is shutting down immediately
        self.telegram_client.send_message("⚠️ System Shutdown Detected! VigiLo is stopping.")

    def run_service(self):
        """Starts the background event monitoring service (SYSTEM context)."""
        logger.info("=== VigiLo Running in SERVICE Mode ===")
        
        # 0. Single-Instance Mutex Guard
        self._service_mutex = acquire_named_mutex("Global\\VigiLoServiceMutex")
        if not self._service_mutex:
            logger.warning("[SYSTEM] VigiLo Service is already running! Exiting duplicate process.")
            return

        # 1. Start Event Log Monitor
        self.event_monitor = EventLogMonitor(
            event_id=self.config.security.event_id,
            threshold=self.config.security.failed_attempt_threshold,
            check_interval=self.config.security.check_interval_seconds,
            callback=self.capture_alert
        )
        
        monitor_thread = threading.Thread(
            target=self.event_monitor.start,
            args=(self.stop_event,),
            name="EventLogMonitorThread",
            daemon=True
        )
        monitor_thread.start()

        # 2. Start Upload Queue Service
        self.upload_queue = UploadQueueService(
            telegram_client=self.telegram_client,
            captures_dir=self.captures_dir,
            interval=10
        )
        
        uploader_thread = threading.Thread(
            target=self.upload_queue.start,
            args=(self.stop_event,),
            name="UploadQueueThread",
            daemon=True
        )
        uploader_thread.start()

        # 3. Start Shutdown Listener
        self.shutdown_listener = ShutdownListener(callback=self.send_shutdown_alert)
        shutdown_thread = threading.Thread(
            target=self.shutdown_listener.start,
            name="ShutdownListenerThread",
            daemon=True
        )
        shutdown_thread.start()

        # Keep main thread alive
        try:
            while not self.stop_event.is_set():
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            logger.info("KeyboardInterrupt or SystemExit. Stopping service engine...")
            self.stop_event.set()

    def run_commander(self):
        """Starts the interactive Telegram Polling Commander (USER context)."""
        logger.info("=== VigiLo Running in COMMANDER Mode ===")
        
        # 0. Single-Instance Mutex Guard
        self._commander_mutex = acquire_named_mutex("Local\\VigiLoCommanderMutex")
        if not self._commander_mutex:
            logger.warning("[SYSTEM] VigiLo Commander is already running! Exiting duplicate process.")
            return

        self.polling_service = TelegramPollingService(
            telegram_client=self.telegram_client,
            app_config=self.config,
            captures_dir=self.captures_dir
        )
        
        try:
            self.polling_service.start(self.stop_event)
        except (KeyboardInterrupt, SystemExit):
            logger.info("KeyboardInterrupt or SystemExit. Stopping commander polling...")
            self.stop_event.set()
