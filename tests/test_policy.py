# tests/test_policy.py
"""Unit tests for security/policy.py — rate limiting and sandbox jail enforcement."""

from __future__ import annotations

import os
import tempfile
import time
import unittest
from unittest.mock import patch

from security.policy import RateLimiter, SecurityPolicyEngine


class TestRateLimiter(unittest.TestCase):

    def _make_limiter(self, max_commands: int = 5, window: int = 60) -> RateLimiter:
        return RateLimiter(max_commands=max_commands, window_seconds=window)

    def test_allows_commands_within_limit(self) -> None:
        rl = self._make_limiter(max_commands=5)
        for _ in range(5):
            self.assertTrue(rl.is_allowed("chat_001"))

    def test_blocks_on_limit_exceeded(self) -> None:
        rl = self._make_limiter(max_commands=5)
        for _ in range(5):
            rl.is_allowed("chat_001")
        # 6th command should be blocked
        self.assertFalse(rl.is_allowed("chat_001"))

    def test_different_actors_are_independent(self) -> None:
        rl = self._make_limiter(max_commands=3)
        for _ in range(3):
            rl.is_allowed("chat_A")
        # chat_A is blocked
        self.assertFalse(rl.is_allowed("chat_A"))
        # chat_B has its own independent bucket — should be allowed
        self.assertTrue(rl.is_allowed("chat_B"))

    def test_window_expiry_resets_count(self) -> None:
        """Commands from before the window should not count."""
        rl = self._make_limiter(max_commands=3, window=2)
        for _ in range(3):
            rl.is_allowed("chat_001")
        # Currently blocked
        self.assertFalse(rl.is_allowed("chat_001"))

        # Fast-forward 3 seconds past the 2-second window
        future_time = time.time() + 3
        with patch("security.policy.time") as mock_time:
            mock_time.time.return_value = future_time
            # Window has expired — old entries pruned, should be allowed again
            self.assertTrue(rl.is_allowed("chat_001"))

    def test_zero_commands_always_blocked(self) -> None:
        rl = self._make_limiter(max_commands=0)
        self.assertFalse(rl.is_allowed("chat_001"))


class TestSecurityPolicyEngine(unittest.TestCase):

    def test_enforce_rate_limit_allows_within_limit(self) -> None:
        engine = SecurityPolicyEngine(rate_limiter=RateLimiter(max_commands=10))
        for _ in range(10):
            self.assertTrue(engine.enforce_rate_limit("chat_001"))

    def test_enforce_rate_limit_blocks_exceeded(self) -> None:
        engine = SecurityPolicyEngine(rate_limiter=RateLimiter(max_commands=2))
        engine.enforce_rate_limit("chat_001")
        engine.enforce_rate_limit("chat_001")
        self.assertFalse(engine.enforce_rate_limit("chat_001"))

    def test_sandbox_jail_allows_child_path(self) -> None:
        with tempfile.TemporaryDirectory() as jail:
            child = os.path.join(jail, "subdir")
            os.makedirs(child)
            engine = SecurityPolicyEngine()
            self.assertTrue(engine.enforce_sandbox_jail(child, jail))

    def test_sandbox_jail_blocks_parent_escape(self) -> None:
        with tempfile.TemporaryDirectory() as jail:
            parent = os.path.dirname(jail)
            engine = SecurityPolicyEngine()
            self.assertFalse(engine.enforce_sandbox_jail(parent, jail))

    def test_sandbox_jail_blocks_sibling_path(self) -> None:
        with tempfile.TemporaryDirectory() as base:
            jail = os.path.join(base, "jail")
            sibling = os.path.join(base, "other")
            os.makedirs(jail)
            os.makedirs(sibling)
            engine = SecurityPolicyEngine()
            self.assertFalse(engine.enforce_sandbox_jail(sibling, jail))

    def test_sanitize_filename_strips_traversal(self) -> None:
        engine = SecurityPolicyEngine()
        result = engine.sanitize_filename("../../etc/passwd")
        self.assertNotIn("..", result)


if __name__ == "__main__":
    unittest.main()
