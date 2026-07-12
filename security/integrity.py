# security/integrity.py
import hashlib
import os
from security.interfaces import IIntegrityManager

class IntegrityManager(IIntegrityManager):
    def calculate_sha256(self, filepath: str) -> str:
        """Calculates the SHA-256 checksum of a file on disk."""
        if not os.path.exists(filepath):
            return ""
        h = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                while chunk := f.read(8192):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return ""

    def verify_file(self, filepath: str, expected_hash: str) -> bool:
        """Compares calculated file checksum against the expected signature hash."""
        actual = self.calculate_sha256(filepath)
        if not actual or not expected_hash:
            return False
        return actual.lower() == expected_hash.lower()

    def verify_system_integrity(self, file_map: dict) -> dict:
        """
        Runs validation checks on system executable binaries and configuration assets.
        Outputs structured reports and registers tamper audits.
        """
        report = {
            "status": "HEALTHY",
            "failures": []
        }
        
        # Safe import to avoid circular dependency loops
        from security.audit import HashMismatch
        from security.core import security_core
        
        for filepath, expected_hash in file_map.items():
            if not os.path.exists(filepath):
                report["status"] = "TAMPERED"
                report["failures"].append(filepath)
                event = HashMismatch(filepath, "VerifyIntegrity", "Critical resource file is missing")
                security_core.audit_logger.log_security_event(event)
                continue

            if not self.verify_file(filepath, expected_hash):
                report["status"] = "TAMPERED"
                report["failures"].append(filepath)
                event = HashMismatch(filepath, "VerifyIntegrity", "Checksum verification failed")
                security_core.audit_logger.log_security_event(event)

        return report
