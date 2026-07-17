# security/audit.py
import logging
import os
import json
import threading
from logging.handlers import RotatingFileHandler
from security.interfaces import IAuditLogger
from security.context import SecurityContext
from utils.system import get_base_dir


# Thread-safe counter for AUD-XXXXXX sequence IDs
class AuditSequenceCounter:
    def __init__(self, sequence_file_path=None):
        self._lock = threading.Lock()
        self._current_id = 0
        self.sequence_file = (
            sequence_file_path
            if sequence_file_path
            else os.path.join(get_base_dir(), "logs", "audit_sequence.txt")
        )
        self._load()

    def _load(self):
        if os.path.exists(self.sequence_file):
            try:
                with open(self.sequence_file, "r") as f:
                    self._current_id = int(f.read().strip())
            except Exception:
                self._current_id = 0

    def _save(self):
        try:
            dir_name = os.path.dirname(self.sequence_file)
            os.makedirs(dir_name, exist_ok=True)
            with open(self.sequence_file, "w") as f:
                f.write(str(self._current_id))
        except Exception:
            pass

    def next_id(self) -> str:
        with self._lock:
            self._current_id += 1
            self._save()
            return f"AUD-{self._current_id:06d}"


# Global counter instance
audit_counter = AuditSequenceCounter()


# Structured Security Event classes
class SecurityEvent:
    def __init__(
        self,
        event_type: str,
        actor: str,
        action: str,
        status: str,
        details: str = "",
        context: dict = None,
    ):
        self.event_id = audit_counter.next_id()
        self.event_type = event_type
        self.actor = actor
        self.action = action
        self.status = status
        self.details = details
        self.context = context if context else {}

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "actor": self.actor,
            "action": self.action,
            "status": self.status,
            "details": self.details,
            "context": self.context,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class PermissionDenied(SecurityEvent):
    def __init__(
        self, actor: str, action: str, details: str = "", context: dict = None
    ):
        super().__init__("PermissionDenied", actor, action, "DENIED", details, context)


class HashMismatch(SecurityEvent):
    def __init__(
        self, filepath: str, action: str, details: str = "", context: dict = None
    ):
        super().__init__(
            "HashMismatch",
            "System",
            action,
            "FAILED",
            f"File: {filepath} | {details}",
            context,
        )


class DecryptFailure(SecurityEvent):
    def __init__(
        self, actor: str, action: str, details: str = "", context: dict = None
    ):
        super().__init__("DecryptFailure", actor, action, "FAILED", details, context)


class UnauthorizedCommand(SecurityEvent):
    def __init__(
        self, actor: str, command: str, details: str = "", context: dict = None
    ):
        super().__init__(
            "UnauthorizedCommand",
            actor,
            f"Execute: {command}",
            "DENIED",
            details,
            context,
        )


class ConfigTampered(SecurityEvent):
    def __init__(self, filepath: str, details: str = "", context: dict = None):
        super().__init__(
            "ConfigTampered",
            "System",
            "ValidateConfig",
            "FAILED",
            f"Config: {filepath} | {details}",
            context,
        )


class RateLimitExceeded(SecurityEvent):
    def __init__(
        self, actor: str, command: str, details: str = "", context: dict = None
    ):
        super().__init__(
            "RateLimitExceeded",
            actor,
            f"Execute: {command}",
            "BLOCKED",
            details,
            context,
        )


class AuditLogger(IAuditLogger):
    def __init__(self, log_filename="audit.log"):
        self.logger = logging.getLogger("VigiLo_Audit")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            formatter = logging.Formatter("%(asctime)s - %(message)s")
            log_dir = os.path.join(get_base_dir(), "logs")
            os.makedirs(log_dir, exist_ok=True)

            log_path = os.path.join(log_dir, log_filename)
            try:
                file_handler = RotatingFileHandler(
                    log_path, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
                )
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
            except Exception:
                pass

    def log_event(
        self, event_type: str, actor: str, action: str, status: str, details: str = ""
    ):
        """Backward compatible audit log logger, automatically maps to structured events."""
        context = SecurityContext.capture(action, "LegacyModule", status)
        event = SecurityEvent(event_type, actor, action, status, details, context)
        self.logger.info(event.to_json())

    def log_security_event(self, event: SecurityEvent):
        """Records a structured SecurityEvent object."""
        self.logger.info(event.to_json())
