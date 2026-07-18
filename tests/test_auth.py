# tests/test_auth.py
"""Unit tests for security/auth.py — HMAC token authorization."""

from __future__ import annotations

import time
import unittest
from unittest.mock import MagicMock, patch

from security.auth import AuthorizationManager, _derive_hmac_key


_FAKE_BOT_TOKEN = "1234567890:ABCDefghijKLMNopqrSTUVwxyz-FAKE_TOKEN"
_AUTHORIZED_CHAT_ID = "99887766"


def _make_manager(bot_token: str = _FAKE_BOT_TOKEN) -> AuthorizationManager:
    """Builds a manager with stubbed permission checks (always admin)."""
    pm_mock = MagicMock()
    pm_mock.is_admin.return_value = True
    pm_mock.is_system.return_value = False
    matrix_mock = MagicMock()
    matrix_mock.check_permission.return_value = True
    manager = AuthorizationManager(bot_token=bot_token)
    # Replace internals so we don't need real Windows DPAPI in CI
    manager.pm = pm_mock
    manager.matrix = matrix_mock
    return manager


class TestGenerateToken(unittest.TestCase):
    def test_generate_token_is_string(self) -> None:
        m = _make_manager()
        tok = m.generate_token(_AUTHORIZED_CHAT_ID)
        self.assertIsInstance(tok, str)

    def test_generate_token_has_four_parts(self) -> None:
        m = _make_manager()
        tok = m.generate_token(_AUTHORIZED_CHAT_ID)
        parts = tok.split(":")
        self.assertEqual(
            len(parts), 4, f"Token should have 4 colon-separated fields, got: {tok}"
        )

    def test_generate_token_raises_without_key(self) -> None:
        """Manager with no bot_token cannot generate a token."""
        m = AuthorizationManager()  # no bot_token → legacy mode
        with self.assertRaises(RuntimeError):
            m.generate_token(_AUTHORIZED_CHAT_ID)


