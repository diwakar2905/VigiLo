import os
import shutil
import tempfile
import pytest
from src.core.controllers.container import ServiceContainer
from src.core.models.device_state import DeviceState

class TestServiceContainerIntegration:
    def setup_method(self):
        self.test_dir = tempfile.mkdtemp()
        self.container = ServiceContainer.get_instance(self.test_dir)

    def teardown_method(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_full_container_lifecycle(self):
        # 1. State service
        assert self.container.device_state_service.get_current_state() == DeviceState.WATCH_MODE
        self.container.device_state_service.transition_to(DeviceState.LOST_MODE, "Integration Test", "System")

        # 2. Timeline recording
        evt = self.container.timeline_service.record_event("LOST_MODE_ACTIVATED", "CRITICAL", "Lost mode triggered")
        assert evt.sha256_hash is not None

        # 3. Report generation
        report = self.container.report_service.generate_report()
        assert report.device_name != ""

        # 4. Audit log verification
        audit_path = os.path.join(self.test_dir, "audit.log")
        assert os.path.exists(audit_path)
        with open(audit_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "LOST_MODE_ACTIVATED" in content or "STATE_TRANSITION" in content
