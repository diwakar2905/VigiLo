# config/backup.py
import os
import shutil
import hashlib
import json
from logs.logger import logger


class ConfigBackupManager:
    def __init__(self, config_path: str, max_backups: int = 5):
        self.config_path = config_path
        self.max_backups = max_backups
        self.dir_name = os.path.dirname(os.path.abspath(config_path))

    def get_backup_path(self, index: int) -> str:
        """Returns the path for a given backup index (1-indexed)."""
        return f"{self.config_path}.bak.{index}"

    def get_backup_metadata_path(self, index: int) -> str:
        """Returns the path for the metadata manifest of a backup index."""
        return f"{self.config_path}.bak.{index}.meta"

    def calculate_sha256(self, filepath: str) -> str:
        """Calculates the SHA-256 checksum of a file."""
        if not os.path.exists(filepath):
            return ""
        h = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                while chunk := f.read(8192):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return ""

    def create_backup(self) -> bool:
        """Creates an atomic backup of the current configuration file and shifts existing backups."""
        if not os.path.exists(self.config_path):
            return False

        try:
            current_hash = self.calculate_sha256(self.config_path)
            if not current_hash:
                return False

            # Verify current file is valid JSON before backing up (no corrupted propagation)
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    json.load(f)
            except Exception as je:
                logger.error(
                    f"BackupManager: Current config is malformed JSON ({je}). Skipping backup."
                )
                return False

            # Shift existing backups back (e.g. 4 -> 5, 3 -> 4, etc.)
            for i in range(self.max_backups - 1, 0, -1):
                src_file = self.get_backup_path(i)
                src_meta = self.get_backup_metadata_path(i)
                dest_file = self.get_backup_path(i + 1)
                dest_meta = self.get_backup_metadata_path(i + 1)

                if os.path.exists(src_file):
                    shutil.move(src_file, dest_file)
                if os.path.exists(src_meta):
                    shutil.move(src_meta, dest_meta)

            # Copy current config to index 1 backup path atomically
            target_path = self.get_backup_path(1)
            target_meta_path = self.get_backup_metadata_path(1)

            shutil.copy2(self.config_path, target_path)

            # Write metadata manifest
            meta_data = {
                "version": 1,
                "sha256": current_hash,
                "timestamp": os.path.getmtime(self.config_path),
            }
            with open(target_meta_path, "w", encoding="utf-8") as mf:
                json.dump(meta_data, mf, indent=4)

            logger.info(
                "BackupManager: Successfully created rolling configuration backup."
            )
            return True
        except Exception as e:
            logger.error(f"BackupManager: Backup failed: {e}")
            return False

    def restore_latest_valid_backup(self) -> bool:
        """Finds the newest valid backup file and restores it to the active configuration path."""
        for i in range(1, self.max_backups + 1):
            backup_path = self.get_backup_path(i)
            meta_path = self.get_backup_metadata_path(i)

            if not os.path.exists(backup_path) or not os.path.exists(meta_path):
                continue

            try:
                # 1. Read metadata
                with open(meta_path, "r", encoding="utf-8") as mf:
                    meta = json.load(mf)
                expected_hash = meta.get("sha256", "")

                # 2. Verify SHA-256 integrity signature
                actual_hash = self.calculate_sha256(backup_path)
                if actual_hash != expected_hash:
                    logger.warning(
                        f"BackupManager: Backup index {i} integrity verification failed. Skipping."
                    )
                    continue

                # 3. Verify JSON parsing checks
                with open(backup_path, "r", encoding="utf-8") as f:
                    json.load(f)

                # 4. Perform atomic swap to main configuration path
                os.replace(backup_path, self.config_path)
                # Cleanup metadata file since the backup has been promoted
                try:
                    os.remove(meta_path)
                except Exception:
                    pass

                logger.info(
                    f"BackupManager: Successfully restored config from backup index {i}."
                )
                return True
            except Exception as e:
                logger.error(
                    f"BackupManager: Verification failed on backup index {i}: {e}"
                )

        logger.critical("BackupManager: No valid backups found to restore.")
        return False
