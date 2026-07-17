# tests/test_security_utils.py
"""Unit tests for miscellaneous utility files in security package."""

from __future__ import annotations

import os
import tempfile
import time
import unittest
from unittest.mock import MagicMock, patch

from security.context import SecurityContext
from security.crypt import SecretManager, encrypt_data, decrypt_data
from security.hash import HashManager
from security.integrity import IntegrityManager
from security.privilege import (
    PermissionManager,
    is_admin,
    is_system,
    elevate,
    acquire_named_mutex,
    PermissionMatrix,
)
from security.secure_memory import SecureMemory
from security.auth import SessionManager


class TestSecurityContext(unittest.TestCase):
    def test_capture_fields(self) -> None:
        ctx = SecurityContext.capture("TestAction", "TestModule", "SUCCESS")
        self.assertIsInstance(ctx, dict)
        self.assertIn("timestamp", ctx)
        self.assertEqual(ctx["action"], "TestAction")
        self.assertEqual(ctx["calling_module"], "TestModule")
        self.assertEqual(ctx["result"], "SUCCESS")
        self.assertIsInstance(ctx["pid"], int)
        self.assertIsInstance(ctx["tid"], int)
        self.assertIsInstance(ctx["user"], str)
        self.assertIsInstance(ctx["session_id"], int)
        self.assertIsInstance(ctx["integrity_level"], str)


class TestCryptDPAPI(unittest.TestCase):
    def test_encrypt_decrypt_roundtrip(self) -> None:
        plaintext = "secret_password_123"
        ciphertext = encrypt_data(plaintext)
        self.assertNotEqual(plaintext, ciphertext)
        decrypted = decrypt_data(ciphertext)
        self.assertEqual(plaintext, decrypted)

    def test_encrypt_decrypt_empty_or_special(self) -> None:
        # None or YOUR_ should return as-is
        self.assertEqual(encrypt_data(""), "")
        self.assertEqual(encrypt_data("YOUR_BOT_TOKEN"), "YOUR_BOT_TOKEN")
        self.assertEqual(decrypt_data(""), "")
        self.assertEqual(decrypt_data("YOUR_BOT_TOKEN"), "YOUR_BOT_TOKEN")
        self.assertEqual(decrypt_data("short"), "short")
        self.assertEqual(decrypt_data("not-hex-string"), "not-hex-string")

    def test_secret_manager_cache(self) -> None:
        mgr = SecretManager()
        plaintext = "my-secret-token"
        ciphertext = mgr.encrypt(plaintext)
        # Verify cached encrypt
        self.assertEqual(mgr.encrypt(plaintext), ciphertext)
        # Verify cached decrypt
        self.assertEqual(mgr.decrypt(ciphertext), plaintext)
        # Verify direct decrypt
        mgr.clear_cache()
        self.assertEqual(mgr.decrypt(ciphertext), plaintext)

    def test_rotate_secrets(self) -> None:
        mgr = SecretManager()
        self.assertTrue(mgr.rotate_secrets())


class TestHashManager(unittest.TestCase):
    def test_hash_with_and_without_salt(self) -> None:
        hm = HashManager()
        h1 = hm.secure_hash("test-data")
        h2 = hm.secure_hash("test-data", salt="my-salt")
        self.assertNotEqual(h1, h2)
        self.assertEqual(len(h1), 64)


class TestIntegrityManager(unittest.TestCase):
    def test_calculate_sha256_missing_file(self) -> None:
        im = IntegrityManager()
        self.assertEqual(im.calculate_sha256("non-existent-file"), "")

    def test_calculate_sha256_and_verify(self) -> None:
        im = IntegrityManager()
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"Hello world integrity test")
            tmp_path = tmp.name

        try:
            expected_hash = (
                "d7f0298651eb92733c885b4c6f452e89874b4322cea0fcafc4837e443635740c"
            )
            self.assertEqual(im.calculate_sha256(tmp_path), expected_hash)
            self.assertTrue(im.verify_file(tmp_path, expected_hash))
            self.assertFalse(im.verify_file(tmp_path, "wrong-hash"))
            self.assertFalse(im.verify_file(tmp_path, ""))
            self.assertFalse(im.verify_file("non-existent", expected_hash))
        finally:
            os.remove(tmp_path)

    def test_verify_system_integrity(self) -> None:
        im = IntegrityManager()
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"file contents")
            tmp_path = tmp.name

        try:
            h = im.calculate_sha256(tmp_path)
            # Healthy verify
            report = im.verify_system_integrity({tmp_path: h})
            self.assertEqual(report["status"], "HEALTHY")
            self.assertEqual(len(report["failures"]), 0)

            # Mismatched hash verify
            report = im.verify_system_integrity({tmp_path: "bad-hash"})
            self.assertEqual(report["status"], "TAMPERED")
            self.assertEqual(report["failures"], [tmp_path])

            # Missing file verify
            report = im.verify_system_integrity({"missing-file-path.txt": "some-hash"})
            self.assertEqual(report["status"], "TAMPERED")
            self.assertEqual(report["failures"], ["missing-file-path.txt"])
        finally:
            os.remove(tmp_path)


