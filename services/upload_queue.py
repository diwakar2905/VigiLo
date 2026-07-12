# services/upload_queue.py
import os
import time
from api.telegram_client import TelegramClient
from utils.network import check_internet
from utils.system import get_captures_dir
from logs.logger import logger

class UploadQueueService:
    def __init__(self, telegram_client, captures_dir=None, interval=10):
        self.client = telegram_client
        self.captures_dir = captures_dir if captures_dir else get_captures_dir()
        self.interval = interval

    def start(self, stop_event):
        """
        Monitors the captures folder and uploads pending files when online.
        """
        logger.info(f"Upload queue worker started. Monitoring folder: {self.captures_dir}")
        
        while not stop_event.is_set():
            if not os.path.exists(self.captures_dir):
                time.sleep(5)
                continue

            try:
                files = [f for f in os.listdir(self.captures_dir) if f.endswith(".jpg") or f.endswith(".png")]
            except Exception as e:
                logger.error(f"Failed to list captures directory: {e}")
                files = []

            if not files:
                time.sleep(5)
                continue

            logger.debug(f"Found {len(files)} pending upload files in queue. Checking connectivity...")
            
            if check_internet():
                logger.info("Internet connected. Uploading queue...")
                for filename in files:
                    # Skip commander-specific files (Commander handles them synchronously)
                    if filename.startswith("cmd_"):
                        continue

                    filepath = os.path.join(self.captures_dir, filename)
                    logger.info(f"Uploading file from queue: {filename}")
                    
                    # Upload
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
