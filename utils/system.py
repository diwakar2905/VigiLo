# utils/system.py
import sys
import os

def is_frozen():
    """Returns True if the application is running as a compiled PyInstaller executable."""
    return getattr(sys, 'frozen', False)

def get_base_dir():
    """Returns the base execution directory (executable directory for frozen, project root for script)."""
    if is_frozen():
        return os.path.dirname(sys.executable)
    # utils/system.py is in WatchDog/utils, so its parent directory is WatchDog/
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_config_path():
    """Returns the absolute path to config.json."""
    return os.path.join(get_base_dir(), "config.json")

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller _MEIPASS extraction."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = get_base_dir()
    return os.path.join(base_path, relative_path)

def get_captures_dir():
    """Returns the absolute path to the ProgramData folder used for image and audio logs, ensuring it exists."""
    image_dir = os.getenv("PROGRAMDATA") or "C:\\ProgramData"
    captures_dir = os.path.join(image_dir, "VigiLoCaptures")
    if not os.path.exists(captures_dir):
        try:
            os.makedirs(captures_dir)
        except Exception as e:
            print(f"[ERROR] Failed to create captures directory: {e}")
    return captures_dir
