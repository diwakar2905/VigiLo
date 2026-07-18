# security/hash.py
import hashlib
from security.interfaces import IHashManager


class HashManager(IHashManager):
    def secure_hash(self, data: str, salt: str = "") -> str:
        """Generates a secure SHA-256 hash using the specified data and salt values."""
        h = hashlib.sha256()
        if salt:
            h.update(salt.encode("utf-8"))
        h.update(data.encode("utf-8"))
        return h.hexdigest()
