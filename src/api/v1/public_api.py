from typing import List, Dict, Any, Optional
from ...core.controllers.container import ServiceContainer
from ...core.models.device_state import DeviceState
from ...core.models.incident_event import IncidentEvent
from ...core.models.incident_report import IncidentReportModel
from ...core.models.health_object import HealthObject
from ...core.models.device_identity import DeviceIdentityModel
from ...core.services.observability_service import TelemetrySnapshot

class VigiLoPublicAPIv1:
    """Stable, versioned (v1) Public API facade for VigiLo Platform."""

    def __init__(self, container: Optional[ServiceContainer] = None):
        self._container = container or ServiceContainer.get_instance()

    @property
    def version(self) -> str:
        return "1.0.0"

    # --- Runtime & State API ---
    def get_device_state(self) -> str:
        return self._container.device_state_service.get_current_state().value

    def set_device_state(self, target_state: str, reason: str, actor: str = "API") -> bool:
        state_enum = DeviceState(target_state)
        return self._container.device_state_service.transition_to(state_enum, reason, actor)

    # --- Identity API ---
    def get_device_identity(self) -> DeviceIdentityModel:
        return self._container.identity_service.get_identity()

    # --- Timeline & Incident API ---
    def get_timeline_events(self, filter_type: Optional[str] = None, limit: int = 100) -> List[IncidentEvent]:
        return self._container.timeline_service.get_timeline(filter_type=filter_type, limit=limit)

    def record_incident(self, event_type: str, severity: str, description: str, metadata: dict = None) -> IncidentEvent:
        return self._container.timeline_service.record_event(event_type, severity, description, metadata)

    def generate_forensic_report(self) -> IncidentReportModel:
        return self._container.report_service.generate_report()

    # --- Health & Diagnostics API ---
    def get_system_health(self) -> str:
        return self._container.health_service.get_aggregate_health().value

    def run_self_diagnostics(self) -> Dict[str, Any]:
        rep = self._container.diagnostics_service.run_full_diagnostics()
        return {
            "overall_status": rep.overall_status,
            "generated_at": rep.generated_at,
            "checks": [
                {
                    "probe_id": c.probe_id,
                    "component": c.component_name,
                    "status": c.status,
                    "message": c.message
                }
                for c in rep.checks
            ]
        }

    # --- Observability API (Feature 10) ---
    def get_telemetry_snapshot(self) -> TelemetrySnapshot:
        return self._container.observability_service.get_telemetry_snapshot()
