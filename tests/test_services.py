# tests/test_services.py
"""Unit tests for services package: telegram_polling, upload_queue, and persistence."""

from __future__ import annotations

import os
import threading
import time
import unittest
from unittest.mock import MagicMock, patch

from services.persistence import PersistenceService
from services.upload_queue import UploadQueueService
from services.telegram_polling import TelegramPollingService


class TestPersistenceService(unittest.TestCase):
    def setUp(self) -> None:
        self.exe_path = r"C:\Program Files\VigiLo\VigiLo.exe"
        self.service = PersistenceService(self.exe_path)

    @patch("services.persistence.is_admin")
    def test_register_tasks_non_admin_fails(self, mock_is_admin: MagicMock) -> None:
        mock_is_admin.return_value = False
        self.assertFalse(self.service.register_tasks())

    @patch("services.persistence.is_admin")
    @patch("services.persistence.subprocess.run")
    def test_register_tasks_admin_success(
        self, mock_run: MagicMock, mock_is_admin: MagicMock
    ) -> None:
        mock_is_admin.return_value = True
        mock_run.return_value = MagicMock(returncode=0)

        with patch("builtins.open", unittest.mock.mock_open()):
            res = self.service.register_tasks()
            self.assertTrue(res)
            self.assertEqual(mock_run.call_count, 4)  # unregister + service + commander

    @patch("services.persistence.is_admin")
    def test_unregister_tasks_non_admin_fails(self, mock_is_admin: MagicMock) -> None:
        mock_is_admin.return_value = False
        self.assertFalse(self.service.unregister_tasks())

    @patch("services.persistence.is_admin")
    @patch("services.persistence.subprocess.run")
    def test_unregister_tasks_admin(
        self, mock_run: MagicMock, mock_is_admin: MagicMock
    ) -> None:
        mock_is_admin.return_value = True
        self.service.unregister_tasks()
        self.assertEqual(mock_run.call_count, 2)  # service + commander deletion

    @patch("services.persistence.is_admin")
    def test_add_registry_startup_non_admin_fails(
        self, mock_is_admin: MagicMock
    ) -> None:
        mock_is_admin.return_value = False
        self.assertFalse(self.service.add_registry_startup())

    @patch("services.persistence.is_admin")
    @patch("services.persistence.winreg")
    def test_add_registry_startup_admin(
        self, mock_winreg: MagicMock, mock_is_admin: MagicMock
    ) -> None:
        mock_is_admin.return_value = True
        mock_winreg.OpenKey.return_value = MagicMock()
        self.assertTrue(self.service.add_registry_startup())
        mock_winreg.OpenKey.assert_called_once()
        mock_winreg.SetValueEx.assert_called_once()

    @patch("services.persistence.is_admin")
    @patch("services.persistence.winreg")
    def test_remove_registry_startup_admin(
        self, mock_winreg: MagicMock, mock_is_admin: MagicMock
    ) -> None:
        mock_is_admin.return_value = True
        mock_winreg.OpenKey.return_value = MagicMock()
        self.assertTrue(self.service.remove_registry_startup())
        mock_winreg.OpenKey.assert_called_once()
        mock_winreg.DeleteValue.assert_called_once()


