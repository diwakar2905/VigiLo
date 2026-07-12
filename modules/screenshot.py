# modules/screenshot.py
import os
import time
from modules.base import BaseModule
from logs.logger import logger

class ScreenshotModule(BaseModule):
    def execute(self, save_dir, prefix="cmd_screen_"):
        """
        Captures a desktop screenshot and saves it to disk.
        Returns the absolute filepath if successful, or None.
        """
        try:
            import pyautogui
            timestamp = int(time.time())
            filename = f"{prefix}{timestamp}.png"
            filepath = os.path.join(save_dir, filename)
            
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            
            logger.info(f"Screenshot taken: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Screenshot module exception: {e}")
            
        return None
