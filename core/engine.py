# core/engine.py
import os
import threading
import time
from api.telegram_client import TelegramClient
from config.manager import ConfigManager
from logs.logger import logger
from utils.system import get_captures_dir
from core.event_monitor import EventLogMonitor
from core.shutdown_listener import ShutdownListener
from services.upload_queue import UploadQueueService
from services.telegram_polling import TelegramPollingService
from modules.camera import CameraModule
from security.privilege import acquire_named_mutex
from core.runtime import ServiceManager, ThreadSupervisor


class VigiLoEngine:
    def __init__(self, config_path=None):
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.config
        self.captures_dir = get_captures_dir()

        # Instantiate Telegram Client
        self.telegram_client = TelegramClient(
            bot_token=self.config.telegram.bot_token,
            chat_id=self.config.telegram.chat_id,
        )

        # Instantiate Notification Router
        from api.notification_router import NotificationRouter

        self.notification_router = NotificationRouter(
            config=self.config,
            telegram_client=self.telegram_client,
        )

        # Re-derive the HMAC key now that we have the decrypted bot_token
        from security.core import security_core

        security_core.reinitialize_auth(self.config.telegram.bot_token)

        # Check and generate vault key if enabled and empty
        vault_enabled = getattr(self.config.vault, "enabled", False)
        vault_key = getattr(self.config.vault, "vault_key", "")
        if vault_enabled and not vault_key:
            try:
                from cryptography.fernet import Fernet

                new_key = Fernet.generate_key().decode("utf-8")

                from config.schema import AppConfig, VaultConfig

                mutable_cfg = AppConfig(
                    telegram=self.config.telegram,
                    security=self.config.security,
                    camera=self.config.camera,
                    face_verification=self.config.face_verification,
                    vault=VaultConfig(
                        enabled=self.config.vault.enabled,
                        target_dir=self.config.vault.target_dir,
                        vault_key=new_key,
                    ),
                )
                self.config_manager.save(mutable_cfg)
                self.config = self.config_manager.config
                logger.info(
                    "Automatically generated and saved a new DPAPI-encrypted vault key."
                )
            except Exception as e:
                logger.error(f"Failed to generate automatic vault key: {e}")

        # Shutdown event for thread lifecycle management
        self.stop_event = threading.Event()
        self.last_capture_time = 0
        self.capture_cooldown = 0.0  # Delay between captures in seconds
        self._service_mutex = None
        self._commander_mutex = None
        self.service_manager = ServiceManager()
        self.supervisor = ThreadSupervisor(self.service_manager)

    def capture_alert(self):
        """Callback triggered when failed login attempt threshold is reached."""
        logger.warning(
            "[ALERT] Wrong Password Threshold Reached! Triggering camera capture..."
        )
        now = time.time()
        if now - self.last_capture_time >= self.capture_cooldown:
            try:
                camera = CameraModule(device_index=self.config.camera.device_index)

                # Check if face verification is enabled and we have enrolled embeddings
                fv_enabled = getattr(self.config.face_verification, "enabled", False)
                reference_embs = getattr(
                    self.config.face_verification, "reference_embeddings", []
                )

                if fv_enabled and reference_embs:
                    # Capture with a temporary prefix first
                    filepath = camera.execute(self.captures_dir, prefix="temp_alert_")
                    if filepath:
                        from modules.face_verification import (
                            FaceVerificationModule,
                            FaceStats,
                            deserialize_embedding,
                        )

                        # Deserialize embeddings
                        refs = []
                        for raw_emb in reference_embs:
                            try:
                                refs.append(deserialize_embedding(raw_emb))
                            except Exception as ex:
                                logger.error(
                                    f"Failed to deserialize face embedding: {ex}"
                                )

                        if refs:
                            fvm = FaceVerificationModule(
                                threshold=self.config.face_verification.threshold
                            )
                            # Verify if the face matches the owner
                            if fvm.verify(filepath, refs):
                                logger.info(
                                    "[Owner Detected] Login failed but face matches enrolled owner. Suppressing alert."
                                )
                                FaceStats.record_attempt(is_owner=True)
                                try:
                                    os.remove(filepath)
                                except Exception as err:
                                    logger.error(
                                        f"Failed to delete temp alert photo: {err}"
                                    )
                            else:
                                logger.warning(
                                    "[Intruder Detected] Face did not match or no face detected. Escalating alert."
                                )
                                FaceStats.record_attempt(is_owner=False)
                                self.lock_vault()
                                # Rename to alert_ prefix so upload queue picks it up
                                dir_name = os.path.dirname(filepath)
                                base_name = os.path.basename(filepath).replace(
                                    "temp_alert_", "alert_"
                                )
                                new_filepath = os.path.join(dir_name, base_name)
                                try:
                                    os.rename(filepath, new_filepath)
                                    logger.info(
                                        f"Intruder photo saved to offline queue: {new_filepath}"
                                    )
                                except Exception as err:
                                    logger.error(f"Failed to rename alert photo: {err}")
                        else:
                            # Fallback: rename to alert_ directly
                            logger.warning(
                                "No valid face embeddings found. Falling back to threshold-only mode."
                            )
                            self.lock_vault()
                            dir_name = os.path.dirname(filepath)
                            base_name = os.path.basename(filepath).replace(
                                "temp_alert_", "alert_"
                            )
                            new_filepath = os.path.join(dir_name, base_name)
                            try:
                                os.rename(filepath, new_filepath)
                            except Exception:
                                pass
                else:
                    # 'alert_' prefix ensures the upload queue service picks it up automatically
                    filepath = camera.execute(self.captures_dir, prefix="alert_")
                    if filepath:
                        logger.info(
                            f"Intruder photo saved to offline queue: {filepath}"
                        )
                    else:
                        logger.error("Camera capture failed to write photo.")
                    self.lock_vault()
            except Exception as e:
                logger.error(f"Exception during alert camera capture: {e}")
            self.last_capture_time = now
        else:
            logger.info("Camera capture alert suppressed on cooldown.")

    def lock_vault(self):
        """Encrypts the configured vault directory contents recursively."""
        vault_enabled = getattr(self.config.vault, "enabled", False)
        vault_key = getattr(self.config.vault, "vault_key", "")
        target_dir = getattr(self.config.vault, "target_dir", "")

        if vault_enabled and vault_key and target_dir:
            logger.warning(
                f"[VAULT] Escalating alert: Locking vault directory: {target_dir}"
            )
            if not os.path.exists(target_dir):
                try:
                    os.makedirs(target_dir, exist_ok=True)
                except Exception:
                    pass
            try:
                from modules.vault import VaultModule

                vm = VaultModule(target_dir=target_dir, key=vault_key)
                if vm.lock():
                    logger.info(
                        "[VAULT] Vault folder locked and encrypted successfully."
                    )
                else:
                    logger.error(
                        "[VAULT] Vault folder encryption completed with errors."
                    )
            except Exception as exc:
                logger.error(f"[VAULT] Failed to execute vault lock: {exc}")

    def send_shutdown_alert(self):
        """Direct alert notification sent to Telegram and WhatsApp when Windows is shutting down."""
        logger.warning("[SHUTDOWN] System shutdown detected. Alerting user...")
        # Direct synchronous upload since the system is shutting down immediately
        self.notification_router.send_message(
            "⚠️ System Shutdown Detected! VigiLo is stopping."
        )

    def run_service(self):
        """Starts the background event monitoring service (SYSTEM context)."""
        logger.info("=== VigiLo Running in SERVICE Mode ===")

        # 0. Single-Instance Mutex Guard
        self._service_mutex = acquire_named_mutex("Global\\VigiLoServiceMutex")
        if not self._service_mutex:
            logger.warning(
                "[SYSTEM] VigiLo Service is already running! Exiting duplicate process."
            )
            return

        # 1. Instantiate Services
        self.event_monitor = EventLogMonitor(
            event_id=self.config.security.event_id,
            threshold=self.config.security.failed_attempt_threshold,
            check_interval=self.config.security.check_interval_seconds,
            callback=self.capture_alert,
        )

        self.upload_queue = UploadQueueService(
            notification_client=self.notification_router,
            captures_dir=self.captures_dir,
            interval=10,
        )

        self.shutdown_listener = ShutdownListener(callback=self.send_shutdown_alert)

        # 2. Register Services in ServiceManager
        self.service_manager.register_service("EventLogMonitor", self.event_monitor)
        self.service_manager.register_service("UploadQueueService", self.upload_queue)
        self.service_manager.register_service(
            "ShutdownListener", self.shutdown_listener
        )

        # 3. Initialize and Start Services
        if not self.service_manager.initialize_all():
            logger.critical(
                "Runtime: Service initialization sequence failed. Aborting service launch."
            )
            return

        self.service_manager.start_all()

        # 4. Start Thread Supervisor Watchdog
        self.supervisor.start()

        # Keep main thread alive
        try:
            while not self.stop_event.is_set():
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            logger.info("KeyboardInterrupt or SystemExit. Stopping service engine...")
            self.stop_event.set()
        finally:
            self.supervisor.stop()
            self.service_manager.stop_all()

    def run_commander(self):
        """Starts the interactive Telegram Polling Commander (USER context)."""
        logger.info("=== VigiLo Running in COMMANDER Mode ===")

        # 0. Single-Instance Mutex Guard
        self._commander_mutex = acquire_named_mutex("Local\\VigiLoCommanderMutex")
        if not self._commander_mutex:
            logger.warning(
                "[SYSTEM] VigiLo Commander is already running! Exiting duplicate process."
            )
            return

        self.polling_service = TelegramPollingService(
            telegram_client=self.telegram_client,
            app_config=self.config,
            captures_dir=self.captures_dir,
        )

        try:
            self.polling_service.start(self.stop_event)
        except (KeyboardInterrupt, SystemExit):
            logger.info(
                "KeyboardInterrupt or SystemExit. Stopping commander polling..."
            )
            self.stop_event.set()
