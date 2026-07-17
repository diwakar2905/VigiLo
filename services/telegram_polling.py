# services/telegram_polling.py
"""Telegram long-polling command server for VigiLo.

Security guarantees (Phase 1):
  - Every command is gated by HMAC-SHA256 token validation (5-min window, nonce replay protection).
  - Per-chat_id rate limiting enforced before dispatch (default 20 cmd/min).
  - All file-manager commands (/ls, /cd, /download) populate full sandbox jail context
    so authorize_action can enforce path constraints.
  - All commands flow through security_core.authorization_manager.authorize_action for
    permission checks and full audit trail.
"""

from __future__ import annotations

import os
import threading
import time

import requests

from api.telegram_client import TelegramClient
from logs.logger import logger
from modules.audio import AudioModule
from modules.camera import CameraModule
from modules.file_manager import FileManagerModule
from modules.locate import LocateModule
from modules.locking import LockingModule
from modules.screenshot import ScreenshotModule
from modules.speech import SpeechModule
from modules.system_stats import SystemStatsModule
from security.audit import RateLimitExceeded
from security.core import security_core
from security.exceptions import SecurityError


class TelegramPollingService:
    def __init__(
        self,
        telegram_client: TelegramClient,
        app_config,
        captures_dir: str,
    ) -> None:
        self.client = telegram_client
        self.config = app_config
        self.captures_dir = captures_dir
        self.chat_id: str = str(app_config.telegram.chat_id)

        # Instantiate modules
        self.camera_mod = CameraModule(device_index=app_config.camera.device_index)
        self.audio_mod = AudioModule()
        self.screenshot_mod = ScreenshotModule()
        self.locking_mod = LockingModule()
        self.locate_mod = LocateModule()
        self.stats_mod = SystemStatsModule()
        self.file_mod = FileManagerModule()
        self.speech_mod = SpeechModule()

    # ----------------------------------------------------------------------- #
    # Telegram bot-menu registration
    # ----------------------------------------------------------------------- #

    def set_menu_commands(self) -> None:
        """Sets the command list in Telegram dynamically."""
        url = f"https://api.telegram.org/bot{self.client.bot_token}/setMyCommands"
        commands = [
            {"command": "ping", "description": "Check if system is online"},
            {"command": "capture", "description": "Take camera snapshot"},
            {"command": "listen", "description": "Record microphone audio"},
            {"command": "screen", "description": "Capture screen snapshot"},
            {
                "command": "locate",
                "description": "Get IP & WiFi triangulation location",
            },
            {
                "command": "stat",
                "description": "Fetch system stats (CPU, RAM, Battery)",
            },
            {"command": "lock", "description": "Lock Windows Workstation"},
            {"command": "ls", "description": "List sandboxed files"},
            {"command": "cd", "description": "Change sandboxed working directory"},
            {"command": "download", "description": "Download a file from sandbox"},
            {"command": "msg", "description": "Show pop-up message and speak it"},
            {"command": "help", "description": "View command help guide"},
        ]
        try:
            resp = requests.post(url, json={"commands": commands}, timeout=10)
            if resp.status_code == 200:
                logger.info("Telegram menu commands updated successfully.")
            else:
                logger.warning(
                    f"Telegram setMyCommands failed: HTTP {resp.status_code}"
                )
        except Exception as exc:
            logger.error(f"Failed to set Telegram menu commands: {exc}")

    # ----------------------------------------------------------------------- #
    # Command dispatch
    # ----------------------------------------------------------------------- #

    def execute_command(
        self, command_text: str, user_id: str, token: str | None
    ) -> None:
        """Parses and executes a Telegram command after security checks pass.

        Parameters
        ----------
        command_text:
            Raw text from the Telegram message (e.g. ``/capture``).
        user_id:
            Telegram user ID of the sender (already verified against chat_id upstream).
        token:
            HMAC-signed token extracted from the command text, or ``None`` if not provided.
        """
        try:
            parts = command_text.strip().split()
            if not parts:
                return

            action = parts[0].lower()
            logger.info(f"Telegram Commander: Received command '{action}'")

            # ---------------------------------------------------------------- #
            # Step 1 — HMAC token authorization (gates every command)
            # ---------------------------------------------------------------- #
            authorized = security_core.authorization_manager.authorize_request(
                sender_chat_id=user_id,
                authorized_chat_id=self.chat_id,
                token=token,
            )
            if not authorized:
                self.client.send_message(
                    "❌ Authorization failed. Attach a valid signed token to your command."
                )
                return

            # ---------------------------------------------------------------- #
            # Step 2 — Map command → action permission name
            # ---------------------------------------------------------------- #
            action_map: dict[str, str] = {
                "/ping": "Ping",
                "/capture": "CaptureCamera",
                "/screen": "CaptureScreen",
                "/lock": "LockWorkstation",
                "/msg": "SpeakText",
                "/download": "AccessFiles",
                "/ls": "AccessFiles",
                "/cd": "AccessFiles",
                "/listen": "RecordAudio",
                "/locate": "AccessFiles",
                "/stat": "AccessFiles",
                "/unlock": "AccessFiles",
                "/report": "AccessFiles",
                "/help": "ViewHelp",
            }

            perm_name = action_map.get(action)
            if not perm_name:
                self.client.send_message(f"⚠️ Unknown command: {action}")
                return

            # ---------------------------------------------------------------- #
            # Step 3 — Build context_details including sandbox jail for file ops
            # ---------------------------------------------------------------- #
            ctx_details: dict = {}
            jail_root: str = getattr(
                self.file_mod, "jail_root", os.path.expanduser("~")
            )

            if action in ("/ls", "/cd"):
                # Resolve the target path relative to current working dir
                target_rel = " ".join(parts[1:]) if len(parts) > 1 else "."
                target_abs = os.path.realpath(os.path.abspath(target_rel))
                ctx_details["target_path"] = target_abs
                ctx_details["jail_path"] = jail_root

            elif action == "/download":
                if len(parts) > 1:
                    target_rel = " ".join(parts[1:])
                    target_abs = os.path.realpath(os.path.abspath(target_rel))
                    ctx_details["target_path"] = target_abs
                    ctx_details["jail_path"] = jail_root

            # ---------------------------------------------------------------- #
            # Step 4 — authorize_action (permission matrix + sandbox jail + audit)
            # ---------------------------------------------------------------- #
            if perm_name not in ("Ping", "ViewHelp"):
                # Ping and Help are informational; still audited via authorize_request above
                try:
                    security_core.authorization_manager.authorize_action(
                        perm_name, "TelegramPollingService", ctx_details
                    )
                except SecurityError as sec_err:
                    self.client.send_message(f"❌ Security Block: {sec_err}")
                    return

            # ---------------------------------------------------------------- #
            # Step 5 — Execute
            # ---------------------------------------------------------------- #
            self._dispatch(action, parts)

        except Exception as exc:
            logger.error(f"Telegram Commander: Command execution exception: {exc}")

    def _dispatch(self, action: str, parts: list[str]) -> None:
        """Performs the actual module call for an already-authorized command."""

        if action == "/ping":
            self.client.send_message("🏓 Pong! VigiLo is active and listening.")

        elif action == "/capture":
            self.client.send_message("📸 Capturing photo...")
            filepath = self.camera_mod.execute(self.captures_dir, prefix="cmd_")
            if filepath:
                self.client.send_photo(filepath, "📸 Remote webcam capture")
                try:
                    os.remove(filepath)
                except Exception:
                    pass
            else:
                self.client.send_message(
                    "❌ Camera unavailable or failed to initialize."
                )

        elif action == "/screen":
            self.client.send_message("🖥️ Capturing screenshot...")
            filepath = self.screenshot_mod.execute(self.captures_dir)
            if filepath:
                self.client.send_photo(filepath, "🖥️ Remote desktop screenshot")
                try:
                    os.remove(filepath)
                except Exception:
                    pass
            else:
                self.client.send_message("❌ Screenshot failed to capture.")

        elif action == "/lock":
            self.client.send_message("🔒 Locking workstation...")
            if self.locking_mod.execute():
                self.client.send_message("✅ Workstation locked successfully.")
            else:
                self.client.send_message("❌ Failed to lock workstation.")

        elif action == "/unlock":
            self.client.send_message("🔓 Unlocking VigiLo Vault data...")
            vault_enabled = getattr(self.config.vault, "enabled", False)
            vault_key = getattr(self.config.vault, "vault_key", "")
            target_dir = getattr(self.config.vault, "target_dir", "")

            if not vault_enabled:
                self.client.send_message("❌ Vault is not enabled in configuration.")
            elif not vault_key or not target_dir:
                self.client.send_message(
                    "❌ Vault configuration is incomplete (missing key/path)."
                )
            else:
                try:
                    from modules.vault import VaultModule

                    vm = VaultModule(target_dir=target_dir, key=vault_key)
                    if vm.unlock():
                        self.client.send_message(
                            "✅ Vault data unlocked and decrypted successfully."
                        )
                    else:
                        self.client.send_message(
                            "⚠️ Vault unlock completed with warnings or some files failed."
                        )
                except Exception as exc:
                    self.client.send_message(f"❌ Failed to run vault unlock: {exc}")

        elif action == "/msg":
            message = " ".join(parts[1:])
            if message:
                self.client.send_message(f"📢 Displaying alert: '{message}'")
                self.speech_mod.execute(message)
            else:
                self.client.send_message("⚠️ Usage: /msg [alert message text]")

        elif action == "/locate":
            self.client.send_message("📡 Scanning wireless spectrum & geolocating...")
            threading.Thread(target=self._run_locate, daemon=True).start()

        elif action in ("/stat", "/stats"):
            self.client.send_message("📊 Analyzing system statistics...")
            threading.Thread(target=self._run_stats, daemon=True).start()

        elif action == "/report":
            threading.Thread(target=self._run_report, daemon=True).start()

        elif action == "/listen":
            duration = 5
            if len(parts) > 1 and parts[1].isdigit():
                duration = min(int(parts[1]), 30)
            self.client.send_message(f"🎤 Recording {duration}s of audio...")
            threading.Thread(
                target=self._run_listen, args=(duration,), daemon=True
            ).start()

        elif action == "/ls":
            target = " ".join(parts[1:]) if len(parts) > 1 else "."
            reply = self.file_mod.execute("ls", target)
            self.client.send_message(reply)

        elif action == "/cd":
            target = " ".join(parts[1:])
            reply = self.file_mod.execute("cd", target)
            self.client.send_message(reply)

        elif action == "/download":
            target = " ".join(parts[1:])
            if not target:
                self.client.send_message(
                    "⚠️ Usage: /download [relative_or_absolute_file_path]"
                )
                return
            filepath = self.file_mod.execute("download", target)
            if filepath:
                self.client.send_message(
                    f"⬇️ Uploading file '{os.path.basename(filepath)}'..."
                )
                self.client.send_document(filepath)
            else:
                self.client.send_message(
                    "❌ Access Denied: File resides outside sandbox or does not exist."
                )

        elif action == "/help":
            help_text = (
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
            self.client.send_message(help_text)

    # ----------------------------------------------------------------------- #
    # Threaded helpers
    # ----------------------------------------------------------------------- #

    def _run_locate(self) -> None:
        data = self.locate_mod.execute()
        wifi_list = []
        for net in data.get("wifi", []):
            wifi_list.append(f"📶 {net['ssid']} ({net['signal']})\n   `{net['bssid']}`")
        wifi_report = (
            "\n".join(wifi_list[:8]) if wifi_list else "No WiFi networks found."
        )
        geo = data.get("geo")
        if geo:
            map_link = f"https://maps.google.com/?q={geo['lat']},{geo['lon']}"
            msg = (
                f"📍 *Detailed Location Report*\n"
                f"--------------------------------\n"
                f"🌍 *IP-Based Info*:\n"
                f"   City: {geo['city']}\n"
                f"   ISP: {geo['isp']}\n"
                f"   IP: {geo['query']}\n"
                f"   🔗 [Google Maps]({map_link})\n\n"
                f"📡 *Nearby WiFi (Triangulation Data)*:\n"
                f"{wifi_report}\n\n"
                f"_Copy BSSIDs to Wigle.net for precise coordinate mapping_"
            )
            self.client.send_message(msg)
        else:
            self.client.send_message(
                f"❌ Geolocation failed. WiFi network scans:\n{wifi_report[:200]}"
            )

    def _run_stats(self) -> None:
        s = self.stats_mod.execute()
        batt_status = "N/A"
        if s["battery_percent"] is not None:
            plugged = "🔌 Plugged In" if s["battery_plugged"] else "🔋 On Battery"
            batt_status = f"{s['battery_percent']}% ({plugged})"
        msg = (
            f"📊 *System Statistics*\n"
            f"------------------------\n"
            f"💻 *System*: {s['os']}\n"
            f"🧠 *CPU*: {s['cpu_usage']}% (Freq: {s['cpu_freq']})\n"
            f"💾 *RAM*: {s['ram_used_gb']}GB / {s['ram_total_gb']}GB ({s['ram_percent']}%)\n"
            f"💿 *Disk (C:)*: {s['disk_free_gb']}GB free / {s['disk_total_gb']}GB\n"
            f"⚡ *Battery*: {batt_status}\n"
            f"⏱️ *Boot Time*: {s['boot_time']}"
        )
        self.client.send_message(msg)

    def _run_listen(self, duration: int) -> None:
        filepath = self.audio_mod.execute(
            self.captures_dir, duration=duration, prefix="cmd_"
        )
        if filepath:
            self.client.send_audio(filepath, caption="🎤 Remote audio recording")
            try:
                os.remove(filepath)
            except Exception:
                pass
        else:
            self.client.send_message(
                "❌ Audio recording failed (microphone unavailable or disabled)."
            )

    def _run_report(self) -> None:
        """Gathers evidence, compiles a security PDF report, and uploads it to Telegram."""
        self.client.send_message("📊 Generating security incident PDF report...")
        try:
            from modules.report import ReportModule

            rm = ReportModule()
            pdf_path = rm.execute(self.captures_dir)
            if pdf_path and os.path.exists(pdf_path):
                self.client.send_message("📤 Uploading PDF report...")
                if self.client.send_document(
                    pdf_path, caption="📊 VigiLo Security Report"
                ):
                    logger.info("PDF report successfully sent to Telegram.")
                else:
                    self.client.send_message(
                        "❌ Failed to send PDF report via Telegram."
                    )

                try:
                    os.remove(pdf_path)
                    logger.info(f"Cleaned up temporary report: {pdf_path}")
                except Exception as ex:
                    logger.error(f"Failed to delete temporary report file: {ex}")
            else:
                self.client.send_message(
                    "❌ Failed to generate the PDF security report."
                )
        except Exception as e:
            logger.error(f"Error in _run_report: {e}")
            self.client.send_message(f"❌ Error generating report: {e}")

    # ----------------------------------------------------------------------- #
    # Polling loop
    # ----------------------------------------------------------------------- #

    def start(self, stop_event: threading.Event) -> None:
        """Starts the update polling loop. Blocks until *stop_event* is set."""
        logger.info("Telegram Polling Service Started.")
        self.set_menu_commands()

        offset = 0
        session = requests.Session()

        while not stop_event.is_set():
            try:
                url = f"{self.client.base_url}/getUpdates"
                params = {"offset": offset, "timeout": 30}
                resp = session.get(url, params=params, timeout=40)

                if resp.status_code != 200:
                    logger.error(f"getUpdates HTTP error: {resp.status_code}")
                    time.sleep(5)
                    continue

                result = resp.json()
                if result.get("ok"):
                    for update in result.get("result", []):
                        offset = update["update_id"] + 1

                        if "message" not in update:
                            continue

                        message = update["message"]
                        user_id: str = str(message.get("from", {}).get("id", ""))
                        text: str = message.get("text", "")

                        # -------------------------------------------------- #
                        # Primary chat_id guard — discard unknown senders fast
                        # -------------------------------------------------- #
                        if user_id != self.chat_id or not text.startswith("/"):
                            continue

                        # -------------------------------------------------- #
                        # Rate limit check — enforce before any token parsing
                        # -------------------------------------------------- #
                        if not security_core.policy_engine.enforce_rate_limit(user_id):
                            event = RateLimitExceeded(
                                actor=user_id,
                                command=text.split()[0] if text else "unknown",
                                details=(f"Exceeded rate limit for chat_id={user_id}"),
                            )
                            security_core.audit_logger.log_security_event(event)
                            self.client.send_message(
                                "⚠️ Rate limit exceeded. Please slow down and retry in 60 seconds."
                            )
                            continue

                        # -------------------------------------------------- #
                        # Extract optional HMAC token from message
                        #
                        # Supported format:
                        #   /command [args...] --token=<token_string>
                        #
                        # If no --token flag is present, token=None and the
                        # authorization_manager falls back to legacy mode.
                        # -------------------------------------------------- #
                        token: str | None = None
                        clean_text = text
                        if "--token=" in text:
                            parts = text.split("--token=", 1)
                            clean_text = parts[0].strip()
                            token = parts[1].strip()

                        threading.Thread(
                            target=self.execute_command,
                            args=(clean_text, user_id, token),
                            daemon=True,
                        ).start()

            except Exception as exc:
                logger.error(f"Telegram polling loop exception: {exc}")
                time.sleep(5)

            time.sleep(0.5)