class TestUploadQueueService(unittest.TestCase):
    def setUp(self) -> None:
        self.client_mock = MagicMock()
        self.captures_dir = r"C:\fake_captures"
        self.service = UploadQueueService(
            self.client_mock, captures_dir=self.captures_dir, interval=0.1
        )

    @patch("services.upload_queue.os.path.exists")
    @patch("services.upload_queue.os.makedirs")
    def test_initialize(self, mock_makedirs: MagicMock, mock_exists: MagicMock) -> None:
        # Folder doesn't exist
        mock_exists.return_value = False
        self.assertTrue(self.service.initialize())
        mock_makedirs.assert_called_once_with(self.captures_dir, exist_ok=True)

        # Folder exists
        mock_exists.return_value = True
        mock_makedirs.reset_mock()
        self.assertTrue(self.service.initialize())
        mock_makedirs.assert_not_called()

    def test_pause_resume_stop_start_lifecycle(self) -> None:
        self.assertTrue(self.service.pause())
        self.assertTrue(self.service.resume())
        self.service.dispose()  # void method

        # Status stopped
        self.assertEqual(self.service.status(), "STOPPED")

        # Start service
        self.assertTrue(self.service.start())
        # Mock thread states to verify status method
        self.service._thread = MagicMock()
        self.service._thread.is_alive.return_value = True
        self.assertEqual(self.service.status(), "RUNNING")
        self.service.stop()
        self.service._thread = MagicMock()
        self.service._thread.is_alive.return_value = False
        self.assertEqual(self.service.status(), "STOPPED")

    @patch("services.upload_queue.check_internet")
    @patch("services.upload_queue.os.path.exists")
    @patch("services.upload_queue.os.listdir")
    @patch("services.upload_queue.os.remove")
    @patch("services.upload_queue.time.sleep")
    def test_run_loop_upload(
        self,
        mock_sleep: MagicMock,
        mock_remove: MagicMock,
        mock_listdir: MagicMock,
        mock_exists: MagicMock,
        mock_check_internet: MagicMock,
    ) -> None:
        mock_exists.return_value = True
        mock_listdir.return_value = ["cmd_capture.png", "alert_intruder.jpg"]
        mock_check_internet.return_value = True
        self.client_mock.send_photo.return_value = True

        # Stop event gets set when time.sleep is called at the end of the loop
        mock_sleep.side_effect = lambda s: self.service.stop_event.set()
        self.service._run()

        # Should upload alert_intruder.jpg, skip cmd_capture.png
        self.client_mock.send_photo.assert_called_once_with(
            os.path.join(self.captures_dir, "alert_intruder.jpg"),
            caption="🚨 Intruder attempt detected! (Buffered Alert Image)",
        )
        mock_remove.assert_called_once_with(
            os.path.join(self.captures_dir, "alert_intruder.jpg")
        )


