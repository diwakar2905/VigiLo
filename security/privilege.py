# security/privilege.py
import ctypes
import sys
from logs.logger import logger
from security.interfaces import IPermissionManager

class PermissionManager(IPermissionManager):
    def is_admin(self) -> bool:
        """Checks if current user has Admin privileges."""
        return is_admin()

    def is_system(self) -> bool:
        """Checks if process is running under NT AUTHORITY\\SYSTEM."""
        return is_system()

    def acquire_mutex(self, mutex_name: str) -> object:
        """Acquires a named Win32 mutex."""
        return acquire_named_mutex(mutex_name)

def is_admin():
    """Returns True if the current process has administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception as e:
        logger.error(f"Failed to check admin status: {e}")
        return False

def elevate():
    """Relaunches the current process with administrator privileges."""
    if not is_admin():
        logger.info("Requesting administrator privileges...")
        try:
            params = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, params, None, 1
            )
            sys.exit(0)
        except Exception as e:
            logger.error(f"UAC elevation request failed: {e}")
            return False
    return True

def is_system():
    """Checks if the current process is running in the SYSTEM context (NT AUTHORITY\\SYSTEM)."""
    try:
        buf = ctypes.create_unicode_buffer(256)
        buf_size = ctypes.c_ulong(256)
        if ctypes.windll.advapi32.GetUserNameW(buf, ctypes.byref(buf_size)):
            user_name = buf.value.upper()
            return user_name == "SYSTEM" or "NT AUTHORITY" in user_name
    except Exception as e:
        logger.error(f"Failed to check SYSTEM context: {e}")
    return False

ERROR_ALREADY_EXISTS = 183

def acquire_named_mutex(mutex_name):
    """
    Attempts to create/acquire a global named mutex.
    Returns the mutex handle if successful, or None if another instance is already running.
    """
    try:
        kernel32 = ctypes.windll.kernel32
        mutex_handle = kernel32.CreateMutexW(None, True, mutex_name)
        last_error = kernel32.GetLastError()
        if last_error == ERROR_ALREADY_EXISTS:
            if mutex_handle:
                kernel32.CloseHandle(mutex_handle)
            return None
        return mutex_handle
    except Exception as e:
        logger.error(f"Failed to acquire named mutex '{mutex_name}': {e}")
        return True

class PermissionMatrix:
    def __init__(self, permission_manager):
        self.pm = permission_manager

    def check_permission(self, action: str, context_details: dict = None) -> bool:
        """Verifies if the current context satisfies declarative permission rules."""
        if action in ["CaptureCamera", "CaptureScreen", "RecordAudio", "AccessFiles", "SpeakText"]:
            # Requires Admin or SYSTEM privileges
            return self.pm.is_admin() or self.pm.is_system()
        elif action == "LockWorkstation":
            return True
        return False


