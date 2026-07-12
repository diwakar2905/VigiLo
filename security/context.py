# security/context.py
import os
import sys
import time
import threading
import ctypes
from logs.logger import logger

try:
    import win32security
    import win32api
    import win32con
except ImportError:
    win32security = None
    win32api = None
    win32con = None

class SecurityContext:
    @staticmethod
    def capture(action: str, calling_module: str, result: str) -> dict:
        """Captures the active Windows security metadata execution context."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        pid = os.getpid()
        tid = threading.get_ident()
        
        # Get User Name
        user = "Unknown"
        try:
            buf = ctypes.create_unicode_buffer(256)
            buf_size = ctypes.c_ulong(256)
            if ctypes.windll.advapi32.GetUserNameW(buf, ctypes.byref(buf_size)):
                user = buf.value
        except Exception:
            pass

        # Get Session ID
        session_id = 0
        try:
            current_pid = ctypes.windll.kernel32.GetCurrentProcessId()
            sid_val = ctypes.c_ulong()
            if ctypes.windll.kernel32.ProcessIdToSessionId(current_pid, ctypes.byref(sid_val)):
                session_id = sid_val.value
        except Exception:
            pass

        # Get Integrity Level
        integrity = "Medium"
        if win32security and win32api and win32con:
            try:
                token = win32security.OpenProcessToken(
                    win32api.GetCurrentProcess(),
                    win32con.TOKEN_QUERY
                )
                sid_and_attrs = win32security.GetTokenInformation(
                    token,
                    win32security.TokenIntegrityLevel
                )
                sid = sid_and_attrs[0]
                sub_authority = win32security.GetSidSubAuthority(sid, 0)
                
                if sub_authority == 0x1000:
                    integrity = "Untrusted"
                elif sub_authority == 0x2000:
                    integrity = "Low"
                elif sub_authority == 0x3000:
                    integrity = "Medium"
                elif sub_authority == 0x4000:
                    integrity = "High"
                elif sub_authority == 0x5000:
                    integrity = "System"
            except Exception:
                pass

        return {
            "timestamp": timestamp,
            "pid": pid,
            "tid": tid,
            "user": user,
            "session_id": session_id,
            "integrity_level": integrity,
            "calling_module": calling_module,
            "action": action,
            "result": result
        }