class TestTelegramPollingService(unittest.TestCase):
    def setUp(self) -> None:
        self.client_mock = MagicMock()
        self.client_mock.bot_token = "fake_bot_token"
        self.app_config = MagicMock()
        self.app_config.telegram.chat_id = "123456"
        self.app_config.camera.device_index = 0
        self.captures_dir = r"C:\fake_captures"
        self.service = TelegramPollingService(
            self.client_mock, self.app_config, self.captures_dir
        )

    @patch("services.telegram_polling.requests.post")
    def test_set_menu_commands(self, mock_post: MagicMock) -> None:
        mock_post.return_value = MagicMock(status_code=200)
        self.service.set_menu_commands()
        mock_post.assert_called_once()

    @patch(
        "services.telegram_polling.security_core.authorization_manager.authorize_request"
    )
    @patch(
        "services.telegram_polling.security_core.authorization_manager.authorize_action"
    )
    def test_execute_command_auth_fail(
        self, mock_auth_action: MagicMock, mock_auth_req: MagicMock
    ) -> None:
        mock_auth_req.return_value = False
        self.service.execute_command("/ping", "123456", token="invalid")
        self.client_mock.send_message.assert_called_once_with(
            "❌ Authorization failed. Attach a valid signed token to your command."
        )

    @patch(
        "services.telegram_polling.security_core.authorization_manager.authorize_request"
    )
    @patch(
        "services.telegram_polling.security_core.authorization_manager.authorize_action"
    )
    def test_execute_command_ping(
        self, mock_auth_action: MagicMock, mock_auth_req: MagicMock
    ) -> None:
        mock_auth_req.return_value = True
        self.service.execute_command("/ping", "123456", token="valid")
        self.client_mock.send_message.assert_called_once_with(
            "🏓 Pong! VigiLo is active and listening."
        )
        mock_auth_action.assert_not_called()

    @patch(
        "services.telegram_polling.security_core.authorization_manager.authorize_request"
    )
    @patch(
        "services.telegram_polling.security_core.authorization_manager.authorize_action"
    )
    def test_execute_command_capture(
        self, mock_auth_action: MagicMock, mock_auth_req: MagicMock
    ) -> None:
        mock_auth_req.return_value = True
        self.service.camera_mod.execute = MagicMock(return_value="photo.jpg")

        with patch("services.telegram_polling.os.remove") as mock_remove:
            self.service.execute_command("/capture", "123456", token="valid")
            self.client_mock.send_message.assert_called_with("📸 Capturing photo...")
            self.client_mock.send_photo.assert_called_with(
                "photo.jpg", "📸 Remote webcam capture"
            )
            mock_remove.assert_called_once_with("photo.jpg")
            mock_auth_action.assert_called_once_with(
                "CaptureCamera", "TelegramPollingService", {}
            )

    @patch(
        "services.telegram_polling.security_core.authorization_manager.authorize_request"
    )
    @patch(
        "services.telegram_polling.security_core.authorization_manager.authorize_action"
    )
    def test_execute_command_ls_sandbox(
        self, mock_auth_action: MagicMock, mock_auth_req: MagicMock
    ) -> None:
        mock_auth_req.return_value = True
        self.service.file_mod.execute = MagicMock(return_value="ls output")

        self.service.execute_command("/ls some_dir", "123456", token="valid")
        self.client_mock.send_message.assert_called_with("ls output")
        # Verify it passes jail paths
        mock_auth_action.assert_called_once()
        args = mock_auth_action.call_args[0]
        self.assertEqual(args[0], "AccessFiles")
        self.assertIn("target_path", args[2])
        self.assertIn("jail_path", args[2])

    @patch(
        "services.telegram_polling.security_core.authorization_manager.authorize_request"
    )
    @patch(
        "services.telegram_polling.security_core.authorization_manager.authorize_action"
    )
    @patch("services.telegram_polling.requests.Session")
    def test_start_polling_loop_rate_limit(
        self,
        mock_session_cls: MagicMock,
        mock_auth_action: MagicMock,
        mock_auth_req: MagicMock,
    ) -> None:
        # Mock Session
        session_mock = MagicMock()
        mock_session_cls.return_value = session_mock
        session_mock.get.return_value = MagicMock(
            status_code=200,
            json=lambda: {
                "ok": True,
                "result": [
                    {
                        "update_id": 1,
                        "message": {"from": {"id": 123456}, "text": "/ping"},
                    }
                ],
            },
        )

        # Mock rate limit check to exceed limit
        self.service.set_menu_commands = MagicMock()
        with patch(
            "services.telegram_polling.security_core.policy_engine.enforce_rate_limit",
            return_value=False,
        ) as mock_limit:
            stop_event = threading.Event()

            # Loop runs once and terminates
            def stop_loop_soon():
                time.sleep(0.1)
                stop_event.set()

            threading.Thread(target=stop_loop_soon, daemon=True).start()

            self.service.start(stop_event)
            mock_limit.assert_called_with("123456")
            self.client_mock.send_message.assert_called_with(
                "⚠️ Rate limit exceeded. Please slow down and retry in 60 seconds."
            )

    @patch(
        "services.telegram_polling.security_core.authorization_manager.authorize_request"
    )
    @patch(
        "services.telegram_polling.security_core.authorization_manager.authorize_action"
    )
    def test_execute_all_commands(
        self, mock_auth_action: MagicMock, mock_auth_req: MagicMock
    ) -> None:
        mock_auth_req.return_value = True

        # 1. /screen
        self.service.screenshot_mod.execute = MagicMock(return_value="screenshot.png")
        with patch("services.telegram_polling.os.remove") as mock_remove:
            self.service.execute_command("/screen", "123456", token="valid")
            self.client_mock.send_photo.assert_called_with(
                "screenshot.png", "🖥️ Remote desktop screenshot"
            )
            mock_remove.assert_called_with("screenshot.png")

        # 2. /lock success and failure
        self.service.locking_mod.execute = MagicMock(return_value=True)
        self.service.execute_command("/lock", "123456", token="valid")
        self.client_mock.send_message.assert_called_with(
            "✅ Workstation locked successfully."
        )

        self.service.locking_mod.execute = MagicMock(return_value=False)
        self.service.execute_command("/lock", "123456", token="valid")
        self.client_mock.send_message.assert_called_with(
            "❌ Failed to lock workstation."
        )

        # 3. /msg
        self.service.speech_mod.execute = MagicMock()
        self.service.execute_command("/msg hello there", "123456", token="valid")
        self.service.speech_mod.execute.assert_called_with("hello there")
        self.client_mock.send_message.assert_called_with(
            "📢 Displaying alert: 'hello there'"
        )

        self.service.execute_command("/msg", "123456", token="valid")
        self.client_mock.send_message.assert_called_with(
            "⚠️ Usage: /msg [alert message text]"
        )

        # 4. /locate
        self.service.locate_mod.execute = MagicMock(
            return_value={
                "wifi": [{"ssid": "HomeNetwork", "signal": "90%", "bssid": "aa:bb:cc"}],
                "geo": {
                    "lat": "40.7128",
                    "lon": "-74.0060",
                    "city": "New York",
                    "isp": "Verizon",
                    "query": "1.2.3.4",
                },
            }
        )
        with patch("threading.Thread") as mock_thread:
            self.service.execute_command("/locate", "123456", token="valid")
            mock_thread.assert_called_once()
        # Direct run to test output
        self.service._run_locate()
        self.client_mock.send_message.assert_called_with(
            "📍 *Detailed Location Report*\n"
            "--------------------------------\n"
            "🌍 *IP-Based Info*:\n"
            "   City: New York\n"
            "   ISP: Verizon\n"
            "   IP: 1.2.3.4\n"
            "   🔗 [Google Maps](https://maps.google.com/?q=40.7128,-74.0060)\n\n"
            "📡 *Nearby WiFi (Triangulation Data)*:\n"
            "📶 HomeNetwork (90%)\n   `aa:bb:cc`\n\n"
            "_Copy BSSIDs to Wigle.net for precise coordinate mapping_"
        )

        # 5. /stat
        self.service.stats_mod.execute = MagicMock(
            return_value={
                "os": "Windows",
                "cpu_usage": 15,
                "cpu_freq": "3.5GHz",
                "ram_used_gb": 4.0,
                "ram_total_gb": 16.0,
                "ram_percent": 25,
                "disk_free_gb": 100,
                "disk_total_gb": 500,
                "battery_percent": 80,
                "battery_plugged": True,
                "boot_time": "12:00",
            }
        )
        self.service._run_stats()
        self.client_mock.send_message.assert_called_with(
            "📊 *System Statistics*\n"
            "------------------------\n"
            "💻 *System*: Windows\n"
            "🧠 *CPU*: 15% (Freq: 3.5GHz)\n"
            "💾 *RAM*: 4.0GB / 16.0GB (25%)\n"
            "💿 *Disk (C:)*: 100GB free / 500GB\n"
            "⚡ *Battery*: 80% (🔌 Plugged In)\n"
            "⏱️ *Boot Time*: 12:00"
        )

        # 6. /listen
        self.service.audio_mod.execute = MagicMock(return_value="audio.wav")
        with patch("services.telegram_polling.os.remove") as mock_remove:
            self.service._run_listen(5)
            self.client_mock.send_audio.assert_called_with(
                "audio.wav", caption="🎤 Remote audio recording"
            )
            mock_remove.assert_called_with("audio.wav")

        # 7. /cd
        self.service.file_mod.execute = MagicMock(return_value="changed dir")
        self.service.execute_command("/cd my_dir", "123456", token="valid")
        self.client_mock.send_message.assert_called_with("changed dir")

        # 8. /download
        self.service.file_mod.execute = MagicMock(return_value="file.txt")
        self.service.execute_command("/download file.txt", "123456", token="valid")
        self.client_mock.send_message.assert_called_with(
            "⬇️ Uploading file 'file.txt'..."
        )
        self.client_mock.send_document.assert_called_with("file.txt")

        self.service.execute_command("/download", "123456", token="valid")
        self.client_mock.send_message.assert_called_with(
            "⚠️ Usage: /download [relative_or_absolute_file_path]"
        )

        # 9. /help
        self.service.execute_command("/help", "123456", token="valid")
        self.client_mock.send_message.assert_called_with(
            "🛡️ *VigiLo Command Center*\n\n"
            "All commands require a signed HMAC token suffix.\n\n"
            "• /ping — Check system status\n"
            "• /capture — Capture webcam snapshot\n"
            "• /listen [sec] — Record mic audio (max 30s)\n"
            "• /screen — Take silent desktop screenshot\n"
            "• /stat — Fetch system CPU/RAM metrics\n"
            "• /locate — Triangulate geolocation\n"
            "• /lock — Force workstation lock\n"
            "• /ls [path] — List files in sandbox\n"
            "• /cd [path] — Change working folder\n"
            "• /download [path] — Download file\n"
            "• /msg [text] — Popup warning and speak it\n"
            "• /help — View help commands list"
        )

        # 10. Unknown command
        self.service.execute_command("/unknown", "123456", token="valid")
        self.client_mock.send_message.assert_called_with("⚠️ Unknown command: /unknown")


