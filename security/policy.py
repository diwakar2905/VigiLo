# security/policy.py
"""Security policy engine for VigiLo.

Provides:
  - Sandbox jail path enforcement (path traversal prevention)
  - Per-chat_id sliding-window rate limiting
"""

from __future__ import annotations

import threading
import time
from collections import deque
from typing import Deque

from logs.logger import logger
from security.interfaces import ISecurityPolicyEngine
from security.sanitizer import is_safe_path, sanitize_filename

# --------------------------------------------------------------------------- #
# Rate limiter constants
# --------------------------------------------------------------------------- #
_RATE_WINDOW_SECONDS: int = 60
_DEFAULT_MAX_COMMANDS: int = 20


class RateLimiter:
    """Sliding-window per-actor rate limiter.

    Parameters
    ----------
    max_commands:
        Maximum number of commands allowed within *window_seconds*.
    window_seconds:
        Length of the sliding window in seconds (default 60).
    """

    def __init__(
        self,
        max_commands: int = _DEFAULT_MAX_COMMANDS,
        window_seconds: int = _RATE_WINDOW_SECONDS,
    ) -> None:
        self.max_commands: int = max_commands
        self.window_seconds: int = window_seconds
        # {chat_id: deque of timestamps}
        self._buckets: dict[str, Deque[float]] = {}
        self._lock = threading.Lock()

    def is_allowed(self, chat_id: str) -> bool:
        """Returns ``True`` if the actor is within rate limits; ``False`` if blocked.

        Internally prunes timestamps older than the sliding window before checking.
        """
        now = time.time()
        cutoff = now - self.window_seconds

        with self._lock:
            bucket = self._buckets.setdefault(chat_id, deque())

            # Prune stale entries
            while bucket and bucket[0] < cutoff:
                bucket.popleft()

            if len(bucket) >= self.max_commands:
                return False

            bucket.append(now)
            return True


class SecurityPolicyEngine(ISecurityPolicyEngine):
    """Implements runtime security policies for VigiLo.

    Parameters
    ----------
    rate_limiter:
        Optional injected ``RateLimiter`` (defaults to ``_DEFAULT_MAX_COMMANDS`` / minute).
    """

    def __init__(self, rate_limiter: RateLimiter | None = None) -> None:
        self._rate_limiter = rate_limiter if rate_limiter else RateLimiter()

    def enforce_sandbox_jail(self, target_path: str, jail_path: str) -> bool:
        """Verifies if *target_path* lies strictly within *jail_path*."""
        return is_safe_path(jail_path, target_path, follow_symlinks=True)

    def sanitize_filename(self, filename: str) -> str:
        """Strips unsafe path operators from file names."""
        return sanitize_filename(filename)

    def enforce_rate_limit(self, chat_id: str) -> bool:
        """Returns ``True`` if the chat_id is within rate limits.

        Should be called once per incoming command *before* dispatching.
        Returns ``False`` when the actor has exceeded ``max_commands`` within
        the sliding window — the caller is responsible for logging and rejecting.
        """
        allowed = self._rate_limiter.is_allowed(chat_id)
        if not allowed:
            logger.warning(
                f"SecurityPolicyEngine: Rate limit exceeded for chat_id={chat_id} "
                f"(max {self._rate_limiter.max_commands} commands / "
                f"{self._rate_limiter.window_seconds}s window)."
            )
        return allowed
