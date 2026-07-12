# config/cache.py
import threading

class ConfigCache:
    def __init__(self):
        self._cached_config = None
        self._lock = threading.Lock()

    def get(self):
        """Thread-safe retrieval of cached configuration."""
        with self._lock:
            return self._cached_config

    def set(self, app_config):
        """Thread-safe update of cached configuration."""
        with self._lock:
            self._cached_config = app_config

    def clear(self):
        """Thread-safe cache invalidation."""
        with self._lock:
            self._cached_config = None
