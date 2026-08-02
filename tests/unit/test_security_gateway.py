import os
import time
import pytest
from src.core.controllers.container import ServiceContainer
from src.core.security.capability_registry import CapabilityRegistry, CapabilityDescriptor
from src.core.security.security_gateway import SecurityGateway, SecurityGatewayRequest, SecurityGatewayResponse
from src.core.services.feature_flag_service import FeatureFlagService

class TestSecurityGateway:
    def test_capability_registry_lookups(self):
        registry = CapabilityRegistry()
        registry.initialize()

        cap_cam = registry.get_capability("CAP_CAMERA")
        assert cap_cam is not None
        assert cap_cam.danger_level == "MEDIUM"

        cap_lock = registry.get_capability("CAP_LOCK")
        assert cap_lock is not None
        assert cap_lock.danger_level == "CRITICAL"
        assert len(registry.list_capabilities()) >= 12

    def test_feature_flag_service_and_env_overrides(self):
        flags = FeatureFlagService()
        flags.initialize()

        assert flags.is_enabled("timeline") is True
        assert flags.is_enabled("experimental_ai") is False

        # Environment variable override test
        os.environ["VIGILO_FLAG_EXPERIMENTAL_AI"] = "1"
        assert flags.is_enabled("experimental_ai") is True
        del os.environ["VIGILO_FLAG_EXPERIMENTAL_AI"]

    def test_security_gateway_execution_pipeline(self):
        container = ServiceContainer.get_instance()
        gw = container.security_gateway

        executed = []
        def mock_handler():
            executed.append(True)
            return "SUCCESS"

        req = SecurityGatewayRequest(
            capability_id="CAP_LOCK",
            action_name="lock_device",
            caller_id="UI",
            handler=mock_handler
        )

        start = time.time()
        resp = gw.execute_privileged_operation(req)
        elapsed_ms = (time.time() - start) * 1000

        assert resp.success is True
        assert resp.correlation_id.startswith("COR-")
        assert resp.decision == "GRANTED"
        assert resp.result == "SUCCESS"
        assert len(executed) == 1

        # Authorization Latency Target < 5 ms
        assert elapsed_ms < 5.0

    def test_security_gateway_unauthorized_caller_rejection(self):
        container = ServiceContainer.get_instance()
        gw = container.security_gateway

        req = SecurityGatewayRequest(
            capability_id="CAP_LOCK",
            action_name="lock_workstation",
            caller_id="UNAUTHORIZED_HACKER_CALLER",
            handler=lambda: "HACK"
        )

        resp = gw.execute_privileged_operation(req)
        assert resp.success is False
        assert resp.decision == "DENIED"
        assert "not authorized" in resp.failure_reason
