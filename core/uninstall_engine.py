# core/uninstall_engine.py
import os
import shutil
import subprocess
import time
from logs.logger import logger
from services.persistence import PersistenceService
from utils.system import get_captures_dir


class UninstallEngine:
    def __init__(
        self, install_dir=r"C:\Program Files\VigiLo", executable_name="VigiLo.exe"
    ):
        self.install_dir = install_dir
        self.exe_name = executable_name
        self.exe_path = os.path.join(self.install_dir, self.exe_name)

    def uninstall(self, progress_callback=None, log_callback=None):
        """Executes the uninstallation cleanup sequence: terminates tasks, deletes registry keys and directories."""

        def report(msg, progress):
            logger.info(msg)
            if log_callback:
                log_callback(msg)
            if progress_callback:
                progress_callback(progress)

        try:
            # 1. Stop running processes
            report("Stopping running VigiLo processes...", 20)
            subprocess.run(
                ["taskkill", "/F", "/IM", self.exe_name],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            time.sleep(0.5)

            # 2. Unregister persistence methods
            report("Removing scheduled tasks & registry keys...", 50)
            persistence = PersistenceService(self.exe_path)
            persistence.unregister_tasks()
            persistence.remove_registry_startup()
            time.sleep(0.5)

            # 3. Clean installation folder
            report("Deleting installation directory...", 80)
            if os.path.exists(self.install_dir):
                for attempt in range(5):
                    try:
                        shutil.rmtree(self.install_dir)
                        report("Installation directory deleted successfully.", 80)
                        break
                    except Exception as e:
                        if attempt < 4:
                            report(
                                f"File locked, retrying folder deletion ({attempt+1}/5)...",
                                80,
                            )
                            time.sleep(1.0)
                        else:
                            report(
                                f"Warning: Could not completely delete {self.install_dir}: {e}",
                                80,
                            )
            else:
                report("Installation directory not found (already removed).", 80)

            # 4. Clean ProgramData capture directories
            report("Removing captured images folder from ProgramData...", 95)
            captures = get_captures_dir()
            if os.path.exists(captures):
                try:
                    shutil.rmtree(captures, ignore_errors=True)
                    report("Captures directory deleted.", 95)
                except Exception as e:
                    report(f"Warning: Could not delete captures folder: {e}", 95)

            report("Uninstallation complete!", 100)
            return True

        except Exception as e:
            report(f"CRITICAL ERROR: Uninstallation failed: {e}", 100)
            logger.error(f"Uninstallation engine failure: {e}")
            return False
