import os
import hashlib
import subprocess
from dataclasses import dataclass
from typing import List, Dict
from ..interfaces.i_service import IService
from .audit_logger_service import AuditLoggerService
from .timeline_service import IncidentTimelineService

@dataclass
class TamperEvent:
    resource_type: str  # FILE, SERVICE, REGISTRY, TASK
    resource_name: str
    anomaly_description: str
    severity: str  # WARNING, CRITICAL

class TamperDetectionService(IService):
    def __init__(self, audit_logger: AuditLoggerService, timeline_service: IncidentTimelineService):
        self.audit_logger = audit_logger
        self.timeline_service = timeline_service
        self._protected_binaries: Dict[str, str] = {}  # path -> expected sha256
        self._initialized = False

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def shutdown(self) -> None:
        self._protected_binaries.clear()
        self._initialized = False

    def register_binary(self, filepath: str) -> None:
        if os.path.exists(filepath):
            self._protected_binaries[filepath] = self._compute_hash(filepath)

    def run_tamper_audit(self) -> List[TamperEvent]:
        anomalies: List[TamperEvent] = []

        # 1. Inspect protected binaries
        for fpath, expected_hash in self._protected_binaries.items():
            if not os.path.exists(fpath):
                anomalies.append(TamperEvent(
                    resource_type="FILE",
                    resource_name=os.path.basename(fpath),
                    anomaly_description=f"Missing runtime binary file: {fpath}",
                    severity="CRITICAL"
                ))
            else:
                curr_hash = self._compute_hash(fpath)
                if curr_hash != expected_hash:
                    anomalies.append(TamperEvent(
                        resource_type="FILE",
                        resource_name=os.path.basename(fpath),
                        anomaly_description=f"Binary hash mismatch (tampered file content): {fpath}",
                        severity="CRITICAL"
                    ))

        # 2. Inspect scheduled tasks (AntiTheft_Commander check)
        task_status = self._check_scheduled_task("AntiTheft_Commander")
        if task_status == "DISABLED":
            anomalies.append(TamperEvent(
                resource_type="TASK",
                resource_name="AntiTheft_Commander",
                anomaly_description="Scheduled task is disabled or removed",
                severity="WARNING"
            ))

        # Pipeline: Audit Event -> Timeline Event -> Incident Log
        for anomaly in anomalies:
            self.audit_logger.log_event(
                category="TAMPER_ALERT",
                action=f"ANOMALY_{anomaly.resource_type}",
                actor="TamperDetectionEngine",
                details={
                    "resource": anomaly.resource_name,
                    "anomaly": anomaly.anomaly_description,
                    "severity": anomaly.severity
                }
            )
            self.timeline_service.record_event(
                event_type="TAMPER_DETECTED",
                severity=anomaly.severity,
                description=f"Tamper Anomaly [{anomaly.resource_type}]: {anomaly.anomaly_description}",
                metadata={"resource": anomaly.resource_name}
            )

        return anomalies

    def _compute_hash(self, filepath: str) -> str:
        try:
            with open(filepath, "rb") as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""

    def _check_scheduled_task(self, task_name: str) -> str:
        try:
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            output = subprocess.check_output(
                ["schtasks", "/Query", "/TN", task_name, "/FO", "LIST"],
                startupinfo=si,
                encoding="utf-8",
                errors="ignore"
            )
            if "Disabled" in output:
                return "DISABLED"
            return "READY"
        except Exception:
            return "MISSING"
