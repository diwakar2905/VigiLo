import os
import shutil
import tempfile
import time
import pytest

from src.core.models.correlation_context import CorrelationContext
from src.core.exceptions.vigi_exceptions import SecurityException, ReplayAttackDetectedException, ConfigurationException
from src.core.services.notifications import NotificationService, NotificationMessage, TelegramNotificationProvider, WebhookNotificationProvider
from src.core.repositories.device_identity_repository import DeviceIdentityRepository
from src.core.services.device_identity_service import DeviceIdentityService
from src.core.services.secure_pairing_service import SecurePairingService
from src.core.services.permission_engine_service import PermissionEngineService, PermissionRequirement, PermissionContext
from src.core.services.security_policy_service import SecurityPolicyService
from src.core.services.command_authorization_service import CommandAuthorizationService, CommandRequest
from src.core.services.observability_service import ObservabilityService
from src.core.services.release_hardening_service import ReleaseHardeningService

class TestPhase5Hardening:
    def setup_method(self):
        self.test_dir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_notification_abstraction_and_priority(self):
        svc = NotificationService()
        svc.initialize()

        p1 = WebhookNotificationProvider("http://localhost/test", priority_level=2)
        p2 = TelegramNotificationProvider("token", "123", priority_level=1)

        svc.register_provider(p1)
        svc.register_provider(p2)

        sorted_provs = svc.get_providers_sorted()
        assert sorted_provs[0].provider_id == "telegram"
        assert sorted_provs[1].provider_id == "webhook"

    def test_device_identity_platform(self):
        repo_file = os.path.join(self.test_dir, "identity.dat")
        repo = DeviceIdentityRepository(repo_file)
        svc = DeviceIdentityService(repo)
        svc.initialize()

        identity1 = svc.get_identity()
        assert identity1.public_id.startswith("VIGI-")
        assert len(identity1.fingerprint) == 64

        # Reboot test: Reload from repository
        svc2 = DeviceIdentityService(repo)
        svc2.initialize()
        identity2 = svc2.get_identity()

        assert identity1.device_uuid == identity2.device_uuid
        assert identity1.public_id == identity2.public_id

    def test_secure_pairing_challenge(self):
        repo_file = os.path.join(self.test_dir, "identity.dat")
        repo = DeviceIdentityRepository(repo_file)
        ident_svc = DeviceIdentityService(repo)
        ident_svc.initialize()

        pairing_svc = SecurePairingService(ident_svc)
        pairing_svc.initialize()

        challenge = pairing_svc.initiate_pairing("TestClient")
        assert "challenge_id" in challenge
        assert pairing_svc.is_channel_paired("TestClient") is False

    def test_command_authorization_replay_protection(self):
        # Mock dependencies
        class MockStateSvc:
            def get_current_state(self):
                from src.core.models.device_state import DeviceState
                return DeviceState.WATCH_MODE
            def is_feature_allowed(self, f): return True

        class MockAuditLogger:
            def log_event(self, **kw): pass

        state_svc = MockStateSvc()
        audit_logger = MockAuditLogger()

        perm_engine = PermissionEngineService(state_svc, audit_logger)
        perm_engine.initialize()

        policy_file = os.path.join(self.test_dir, "policies.json")
        policy_svc = SecurityPolicyService(policy_file)
        policy_svc.initialize()

        cmd_auth = CommandAuthorizationService(perm_engine, policy_svc, max_skew_seconds=10)
        cmd_auth.initialize()

        req1 = CommandRequest("/mode", "User1", timestamp=time.time(), nonce="nonce-123")
        ctx = cmd_auth.authorize_command(req1)
        assert ctx.correlation_id.startswith("COR-")

        # Duplicate nonce test
        with pytest.raises(ReplayAttackDetectedException):
            cmd_auth.authorize_command(req1)

    def test_observability_telemetry_snapshot(self):
        obs = ObservabilityService()
        obs.initialize()

        obs.record_failure()
        obs.set_queue_size(5)
        snap = obs.get_telemetry_snapshot()

        assert snap.failure_count == 1
        assert snap.queue_size == 5
        assert snap.ram_used_mb > 0

    def test_release_hardening_migrations(self):
        meta_file = os.path.join(self.test_dir, "release.json")
        svc = ReleaseHardeningService(meta_file)
        svc.initialize()

        cfg = {"version": "3.0.0"}
        migrated = svc.run_migrations_if_needed(cfg)
        assert migrated["version"] == "3.5.0"
        assert migrated["platform_hardening"]["identity_enabled"] is True

        with pytest.raises(ConfigurationException):
            svc.run_migrations_if_needed({"version": "2.0.0"})
