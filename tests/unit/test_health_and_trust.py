import pytest
from src.core.models.health_object import HealthObject, HealthStatus
from src.core.services.health_monitor_service import HealthMonitorService
from src.core.services.trust_service import TrustService

class TestHealthAndTrust:
    def test_health_monitor_push_updates(self):
        service = HealthMonitorService()
        service.initialize()

        received = []
        service.subscribe(lambda obj: received.append(obj))

        obj = HealthObject("Camera", HealthStatus.HEALTHY, "Ready", "2026-08-01T00:00:00")
        service.update_health(obj)

        assert len(received) == 1
        assert received[0].component_name == "Camera"
        assert service.get_aggregate_health() == HealthStatus.HEALTHY

        obj_deg = HealthObject("EventLog", HealthStatus.UNHEALTHY, "Access Denied", "2026-08-01T00:00:00")
        service.update_health(obj_deg)
        assert service.get_aggregate_health() == HealthStatus.UNHEALTHY

    def test_trust_service_descriptors(self):
        service = TrustService()
        service.initialize()

        descriptors = service.get_permission_descriptors()
        assert len(descriptors) >= 4

        cam_desc = next(d for d in descriptors if d.permission_id == "webcam_capture")
        assert cam_desc.justification != ""
        assert cam_desc.privacy_impact != ""
