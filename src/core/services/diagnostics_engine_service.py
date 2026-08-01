import os
import psutil
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any
from ..interfaces.i_service import IService
from .health_monitor_service import HealthMonitorService
from .trust_service import TrustService
from .notifications.notification_service import NotificationService

@dataclass
class DiagnosticCheckResult:
    probe_id: str
    component_name: str
    status: str  # HEALTHY, WARNING, FAILED
    message: str
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DiagnosticReport:
    generated_at: str
    overall_status: str
    checks: List[DiagnosticCheckResult]

class DiagnosticsEngineService(IService):
    def __init__(
        self,
        health_service: HealthMonitorService,
        trust_service: TrustService,
        notification_service: NotificationService
    ):
        self.health_service = health_service
        self.trust_service = trust_service
        self.notification_service = notification_service
        self._initialized = False

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def shutdown(self) -> None:
        self._initialized = False

    def run_full_diagnostics(self) -> DiagnosticReport:
        checks: List[DiagnosticCheckResult] = []

        # Probe 1: Windows Admin & Privilege Probe
        is_admin = self.trust_service.is_admin()
        checks.append(DiagnosticCheckResult(
            probe_id="PRB-001",
            component_name="Windows Admin Privileges",
            status="HEALTHY" if is_admin else "WARNING",
            message="Process running with Administrator privileges" if is_admin else "Process running as standard user (Event Log monitoring limited)",
            details={"is_admin": is_admin}
        ))

        # Probe 2: Memory & Disk Probe
        disk_info = psutil.disk_usage('C:\\')
        disk_free_gb = disk_info.free / (1024 ** 3)
        checks.append(DiagnosticCheckResult(
            probe_id="PRB-002",
            component_name="Disk Space (C:)",
            status="HEALTHY" if disk_free_gb > 1.0 else "WARNING",
            message=f"{disk_free_gb:.1f} GB available on system drive",
            details={"free_gb": disk_free_gb}
        ))

        # Probe 3: Notification Providers Health
        provider_healths = self.notification_service.check_all_providers_health()
        for p in provider_healths:
            checks.append(DiagnosticCheckResult(
                probe_id=f"PRB-NOTIF-{p.component_name}",
                component_name=f"Provider: {p.component_name}",
                status=p.status.value,
                message=p.message,
                details=p.metrics
            ))

        # Probe 4: Security Log Event Access Probe
        try:
            import win32evtlog
            handle = win32evtlog.OpenEventLog("localhost", "Security")
            win32evtlog.CloseEventLog(handle)
            checks.append(DiagnosticCheckResult(
                probe_id="PRB-004",
                component_name="Windows Security Event Log API",
                status="HEALTHY",
                message="Successfully opened Security Event Log handle (Event 4625 hook ready)",
                details={}
            ))
        except Exception as e:
            checks.append(DiagnosticCheckResult(
                probe_id="PRB-004",
                component_name="Windows Security Event Log API",
                status="FAILED",
                message=f"Failed to access Security Event Log: {e}",
                details={"error": str(e)}
            ))

        overall = "HEALTHY"
        if any(c.status == "FAILED" for c in checks):
            overall = "FAILED"
        elif any(c.status == "WARNING" for c in checks):
            overall = "WARNING"

        return DiagnosticReport(
            generated_at=datetime.utcnow().isoformat(),
            overall_status=overall,
            checks=checks
        )
