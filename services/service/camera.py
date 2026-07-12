# service/camera.py (Backward Compatibility Wrapper)
from modules.camera import CameraModule

def capture_intruder_file(save_dir, cam_index=0, prefix="capture_"):
    """Legacy wrapper delegating webcam capture to modules/camera.py."""
    cam = CameraModule(device_index=cam_index)
    return cam.execute(save_dir, prefix=prefix)
