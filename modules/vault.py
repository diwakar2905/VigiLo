# modules/vault.py
"""Vault Module for VigiLo.

Encrypts and decrypts designated folder contents in-place using Fernet
symmetric keys.
"""

from __future__ import annotations

import os
from cryptography.fernet import Fernet
from modules.base import BaseModule
from logs.logger import logger


class VaultModule(BaseModule):
    """Encrypts and decrypts a directory in-place using a symmetric Fernet key.

    Parameters
    ----------
    target_dir:
        The folder path whose contents should be encrypted/decrypted.
    key:
        The URL-safe base64-encoded 32-byte Fernet key.
    """

    def __init__(self, target_dir: str, key: str | bytes) -> None:
        self.target_dir = target_dir
        if isinstance(key, str):
            self.key = key.encode("utf-8")
        else:
            self.key = key

    def execute(self, action: str, *args, **kwargs) -> bool:
        """Executes the vault action ('lock' or 'unlock')."""
        if action == "lock":
            return self.lock()
        elif action == "unlock":
            return self.unlock()
        else:
            logger.error(f"VaultModule: Unknown action '{action}' requested.")
            return False

    def lock(self) -> bool:
        """Encrypts all files in the target directory recursively, appending '.locked' extension."""
        if not os.path.exists(self.target_dir):
            logger.warning(
                f"VaultModule: Target directory does not exist: {self.target_dir}"
            )
            return False

        try:
            f = Fernet(self.key)
            success = True
            for root, _, files in os.walk(self.target_dir):
                for file in files:
                    if file.endswith(".locked"):
                        continue
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "rb") as fp:
                            plaintext = fp.read()

                        ciphertext = f.encrypt(plaintext)

                        # Overwrite in-place
                        with open(file_path, "wb") as fp:
                            fp.write(ciphertext)

                        # Rename to mark as locked
                        os.rename(file_path, file_path + ".locked")
                        logger.info(
                            f"VaultModule: Encrypted and locked file: {file_path}"
                        )
                    except Exception as exc:
                        logger.error(
                            f"VaultModule: Failed to encrypt file '{file_path}': {exc}"
                        )
                        success = False
            return success
        except Exception as exc:
            logger.error(f"VaultModule: Locking operation failed: {exc}")
            return False

    def unlock(self) -> bool:
        """Decrypts all '.locked' files in the target directory recursively, removing the extension."""
        if not os.path.exists(self.target_dir):
            logger.warning(
                f"VaultModule: Target directory does not exist: {self.target_dir}"
            )
            return False

        try:
            f = Fernet(self.key)
            success = True
            for root, _, files in os.walk(self.target_dir):
                for file in files:
                    if not file.endswith(".locked"):
                        continue
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "rb") as fp:
                            ciphertext = fp.read()

                        plaintext = f.decrypt(ciphertext)

                        # Overwrite in-place
                        with open(file_path, "wb") as fp:
                            fp.write(plaintext)

                        # Rename back to original path
                        original_path = file_path[:-7]  # strip '.locked'
                        os.rename(file_path, original_path)
                        logger.info(
                            f"VaultModule: Decrypted and unlocked file: {original_path}"
                        )
                    except Exception as exc:
                        logger.error(
                            f"VaultModule: Failed to decrypt file '{file_path}': {exc}"
                        )
                        success = False
            return success
        except Exception as exc:
            logger.error(f"VaultModule: Unlocking operation failed: {exc}")
            return False