class TestAuthorizeRequest(unittest.TestCase):

    def test_valid_token_accepted(self) -> None:
        m = _make_manager()
        tok = m.generate_token(_AUTHORIZED_CHAT_ID)
        result = m.authorize_request(
            _AUTHORIZED_CHAT_ID, _AUTHORIZED_CHAT_ID, token=tok
        )
        self.assertTrue(result)

    def test_expired_token_rejected(self) -> None:
        m = _make_manager()
        # Generate a token, then fake-forward time by 301 seconds
        tok = m.generate_token(_AUTHORIZED_CHAT_ID)
        with patch("security.auth.time") as mock_time:
            mock_time.time.return_value = time.time() + 301
            result = m.authorize_request(
                _AUTHORIZED_CHAT_ID, _AUTHORIZED_CHAT_ID, token=tok
            )
        self.assertFalse(result)

    def test_replayed_nonce_rejected(self) -> None:
        m = _make_manager()
        tok = m.generate_token(_AUTHORIZED_CHAT_ID)
        # First use — accepted
        first = m.authorize_request(_AUTHORIZED_CHAT_ID, _AUTHORIZED_CHAT_ID, token=tok)
        self.assertTrue(first)
        # Second use with same token — rejected
        second = m.authorize_request(
            _AUTHORIZED_CHAT_ID, _AUTHORIZED_CHAT_ID, token=tok
        )
        self.assertFalse(second)

    def test_tampered_hmac_rejected(self) -> None:
        m = _make_manager()
        tok = m.generate_token(_AUTHORIZED_CHAT_ID)
        # Corrupt the HMAC (last field)
        parts = tok.split(":")
        parts[-1] = "deadbeef" * 8  # wrong signature
        bad_tok = ":".join(parts)
        result = m.authorize_request(
            _AUTHORIZED_CHAT_ID, _AUTHORIZED_CHAT_ID, token=bad_tok
        )
        self.assertFalse(result)

    def test_wrong_chat_id_in_token_rejected(self) -> None:
        m = _make_manager()
        # Generate token for a different chat_id
        tok = m.generate_token("11111111")
        result = m.authorize_request(
            _AUTHORIZED_CHAT_ID, _AUTHORIZED_CHAT_ID, token=tok
        )
        self.assertFalse(result)

    def test_malformed_token_rejected(self) -> None:
        m = _make_manager()
        result = m.authorize_request(
            _AUTHORIZED_CHAT_ID, _AUTHORIZED_CHAT_ID, token="bad:token"
        )
        self.assertFalse(result)

    # ----------------------------------------------------------------------- #
    # Legacy / backward-compat path
    # ----------------------------------------------------------------------- #

    def test_legacy_fallback_matching_chat_id(self) -> None:
        """When token=None, plain chat_id compare returns True for matching IDs."""
        m = _make_manager()
        result = m.authorize_request(
            _AUTHORIZED_CHAT_ID, _AUTHORIZED_CHAT_ID, token=None
        )
        self.assertTrue(result)

    def test_legacy_fallback_wrong_chat_id(self) -> None:
        """When token=None, plain chat_id compare returns False for non-matching IDs."""
        m = _make_manager()
        result = m.authorize_request("00000000", _AUTHORIZED_CHAT_ID, token=None)
        self.assertFalse(result)

    def test_legacy_mode_no_bot_token(self) -> None:
        """Manager without bot_token operates in legacy mode and accepts matching chat_id."""
        m = AuthorizationManager()  # no bot_token
        result = m.authorize_request(
            _AUTHORIZED_CHAT_ID, _AUTHORIZED_CHAT_ID, token=None
        )
        self.assertTrue(result)

    def test_empty_chat_ids_rejected(self) -> None:
        m = _make_manager()
        self.assertFalse(m.authorize_request("", _AUTHORIZED_CHAT_ID, token=None))
        self.assertFalse(m.authorize_request(_AUTHORIZED_CHAT_ID, "", token=None))

    def test_non_integer_timestamp_rejected(self) -> None:
        m = _make_manager()
        # Token with non-integer timestamp
        tok = f"{_AUTHORIZED_CHAT_ID}:abc:nonce_value:signature"
        result = m.authorize_request(
            _AUTHORIZED_CHAT_ID, _AUTHORIZED_CHAT_ID, token=tok
        )
        self.assertFalse(result)

    def test_nonce_pruning(self) -> None:
        m = _make_manager()
        # Add expired nonce
        m._nonce_store["chat:old_nonce"] = time.time() - 10
        # Generate and use a new token (triggers prune)
        tok = m.generate_token(_AUTHORIZED_CHAT_ID)
        self.assertTrue(
            m.authorize_request(_AUTHORIZED_CHAT_ID, _AUTHORIZED_CHAT_ID, token=tok)
        )
        # Verify old nonce has been pruned
        self.assertNotIn("chat:old_nonce", m._nonce_store)

    def test_hmac_init_failure_fallback(self) -> None:
        # Mock _derive_hmac_key to raise an exception
        with patch(
            "security.auth._derive_hmac_key", side_effect=Exception("Failed derivation")
        ):
            m = AuthorizationManager(bot_token="some_token")
            # Should fallback to legacy mode and allow matching chat_id
            self.assertFalse(m.authorize_request("1", "2", token=None))
            self.assertTrue(m.authorize_request("1", "1", token=None))

    def test_authorize_action_success(self) -> None:
        m = _make_manager()
        # Simple action check
        self.assertTrue(m.authorize_action("LockWorkstation", "TestModule"))

    def test_authorize_action_permission_denied(self) -> None:
        m = _make_manager()
        m.matrix.check_permission.return_value = False
        from security.exceptions import AccessDeniedError

        with self.assertRaises(AccessDeniedError):
            m.authorize_action("CaptureCamera", "TestModule")

    def test_authorize_action_sandbox_jail_violation(self) -> None:
        m = _make_manager()
        m.policy = MagicMock()
        m.policy.enforce_sandbox_jail.return_value = False
        from security.exceptions import PolicyViolationError

        with self.assertRaises(PolicyViolationError):
            m.authorize_action(
                "AccessFiles",
                "TestModule",
                context_details={
                    "target_path": "C:\\Windows\\system32",
                    "jail_path": "C:\\safe",
                },
            )


class TestDeriveHmacKey(unittest.TestCase):
    def test_key_is_32_bytes(self) -> None:
        key = _derive_hmac_key(_FAKE_BOT_TOKEN)
        self.assertEqual(len(key), 32)

    def test_key_is_deterministic(self) -> None:
        k1 = _derive_hmac_key(_FAKE_BOT_TOKEN)
        k2 = _derive_hmac_key(_FAKE_BOT_TOKEN)
        self.assertEqual(k1, k2)

    def test_different_tokens_produce_different_keys(self) -> None:
        k1 = _derive_hmac_key(_FAKE_BOT_TOKEN)
        k2 = _derive_hmac_key("other_token_string")
        self.assertNotEqual(k1, k2)


if __name__ == "__main__":
    unittest.main()
