# services/upload_queue.py
import os
import time
import threading
from api.telegram_client import TelegramClient
from utils.network import check_internet
from utils.system import get_captures_dir
from logs.logger import logger
from core.runtime import IService

class UploadQueueService(IService):
    def __init__(self, telegram_client, captures_dir=None, interval=10):
        self.client = telegram_client
        self.captures_dir = captures_dir if captures_dir else get_captures_dir()
        self.interval = interval
        self.stop_event = threading.Event()
        self._thread = None
        self._healthy = True

    def initialize(self) -> bool:
        """Ensures that the cache captures directory exists."""
        if not os.path.exists(self.captures_dir):
            try:
                os.makedirs(self.captures_dir, exist_ok=True)
            except Exception as e:
                logger.error(f"UploadQueueService failed to create captures directory: {e}")
                return False
        return True

    def start(self) -> bool:
        self.stop_event.clear()
        self._thread = threading.Thread(target=self._run, name="UploadQueueThread", daemon=True)
        self._thread.start()
        return True

    def stop(self) -> bool:
        self.stop_event.set()
        if self._thread:
            self._thread.join(timeout=3)
        return True

    def restart(self) -> bool:
        self.stop()
        return self.start()

    def health(self) -> bool:
        return self._healthy and (self._thread is not None and self._thread.is_alive())

    def status(self) -> str:
        if self.health():
            return "RUNNING"
        return "STOPPED"

    def _run(self):
        """Monitors the captures folder and uploads pending files when online."""
        logger.info(f"Upload queue worker started. Monitoring folder: {self.captures_dir}")
        
        while not self.stop_event.is_set():
            try:
                from core.runtime import ServiceManager
                ServiceManager().publish_heartbeat("UploadQueueService")
            except Exception:
                pass

            if not os.path.exists(self.captures_dir):
                time.sleep(5)
                continue

            try:
                files = [f for f in os.listdir(self.captures_dir) if f.endswith(".jpg") or f.endswith(".png")]
                self._healthy = True
            except Exception as e:
                logger.error(f"Failed to list captures directory: {e}")
                files = []
                self._healthy = False

            if not files:
                time.sleep(5)
                continue

            logger.debug(f"Found {len(files)} pending upload files in queue. Checking connectivity...")
            
            if check_internet():
                logger.info("Internet connected. Uploading queue...")
                for filename in files:
                    if self.stop_event.is_set():
                        break

                    # Skip commander-specific files (Commander handles them synchronously)
                    if filename.startswith("cmd_"):
                        continue

                    filepath = os.path.join(self.captures_dir, filename)
                    logger.info(f"Uploading file from queue: {filename}")
                    
                    caption = "🚨 Intruder attempt detected! (Buffered Alert Image)"
                    if self.client.send_photo(filepath, caption=caption):
                        logger.info(f"Successfully uploaded: {filename}")
                        try:
                            os.remove(filepath)
                        except Exception as delete_err:
                            logger.error(f"Failed to delete uploaded queue file: {delete_err}")
                    else:
                        logger.warning(f"Failed to upload {filename}. Will retry next cycle.")
            else:
                logger.debug("Internet is offline. Postponing queue upload.")
                
            time.sleep(self.interval)
