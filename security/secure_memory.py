# security/secure_memory.py
import ctypes
from security.interfaces import ISecureMemory


class SecureMemory(ISecureMemory):
    def secure_wipe(self, string_obj: str) -> bool:
        """
        Attempts to overwrite the underlying buffer of Python string structures (for mutable bytearrays/ctypes).
        Returns True if the memory block was wiped, False otherwise.
        """
        if isinstance(string_obj, bytearray):
            for i in range(len(string_obj)):
                string_obj[i] = 0
            return True

        elif isinstance(string_obj, bytes):
            # Attempt to zero memory using ctypes pointers directly (use with caution)
            try:
                addr = (
                    id(string_obj) + 20
                )  # Offset for basic Python bytes data in CPython
                size = len(string_obj)
                ctypes.memset(addr, 0, size)
                return True
            except Exception:
                return False

        return False
