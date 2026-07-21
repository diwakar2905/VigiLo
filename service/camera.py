# import cv2  <-- Moved inside function
import time
import os

def capture_intruder_file(save_dir, cam_index=0, prefix="capture_"):
    """
    Captures a single frame and saves it to the specified directory.
    Returns the absolute path of the saved file, or None if failed.
    Optimized for speed (no warmup).
    """
    try:
        import cv2
        # Use DirectShow on Windows for faster init
        cam = cv2.VideoCapture(cam_index, cv2.CAP_DSHOW)
        
        # Immediate read
        ret, frame = cam.read()
        
        if not ret:
            # Ultra-fast retry
            time.sleep(0.01)
            ret, frame = cam.read()

        cam.release()
        
        if ret:
            timestamp = int(time.time())
            filename = f"{prefix}{timestamp}.jpg"
            save_path = os.path.join(save_dir, filename)
            cv2.imwrite(save_path, frame)
            return save_path
            
    except Exception as e:
        print(f"[ERROR] Camera capture failed: {e}")
        
    return None
