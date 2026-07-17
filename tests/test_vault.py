# tests/test_vault.py
import json
import os
import tempfile
from unittest.mock import MagicMock, patch
from cryptography.fernet import Fernet

from config.schema import AppConfig, VaultConfig, TelegramConfig
from config.manager import ConfigManager
from modules.vault import VaultModule


def test_vault_lock_unlock_roundtrip():
    """Verify that VaultModule locks (encrypts) and unlocks (decrypts) files correctly."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Create a test file
        test_file_path = os.path.join(tmp_dir, "secrets.txt")
        original_content = b"my super secret database password"
        with open(test_file_path, "wb") as f:
            f.write(original_content)

        key = Fernet.generate_key()
        vm = VaultModule(target_dir=tmp_dir, key=key)

        # 1. Lock the vault
        assert vm.lock() is True

        # Check file was renamed to .locked and content is encrypted
        locked_file_path = test_file_path + ".locked"
        assert os.path.exists(locked_file_path)
        assert not os.path.exists(test_file_path)

        with open(locked_file_path, "rb") as f:
            encrypted_content = f.read()
        assert encrypted_content != original_content

        # Verify it can be decrypted
        f_fernet = Fernet(key)
        assert f_fernet.decrypt(encrypted_content) == original_content

        # 2. Unlock the vault
        assert vm.unlock() is True

        # Check original file path restored and content decrypted
        assert os.path.exists(test_file_path)
        assert not os.path.exists(locked_file_path)

        with open(test_file_path, "rb") as f:
            decrypted_content = f.read()
        assert decrypted_content == original_content


def test_vault_skips_locked_files_and_ignores_normal_on_unlock():
    """Verify that lock() ignores already locked files and unlock() ignores un-locked files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # File 1: plain file
        file1 = os.path.join(tmp_dir, "plain.txt")
        with open(file1, "wb") as f:
            f.write(b"plain text content")

        key = Fernet.generate_key()
        f_fernet = Fernet(key)

        # File 2: already locked file (must contain a valid encrypted payload)
        file2 = os.path.join(tmp_dir, "pre_locked.txt.locked")
        with open(file2, "wb") as f:
            f.write(f_fernet.encrypt(b"prelocked raw content"))

        vm = VaultModule(target_dir=tmp_dir, key=key)

        # Lock
        assert vm.lock() is True

        # plain.txt -> plain.txt.locked
        assert os.path.exists(file1 + ".locked")
        assert not os.path.exists(file1)

        # pre_locked.txt.locked should not have changed name (i.e. not renamed to .locked.locked)
        assert os.path.exists(file2)
        assert not os.path.exists(file2 + ".locked")

        # Unlock
        assert vm.unlock() is True
        assert os.path.exists(file1)
        assert os.path.exists(
            file2[:-7]
        )  # pre_locked.txt.locked decrypted back to pre_locked.txt


def test_config_save_load_vault_key_encryption():
    """Verify config save/load roundtrip encrypts and decrypts the vault key using DPAPI."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        config_path = os.path.join(tmp_dir, "config.json")

        generated_key = Fernet.generate_key().decode("utf-8")

        app_config = AppConfig(
            telegram=TelegramConfig("token", "chatid"),
            vault=VaultConfig(
                enabled=True,
                target_dir=tmp_dir,
                vault_key=generated_key,
            ),
        )

        # Save config
        manager = ConfigManager(config_path=config_path)
        save_success = manager.save(app_config)
        assert save_success is True

        # Assert saved config file contains encrypted string (should not match plain generated key)
        with open(config_path, "r", encoding="utf-8") as f:
            saved_raw_dict = json.load(f)

        saved_vault_key = saved_raw_dict["vault"]["vault_key"]
        assert saved_vault_key != generated_key  # DPAPI encrypted

        # Load config and verify decrypted result matches original
        loaded_manager = ConfigManager(config_path=config_path)
        loaded_config = loaded_manager.config
        assert loaded_config.vault.enabled is True
        assert loaded_config.vault.target_dir == tmp_dir
        assert loaded_config.vault.vault_key == generated_key


def test_engine_auto_key_generation():
    """Verify engine generates and saves a new DPAPI-encrypted vault key on startup if empty."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        config_path = os.path.join(tmp_dir, "config.json")

        # Setup configuration with empty vault key
        app_config = AppConfig(
            telegram=TelegramConfig("bot_token_123", "chatid_456"),
            vault=VaultConfig(
                enabled=True,
                target_dir=tmp_dir,
                vault_key="",
            ),
        )

        manager = ConfigManager(config_path=config_path)
        manager.save(app_config)

        # Instantiate engine
        from core.engine import VigiLoEngine

        engine = VigiLoEngine(config_path=config_path)

        # Assert that a key was automatically generated and saved
        assert engine.config.vault.vault_key != ""
        # Check that it is a valid base64 Fernet key by instantiating Fernet
        f = Fernet(engine.config.vault.vault_key.encode("utf-8"))
        assert f is not None


@patch("modules.vault.VaultModule")
def test_telegram_polling_unlock_command_dispatch(mock_vault_module_class):
    """Verify that /unlock command is dispatched to VaultModule.unlock."""
    mock_vault_module = MagicMock()
    mock_vault_module_class.return_value = mock_vault_module
    mock_vault_module.unlock.return_value = True

    # Mock dependencies
    mock_tg_client = MagicMock()
    app_config = AppConfig(
        telegram=TelegramConfig("token", "12345"),
        vault=VaultConfig(enabled=True, target_dir="C:\\MyVault", vault_key="some_key"),
    )

    from services.telegram_polling import TelegramPollingService

    service = TelegramPollingService(
        telegram_client=mock_tg_client,
        app_config=app_config,
        captures_dir="captures",
    )

    # Dispatch /unlock command (with mock verified state)
    with patch(
        "security.core.security_core.authorization_manager.authorize_request",
        return_value=True,
    ), patch("security.core.security_core.authorization_manager.authorize_action"):
        service.execute_command("/unlock", "12345", "token_value")

    # Verify VaultModule.unlock was called
    mock_vault_module_class.assert_called_once_with(
        target_dir="C:\\MyVault", key="some_key"
    )
    mock_vault_module.unlock.assert_called_once()
    # Verify Telegram client sent success message
    mock_tg_client.send_message.assert_any_call("🔓 Unlocking VigiLo Vault data...")
    mock_tg_client.send_message.assert_any_call(
        "✅ Vault data unlocked and decrypted successfully."
    )