class TestPersistenceServiceExceptions(unittest.TestCase):
    def setUp(self) -> None:
        self.service = PersistenceService("VigiLo.exe")

    @patch("services.persistence.is_admin", return_value=True)
    @patch(
        "services.persistence.subprocess.run",
        side_effect=Exception("Task create failed"),
    )
    def test_register_tasks_exception(
        self, mock_run: MagicMock, mock_admin: MagicMock
    ) -> None:
        with patch("builtins.open", unittest.mock.mock_open()):
            self.assertFalse(self.service.register_tasks())

    @patch("services.persistence.is_admin", return_value=True)
    @patch(
        "services.persistence.subprocess.run",
        side_effect=Exception("Task delete failed"),
    )
    def test_unregister_tasks_exception(
        self, mock_run: MagicMock, mock_admin: MagicMock
    ) -> None:
        self.service.unregister_tasks()  # Should handle the exception gracefully without raising

    @patch("services.persistence.is_admin", return_value=True)
    @patch(
        "services.persistence.winreg.OpenKey", side_effect=Exception("Reg open failed")
    )
    def test_add_registry_startup_exception(
        self, mock_open: MagicMock, mock_admin: MagicMock
    ) -> None:
        self.assertFalse(self.service.add_registry_startup())

    @patch("services.persistence.is_admin", return_value=True)
    @patch(
        "services.persistence.winreg.OpenKey", side_effect=Exception("Reg open failed")
    )
    def test_remove_registry_startup_exception(
        self, mock_open: MagicMock, mock_admin: MagicMock
    ) -> None:
        self.assertFalse(self.service.remove_registry_startup())

    @patch("services.persistence.is_admin", return_value=False)
    def test_remove_registry_startup_non_admin(self, mock_admin: MagicMock) -> None:
        self.assertFalse(self.service.remove_registry_startup())


