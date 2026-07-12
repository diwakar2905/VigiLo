# security/crypt.py
import ctypes
import threading
from ctypes import wintypes
from logs.logger import logger
from security.interfaces import ISecretManager, ISecretRotator
from security.secure_memory import SecureMemory

class DATA_BLOB(ctypes.Structure):
    _fields_ = [
        ('cbData', wintypes.DWORD),
        ('pbData', ctypes.POINTER(ctypes.c_char))
    ]

class SecretManager(ISecretManager, ISecretRotator):
    def __init__(self):
        self._cache = {}
        self._lock = threading.Lock()
        self.secure_mem = SecureMemory()

    def encrypt(self, plaintext: str) -> str:
        """Encrypts sensitive credentials via Windows DPAPI and caches it."""
        with self._lock:
            for c, p in self._cache.items():
                if p == plaintext:
                    return c
            ciphertext = encrypt_data(plaintext)
            self._cache[ciphertext] = plaintext
            return ciphertext

    def decrypt(self, ciphertext: str) -> str:
        """Decrypts sensitive credentials via Windows DPAPI utilizing cache."""
        with self._lock:
            if ciphertext in self._cache:
                return self._cache[ciphertext]
            plaintext = decrypt_data(ciphertext)
            self._cache[ciphertext] = plaintext
            return plaintext

    def clear_cache(self):
        """Securely wipes all cached secret values from memory and clears cache keys."""
        with self._lock:
            for ciphertext, plaintext in list(self._cache.items()):
                self.secure_mem.secure_wipe(plaintext)
                self.secure_mem.secure_wipe(ciphertext)
            self._cache.clear()

    def rotate_secrets(self) -> bool:
        """Future secret rotation interface hook."""
        logger.info("SecretManager: Secret rotation sequence requested (interface placeholder).")
        return True

def encrypt_data(plaintext_str):
    """
    Encrypts a string using Windows Data Protection API (DPAPI).
    Returns a hex-encoded cipher text string, or the original string on failure.
    """
    if not plaintext_str or "YOUR_" in plaintext_str:
        return plaintext_str
        
    try:
        crypt32 = ctypes.windll.crypt32
        local_free = ctypes.windll.kernel32.LocalFree

        data_bytes = plaintext_str.encode('utf-8')
        
        in_blob = DATA_BLOB()
        in_blob.cbData = len(data_bytes)
        in_blob.pbData = ctypes.cast(ctypes.create_string_buffer(data_bytes), ctypes.POINTER(ctypes.c_char))
        
        out_blob = DATA_BLOB()
        
        # 0x01 = CRYPTPROTECT_UI_FORBIDDEN
        success = crypt32.CryptProtectData(
            ctypes.byref(in_blob),
            None,
            None,
            None,
            None,
            0x01,
            ctypes.byref(out_blob)
        )
        
        if not success:
            logger.error("DPAPI: CryptProtectData failed.")
            return plaintext_str
            
        encrypted_bytes = ctypes.string_at(out_blob.pbData, out_blob.cbData)
        local_free(out_blob.pbData)
        
        return encrypted_bytes.hex()
        
    except Exception as e:
        logger.error(f"DPAPI: Data encryption exception: {e}")
        return plaintext_str

def decrypt_data(ciphertext_hex):
    """
    Decrypts a hex-encoded DPAPI cipher text string.
    Returns the plaintext string, or the original string on failure.
    """
    if not ciphertext_hex or len(ciphertext_hex) < 10:
        # Not a valid DPAPI hex string (backward compatibility fallback)
        return ciphertext_hex
        
    try:
        try:
            cipher_bytes = bytes.fromhex(ciphertext_hex)
        except ValueError:
            # Not a valid hex string, return as-is
            return ciphertext_hex

        crypt32 = ctypes.windll.crypt32
        local_free = ctypes.windll.kernel32.LocalFree
        
        in_blob = DATA_BLOB()
        in_blob.cbData = len(cipher_bytes)
        in_blob.pbData = ctypes.cast(ctypes.create_string_buffer(cipher_bytes), ctypes.POINTER(ctypes.c_char))
        
        out_blob = DATA_BLOB()
        
        # 0x01 = CRYPTPROTECT_UI_FORBIDDEN
        success = crypt32.CryptUnprotectData(
            ctypes.byref(in_blob),
            None,
            None,
            None,
            None,
            0x01,
            ctypes.byref(out_blob)
        )
        
        if not success:
            logger.error("DPAPI: CryptUnprotectData failed.")
            return ciphertext_hex
            
        decrypted_bytes = ctypes.string_at(out_blob.pbData, out_blob.cbData)
        local_free(out_blob.pbData)
        
        return decrypted_bytes.decode('utf-8')
        
    except Exception as e:
        logger.error(f"DPAPI: Data decryption exception: {e}")
        return ciphertext_hex
