# modules/camera.py
import os
import time
from modules.base import BaseModule
from logs.logger import logger


class CameraModule(BaseModule):
    def __init__(self, device_index=0):
        self.device_index = device_index

    def execute(self, save_dir, prefix="capture_"):
        """
        Captures a single frame from the camera and saves it to save_dir.
        Returns the absolute filepath if successful, or None if failed.
        """
        try:
            import cv2

            # Use DirectShow on Windows for faster initialization
            cam = cv2.VideoCapture(self.device_index, cv2.CAP_DSHOW)

            # Read first frame immediately
            ret, frame = cam.read()
            if not ret:
                # Fast retry on lock/delay
                time.sleep(0.01)
                ret, frame = cam.read()

            cam.release()

            if ret:
                timestamp = int(time.time())
                filename = f"{prefix}{timestamp}.jpg"
                save_path = os.path.join(save_dir, filename)
                cv2.imwrite(save_path, frame)
                logger.info(f"Intruder captured successfully: {save_path}")
                return save_path
            else:
                logger.error("Failed to read frame from camera.")
        except Exception as e:
            logger.error(f"Camera module exception: {e}")

        return None
