import platform
import psutil
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from src.api.v1.public_api import VigiLoPublicAPIv1
from src.core.controllers.container import ServiceContainer

@dataclass
class ServiceHealthStatusDTO:
    name: str
    status: str  # RUNNING, STOPPED, RECOVERING, WARNING, ERROR
    uptime_sec: int
    restart_count: int

@dataclass
class ControlCenterSummaryDTO:
    device_name: str
    device_id: str
    device_state: str  # DISARMED, WATCH_MODE, LOST_MODE
    protection_status: str  # PROTECTED, WARNING, CRITICAL
    last_seen: str
    last_heartbeat: str
    runtime_version: str
    config_version: str
    cpu_percent: float
    ram_used_mb: float
    disk_free_gb: float
    os_version: str
    defender_status: str
    services: List[ServiceHealthStatusDTO] = field(default_factory=list)

class DashboardService:
    """Service facade providing decoupled data to Dashboard ViewModels."""

    def __init__(self, api: Optional[VigiLoPublicAPIv1] = None):
        self.api = api or VigiLoPublicAPIv1()
        self._container = self.api._container

    def get_summary(self) -> ControlCenterSummaryDTO:
        ident = self.api.get_device_identity()
        state = self.api.get_device_state()
        health = self.api.get_system_health()

        # Protection status determination
        protection = "PROTECTED" if state in ["WATCH_MODE", "LOST_MODE"] and health == "HEALTHY" else ("WARNING" if state == "DISARMED" else "CRITICAL")

        # Hardware metrics
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().used / (1024 * 1024)
        disk = 0.0
        try:
            disk = psutil.disk_usage("C:\\").free / (1024 ** 3)
        except Exception:
            pass

        # Managed services status DTOs
        services = [
            ServiceHealthStatusDTO("Runtime Host", "RUNNING", 3600, 0),
            ServiceHealthStatusDTO("Event Monitor", "RUNNING" if state != "DISARMED" else "STOPPED", 3600, 0),
            ServiceHealthStatusDTO("Upload Queue", "RUNNING", 3600, 0),
            ServiceHealthStatusDTO("Notification Service", "RUNNING", 3600, 0),
            ServiceHealthStatusDTO("Camera Service", "READY", 3600, 0),
            ServiceHealthStatusDTO("Face Verification", "READY", 3600, 0),
            ServiceHealthStatusDTO("Vault Service", "RUNNING", 3600, 0),
            ServiceHealthStatusDTO("Audit Logger", "RUNNING", 3600, 0)
        ]

        return ControlCenterSummaryDTO(
            device_name=platform.node(),
            device_id=ident.public_id,
            device_state=state,
            protection_status=protection,
            last_seen="Just now",
            last_heartbeat="2s ago",
            runtime_version=self.api.version,
            config_version="v3.5.0",
            cpu_percent=cpu,
            ram_used_mb=round(ram, 1),
            disk_free_gb=round(disk, 1),
            os_version=f"{platform.system()} {platform.release()}",
            defender_status="ACTIVE",
            services=services
        )

    def run_diagnostics(self) -> Dict[str, Any]:
        return self.api.run_self_diagnostics()

    def execute_quick_action(self, action_id: str) -> bool:
        if action_id == "lock":
            return self._container.device_state_service.transition_to(
                self._container.device_state_service.get_current_state(), "Manual Lock", "Dashboard"
            )
        elif action_id == "report":
            return bool(self.api.generate_forensic_report())
        return True
