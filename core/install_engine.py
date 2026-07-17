# core/install_engine.py
import json
import os
import shutil
import subprocess
from logs.logger import logger
from services.persistence import PersistenceService


class InstallEngine:
    def __init__(
        self, install_dir=r"C:\Program Files\VigiLo", executable_name="VigiLo.exe"
    ):
        self.install_dir = install_dir
        self.exe_name = executable_name
        self.dest_exe = os.path.join(self.install_dir, self.exe_name)
        self.dest_config = os.path.join(self.install_dir, "config.json")
        self.dest_uninstall = os.path.join(self.install_dir, "uninstall.exe")

    def deploy(
        self,
        src_exe,
        src_uninstall,
        telegram_config,
        progress_callback=None,
        log_callback=None,
    ):
        """Runs the installation sequence: makes directories, copies binaries, sets configuration, schedules tasks."""

        def report(msg, progress):
            logger.info(msg)
            if log_callback:
                log_callback(msg)
            if progress_callback:
                progress_callback(progress)

        try:
            # 1. Create installation directory
            report(f"Creating installation folder at: {self.install_dir}", 10)
            if not os.path.exists(self.install_dir):
                os.makedirs(self.install_dir)

            # 2. Harden folder permissions (DACLs)
            report("Securing installation folder permissions...", 15)
            try:
                cmd_acl = [
                    "icacls",
                    self.install_dir,
                    "/inheritance:r",
                    "/grant:r",
                    "NT AUTHORITY\\SYSTEM:(OI)(CI)(F)",
                    "/grant:r",
                    "BUILTIN\\Administrators:(OI)(CI)(F)",
                    "/grant:r",
                    "BUILTIN\\Users:(OI)(CI)(RX)",
                ]
                subprocess.run(
                    cmd_acl,
                    check=True,
                    capture_output=True,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                report("DACL permission hardening successful.", 18)
            except Exception as acl_err:
                report(f"Warning: Folder DACL configuration warning: {acl_err}", 18)

            # 3. Copy VigiLo service binary
            report(f"Copying service executable to {self.dest_exe}...", 30)
            if not os.path.exists(src_exe):
                raise FileNotFoundError(
                    f"Source payload executable not found: {src_exe}"
                )
            shutil.copy2(src_exe, self.dest_exe)

            # 4. Copy Uninstaller binary
            report(f"Copying uninstaller binary to {self.dest_uninstall}...", 50)
            if src_uninstall and os.path.exists(src_uninstall):
                shutil.copy2(src_uninstall, self.dest_uninstall)
            else:
                report(
                    "Warning: uninstaller source payload not found. Skipping uninstaller deployment.",
                    50,
                )

            # 5. Generate runtime configuration
            report("Generating config.json details...", 65)
            full_config = {
                "telegram": telegram_config,
                "security": {
                    "failed_attempt_threshold": 2,
                    "event_id": 4625,
                    "check_interval_seconds": 0.1,
                },
                "camera": {"device_index": 0},
            }
            with open(self.dest_config, "w", encoding="utf-8") as f:
                json.dump(full_config, f, indent=4)

            # Encrypt credentials in config immediately after creation
            from config.manager import ConfigManager
            from config.schema import (
                TelegramConfig,
                AppConfig,
                SecurityConfig,
                CameraConfig,
                FaceVerificationConfig,
            )

            mgr = ConfigManager(self.dest_config)
            fv_dict = telegram_config.get("face_verification", {})
            app_cfg = AppConfig(
                telegram=TelegramConfig(
                    telegram_config.get("bot_token"), telegram_config.get("chat_id")
                ),
                security=SecurityConfig(),
                camera=CameraConfig(),
                face_verification=FaceVerificationConfig(
                    enabled=fv_dict.get("enabled", False),
                    threshold=fv_dict.get("threshold", 0.363),
                    reference_embeddings=fv_dict.get("reference_embeddings", []),
                ),
            )
            mgr.save(app_cfg)

            # 6. Clean legacy components
            report("Stopping running service processes...", 75)
            subprocess.run(
                ["taskkill", "/F", "/IM", self.exe_name],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )

            # 7. Schedule tasks
            persistence = PersistenceService(self.dest_exe)
            report("Registering scheduled tasks...", 85)
            if not persistence.register_tasks():
                raise RuntimeError("Failed to register scheduled tasks.")

            persistence.add_registry_startup()

            # 8. Start tasks
            report("Starting background tasks...", 95)
            subprocess.run(
                ["schtasks", "/Run", "/TN", "VigiLo_Service"],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            subprocess.run(
                ["schtasks", "/Run", "/TN", "VigiLo_Commander"],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )

            report("Installation completed successfully!", 100)
            return True

        except Exception as e:
            report(f"CRITICAL ERROR: Installation failed: {e}", 100)
            logger.error(f"Installation engine failure: {e}")
            return False
