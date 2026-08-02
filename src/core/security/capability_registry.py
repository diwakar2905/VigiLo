from dataclasses import dataclass, field
from typing import Dict, List, Optional
from ..interfaces.i_service import IService

@dataclass
class CapabilityDescriptor:
    capability_id: str
    version: str
    required_device_state: str  # DISARMED, WATCH_MODE, LOST_MODE
    required_permission: str
    required_policy: str
    audit_required: bool
    danger_level: str           # LOW, MEDIUM, HIGH, CRITICAL
    allowed_callers: List[str]
    health_status: str          # HEALTHY, DEGRADED, UNHEALTHY

class CapabilityRegistry(IService):
    """Centralized single source of truth for all platform capabilities."""

    def __init__(self):
        self._capabilities: Dict[str, CapabilityDescriptor] = {}
        self._initialized = False

    def initialize(self) -> bool:
        self._register_default_capabilities()
        self._initialized = True
        return True

    def shutdown(self) -> None:
        self._capabilities.clear()
        self._initialized = False

    def _register_default_capabilities(self):
        defaults = [
            CapabilityDescriptor("CAP_CAMERA", "1.0", "WATCH_MODE", "webcam_capture", "camera_policy", True, "MEDIUM", ["UI", "Commander", "Service"], "HEALTHY"),
            CapabilityDescriptor("CAP_SCREENSHOT", "1.0", "LOST_MODE", "screenshot", "screenshot_policy", True, "HIGH", ["UI", "Commander", "Service"], "HEALTHY"),
            CapabilityDescriptor("CAP_AUDIO", "1.0", "LOST_MODE", "evidence_collection", "audio_policy", True, "HIGH", ["UI", "Commander", "Service"], "HEALTHY"),
            CapabilityDescriptor("CAP_LOCK", "1.0", "LOST_MODE", "lock_device", "lock_policy", True, "CRITICAL", ["UI", "Commander", "Service"], "HEALTHY"),
            CapabilityDescriptor("CAP_RECOVERY", "1.0", "LOST_MODE", "recovery_wizard", "recovery_policy", True, "CRITICAL", ["UI", "Wizard", "Commander"], "HEALTHY"),
            CapabilityDescriptor("CAP_TIMELINE", "1.0", "DISARMED", "view_timeline", "timeline_policy", False, "LOW", ["UI", "API", "Plugin"], "HEALTHY"),
            CapabilityDescriptor("CAP_NOTIFICATION", "1.0", "DISARMED", "notification", "notification_policy", True, "LOW", ["Service", "Plugin"], "HEALTHY"),
            CapabilityDescriptor("CAP_LOCATION", "1.0", "LOST_MODE", "locate_device", "location_policy", True, "HIGH", ["UI", "Commander"], "HEALTHY"),
            CapabilityDescriptor("CAP_VAULT", "1.0", "DISARMED", "configuration", "vault_policy", True, "HIGH", ["Service"], "HEALTHY"),
            CapabilityDescriptor("CAP_PLUGIN", "1.0", "DISARMED", "configuration", "plugin_policy", True, "HIGH", ["UI", "Manager"], "HEALTHY"),
            CapabilityDescriptor("CAP_WEBHOOK", "1.0", "DISARMED", "notification", "webhook_policy", True, "LOW", ["Service"], "HEALTHY"),
            CapabilityDescriptor("CAP_DIAGNOSTICS", "1.0", "DISARMED", "runtime_health", "diagnostics_policy", False, "LOW", ["UI", "CLI", "Plugin"], "HEALTHY")
        ]
        for cap in defaults:
            self._capabilities[cap.capability_id] = cap

    def get_capability(self, capability_id: str) -> Optional[CapabilityDescriptor]:
        return self._capabilities.get(capability_id)

    def list_capabilities(self) -> List[CapabilityDescriptor]:
        return list(self._capabilities.values())
