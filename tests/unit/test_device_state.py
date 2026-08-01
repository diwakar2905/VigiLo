import os
import shutil
import tempfile
import pytest
from src.core.models.device_state import DeviceState, FeaturePermissionMatrix
from src.core.repositories.device_state_repository import DeviceStateRepository
from src.core.repositories.audit_log_repository import AuditLogRepository
from src.core.services.audit_logger_service import AuditLoggerService
from src.core.services.device_state_service import DeviceStateService

class TestDeviceStateMachine:
    def setup_method(self):
        self.test_dir = tempfile.mkdtemp()
        self.state_file = os.path.join(self.test_dir, "state.json")
        self.audit_file = os.path.join(self.test_dir, "audit.log")
        
        self.state_repo = DeviceStateRepository(self.state_file)
        self.audit_repo = AuditLogRepository(self.audit_file)
        self.audit_service = AuditLoggerService(self.audit_repo)
        self.audit_service.initialize()

        self.service = DeviceStateService(self.state_repo, self.audit_service)
        self.service.initialize()

    def teardown_method(self):
        shutil.rmtree(self.test_dir)

    def test_default_state_is_watch_mode(self):
        assert self.service.get_current_state() == DeviceState.WATCH_MODE

    def test_state_transitions(self):
        assert self.service.transition_to(DeviceState.DISARMED, "Testing disarm", "UnitTest") is True
        assert self.service.get_current_state() == DeviceState.DISARMED

        assert self.service.transition_to(DeviceState.LOST_MODE, "Testing lost", "UnitTest") is True
        assert self.service.get_current_state() == DeviceState.LOST_MODE

    def test_feature_permission_matrix(self):
        self.service.transition_to(DeviceState.DISARMED, "Disarming", "UnitTest")
        assert self.service.is_feature_allowed("runtime_health") is True
        assert self.service.is_feature_allowed("webcam_capture") is False
        assert self.service.is_feature_allowed("audio_record") is False

        self.service.transition_to(DeviceState.WATCH_MODE, "Watch Mode", "UnitTest")
        assert self.service.is_feature_allowed("win_login_monitor") is True
        assert self.service.is_feature_allowed("webcam_capture") is True
        assert self.service.is_feature_allowed("audio_record") is False

        self.service.transition_to(DeviceState.LOST_MODE, "Lost Mode", "UnitTest")
        assert self.service.is_feature_allowed("lock_device") is True
        assert self.service.is_feature_allowed("locate_device") is True
        assert self.service.is_feature_allowed("audio_record") is False
