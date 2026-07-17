# tests/test_whatsapp.py
import json
import os
import tempfile
from unittest.mock import MagicMock, patch

from api.notification_interface import NotificationInterface
from api.telegram_client import TelegramClient
from api.whatsapp_client import WhatsAppClient
from api.notification_router import NotificationRouter
from config.schema import AppConfig, TelegramConfig, WhatsAppConfig
from config.manager import ConfigManager


def test_notification_interface_inheritance():
    """Verify that both Telegram and WhatsApp clients subclass NotificationInterface."""
    assert issubclass(TelegramClient, NotificationInterface)
    assert issubclass(WhatsAppClient, NotificationInterface)
    assert issubclass(NotificationRouter, NotificationInterface)


def test_whatsapp_client_unconfigured():
    """Verify that WhatsApp client skips execution if credentials are unconfigured or default."""
    client = WhatsAppClient(
        phone_number_id="YOUR_PHONE_NUMBER_ID",
        access_token="access_token",
        recipient_phone="12345",
    )
    assert client._is_configured() is False
    assert client.send_message("test") is False


@patch("requests.post")
def test_whatsapp_client_send_message(mock_post):
    """Verify that WhatsAppClient sends text messages to Graph API with correct payload."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_post.return_value = mock_resp

    client = WhatsAppClient(
        phone_number_id="109876",
        access_token="valid_token",
        recipient_phone="15550199999",
    )

    assert client.send_message("Hello VigiLo User") is True

    mock_post.assert_called_once()
    args, kwargs = mock_post.call_args
    assert args[0] == "https://graph.facebook.com/v18.0/109876/messages"
    assert kwargs["headers"]["Authorization"] == "Bearer valid_token"
    assert kwargs["json"]["to"] == "15550199999"
    assert kwargs["json"]["text"]["body"] == "Hello VigiLo User"


@patch("requests.post")
def test_whatsapp_client_send_media_flow(mock_post):
    """Verify that WhatsAppClient uploads media and then sends a media message referencing the ID."""
    # 1. First post: media upload returning id='media_id_999'
    mock_upload_resp = MagicMock()
    mock_upload_resp.status_code = 200
    mock_upload_resp.json.return_value = {"id": "media_id_999"}

    # 2. Second post: media message dispatch
    mock_send_resp = MagicMock()
    mock_send_resp.status_code = 200

    mock_post.side_effect = [mock_upload_resp, mock_send_resp]

    client = WhatsAppClient(
        phone_number_id="109876",
        access_token="valid_token",
        recipient_phone="15550199999",
    )

    with tempfile.TemporaryDirectory() as tmp_dir:
        fake_photo = os.path.join(tmp_dir, "intruder.jpg")
        with open(fake_photo, "wb") as f:
            f.write(b"jpeg bytes")

        assert client.send_photo(fake_photo, caption="Forensic Capture") is True

    assert mock_post.call_count == 2
    # Verify first call: Upload media
    upload_call = mock_post.call_args_list[0]
    assert upload_call[0][0] == "https://graph.facebook.com/v18.0/109876/media"

    # Verify second call: Send photo message referencing media_id_999
    send_call = mock_post.call_args_list[1]
    assert send_call[0][0] == "https://graph.facebook.com/v18.0/109876/messages"
    assert send_call[1]["json"]["type"] == "image"
    assert send_call[1]["json"]["image"]["id"] == "media_id_999"
    assert send_call[1]["json"]["image"]["caption"] == "Forensic Capture"


def test_notification_router_routes_to_both_when_enabled():
    """Verify that NotificationRouter routes calls to both Telegram and WhatsApp if enabled."""
    mock_tg = MagicMock()
    mock_tg.send_message.return_value = True

    app_config = AppConfig(
        telegram=TelegramConfig("tg_token", "tg_chat"),
        whatsapp=WhatsAppConfig(
            enabled=True,
            phone_number_id="wa_id",
            access_token="wa_token",
            recipient_phone="wa_phone",
        ),
    )

    router = NotificationRouter(config=app_config, telegram_client=mock_tg)

    # Mock the internal whatsapp client
    mock_wa = MagicMock()
    mock_wa.send_message.return_value = True
    router.whatsapp = mock_wa

    assert router.send_message("Alert message") is True
    mock_tg.send_message.assert_called_once_with("Alert message", "Markdown")
    mock_wa.send_message.assert_called_once_with("Alert message", "Markdown")


def test_notification_router_skips_whatsapp_when_disabled():
    """Verify that NotificationRouter does not call WhatsApp if enabled=False in config."""
    mock_tg = MagicMock()
    mock_tg.send_message.return_value = True

    app_config = AppConfig(
        telegram=TelegramConfig("tg_token", "tg_chat"),
        whatsapp=WhatsAppConfig(
            enabled=False,
            phone_number_id="wa_id",
            access_token="wa_token",
            recipient_phone="wa_phone",
        ),
    )

    router = NotificationRouter(config=app_config, telegram_client=mock_tg)

    mock_wa = MagicMock()
    router.whatsapp = mock_wa

    assert router.send_message("Alert message") is True
    mock_tg.send_message.assert_called_once_with("Alert message", "Markdown")
    mock_wa.send_message.assert_not_called()


def test_config_save_load_whatsapp_credentials_encryption():
    """Verify config save/load roundtrip encrypts and decrypts WhatsApp credentials using DPAPI."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        config_path = os.path.join(tmp_dir, "config.json")

        app_config = AppConfig(
            telegram=TelegramConfig("token", "chatid"),
            whatsapp=WhatsAppConfig(
                enabled=True,
                phone_number_id="12345678",
                access_token="super_secret_wa_access_token",
                recipient_phone="+15551234567",
            ),
        )

        # Save config
        manager = ConfigManager(config_path=config_path)
        save_success = manager.save(app_config)
        assert save_success is True

        # Assert saved config file contains encrypted string (should not match plain strings)
        with open(config_path, "r", encoding="utf-8") as f:
            saved_raw_dict = json.load(f)

        saved_token = saved_raw_dict["whatsapp"]["access_token"]
        saved_phone = saved_raw_dict["whatsapp"]["recipient_phone"]
        assert saved_token != "super_secret_wa_access_token"
        assert saved_phone != "+15551234567"

        # Load config and verify decrypted result matches original
        loaded_manager = ConfigManager(config_path=config_path)
        loaded_config = loaded_manager.config
        assert loaded_config.whatsapp.enabled is True
        assert loaded_config.whatsapp.phone_number_id == "12345678"
        assert loaded_config.whatsapp.access_token == "super_secret_wa_access_token"
        assert loaded_config.whatsapp.recipient_phone == "+15551234567"
