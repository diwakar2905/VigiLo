# modules/locking.py
import ctypes
from modules.base import BaseModule
from logs.logger import logger


class LockingModule(BaseModule):
    def execute(self):
        """
        Locks the Windows Workstation session.
        Returns True if successful, False otherwise.
        """
        try:
            logger.info("Executing workstation lock command...")
            result = ctypes.windll.user32.LockWorkStation()
            if result != 0:
                logger.info("Workstation locked successfully.")
                return True
            logger.error("LockWorkStation API returned failure status.")
        except Exception as e:
            logger.error(f"Locking module exception: {e}")

        return False