class TestPrivilegeAndMatrix(unittest.TestCase):
    def test_is_admin_returns_bool(self) -> None:
        self.assertIsInstance(is_admin(), bool)

    def test_is_system_returns_bool(self) -> None:
        self.assertIsInstance(is_system(), bool)

    def test_elevate_already_admin(self) -> None:
        with patch("security.privilege.is_admin", return_value=True):
            self.assertTrue(elevate())

    def test_elevate_not_admin_calls_shellexecute(self) -> None:
        with patch("security.privilege.is_admin", return_value=False):
            with patch(
                "ctypes.windll.shell32.ShellExecuteW", return_value=32
            ) as mock_exec:
                with patch("sys.exit") as mock_exit:
                    elevate()
                    mock_exec.assert_called_once()
                    mock_exit.assert_called_once()

    def test_acquire_named_mutex(self) -> None:
        # Test creating mutex
        mutex1 = acquire_named_mutex("Local\\TestMutex_Unique_Name_123")
        self.assertIsNotNone(mutex1)
        # Test double acquire fails
        mutex2 = acquire_named_mutex("Local\\TestMutex_Unique_Name_123")
        self.assertIsNone(mutex2)
        # Release mutex1
        if mutex1:
            import ctypes

            ctypes.windll.kernel32.CloseHandle(mutex1)

    def test_permission_manager_delegations(self) -> None:
        pm = PermissionManager()
        self.assertIsInstance(pm.is_admin(), bool)
        self.assertIsInstance(pm.is_system(), bool)

        mutex = pm.acquire_mutex("Local\\TestMutex_Unique_Name_456")
        self.assertIsNotNone(mutex)
        if mutex:
            import ctypes

            ctypes.windll.kernel32.CloseHandle(mutex)

    def test_permission_matrix(self) -> None:
        pm_mock = MagicMock()
        matrix = PermissionMatrix(pm_mock)

        # Actions requiring admin/system
        for action in [
            "CaptureCamera",
            "CaptureScreen",
            "RecordAudio",
            "AccessFiles",
            "SpeakText",
        ]:
            pm_mock.is_admin.return_value = True
            self.assertTrue(matrix.check_permission(action))

            pm_mock.is_admin.return_value = False
            pm_mock.is_system.return_value = True
            self.assertTrue(matrix.check_permission(action))

            pm_mock.is_admin.return_value = False
            pm_mock.is_system.return_value = False
            self.assertFalse(matrix.check_permission(action))

        # LockWorkstation requires nothing
        self.assertTrue(matrix.check_permission("LockWorkstation"))

        # Unknown action
        self.assertFalse(matrix.check_permission("UnknownAction"))


class TestSecureMemory(unittest.TestCase):
    def test_secure_wipe_bytearray(self) -> None:
        sm = SecureMemory()
        ba = bytearray(b"secret_data")
        self.assertTrue(sm.secure_wipe(ba))
        self.assertEqual(ba, bytearray([0] * len(ba)))

    def test_secure_wipe_bytes(self) -> None:
        sm = SecureMemory()
        b = b"secret"
        res = sm.secure_wipe(b)
        self.assertIsInstance(res, bool)

    def test_secure_wipe_unsupported_type(self) -> None:
        sm = SecureMemory()
        self.assertFalse(sm.secure_wipe("not-bytes-or-bytearray"))


class TestSessionManager(unittest.TestCase):
    def test_session_lifecycle(self) -> None:
        sm = SessionManager()
        sess = sm.start_session("sess_001", {"ip": "127.0.0.1"})
        self.assertEqual(sess["session_id"], "sess_001")
        self.assertTrue(sess["active"])
        self.assertTrue(sm.validate_session("sess_001"))

        # Test non-existent session
        self.assertFalse(sm.validate_session("non-existent-session-id"))

        # Test timeout validation
        with patch("security.auth.time.time", return_value=time.time() + 7300):
            self.assertFalse(sm.validate_session("sess_001"))


if __name__ == "__main__":
    unittest.main()