class TestUploadQueueServiceExceptions(unittest.TestCase):
    def setUp(self) -> None:
        self.client = MagicMock()
        self.service = UploadQueueService(
            self.client, captures_dir="captures", interval=0.1
        )

    @patch("services.upload_queue.os.path.exists", return_value=False)
    @patch(
        "services.upload_queue.os.makedirs",
        side_effect=Exception("Directory create failed"),
    )
    def test_initialize_directory_create_fail(
        self, mock_makedirs: MagicMock, mock_exists: MagicMock
    ) -> None:
        self.assertFalse(self.service.initialize())

    def test_restart(self) -> None:
        self.service.stop = MagicMock()
        self.service.start = MagicMock(return_value=True)
        self.assertTrue(self.service.restart())
        self.service.stop.assert_called_once()
        self.service.start.assert_called_once()

    @patch("services.upload_queue.os.path.exists", return_value=False)
    @patch("services.upload_queue.time.sleep")
    def test_run_loop_directory_missing(
        self, mock_sleep: MagicMock, mock_exists: MagicMock
    ) -> None:
        mock_sleep.side_effect = lambda s: self.service.stop_event.set()
        self.service._run()
        mock_sleep.assert_called_with(5)

    @patch("services.upload_queue.os.path.exists", return_value=True)
    @patch("services.upload_queue.os.listdir", side_effect=Exception("List dir failed"))
    @patch("services.upload_queue.time.sleep")
    def test_run_loop_listdir_fail(
        self, mock_sleep: MagicMock, mock_listdir: MagicMock, mock_exists: MagicMock
    ) -> None:
        mock_sleep.side_effect = lambda s: self.service.stop_event.set()
        self.service._run()
        self.assertFalse(self.service._healthy)
        mock_sleep.assert_called_with(5)

    @patch("services.upload_queue.check_internet", return_value=True)
    @patch("services.upload_queue.os.path.exists", return_value=True)
    @patch("services.upload_queue.os.listdir", return_value=["alert_1.png"])
    @patch("services.upload_queue.time.sleep")
    def test_run_loop_upload_failed(
        self,
        mock_sleep: MagicMock,
        mock_listdir: MagicMock,
        mock_exists: MagicMock,
        mock_check_internet: MagicMock,
    ) -> None:
        self.client.send_photo.return_value = False
        mock_sleep.side_effect = lambda s: self.service.stop_event.set()
        self.service._run()
        self.client.send_photo.assert_called_once()


if __name__ == "__main__":
    unittest.main()
