import os
import sys

from ..repositories.device_state_repository import DeviceStateRepository
from ..repositories.timeline_repository import TimelineRepository
from ..repositories.audit_log_repository import AuditLogRepository
from ..repositories.device_identity_repository import DeviceIdentityRepository

from ..services.audit_logger_service import AuditLoggerService
from ..services.device_state_service import DeviceStateService
from ..services.timeline_service import IncidentTimelineService
from ..services.report_generator_service import IncidentReportService
from ..services.health_monitor_service import HealthMonitorService
from ..services.trust_service import TrustService

from ..services.notifications.notification_service import NotificationService
from ..services.notifications.telegram_provider import TelegramNotificationProvider
from ..services.notifications.webhook_provider import WebhookNotificationProvider
from ..services.device_identity_service import DeviceIdentityService
from ..services.secure_pairing_service import SecurePairingService
from ..services.tamper_detection_service import TamperDetectionService
from ..services.permission_engine_service import PermissionEngineService
from ..services.security_policy_service import SecurityPolicyService
from ..services.command_authorization_service import CommandAuthorizationService
from ..services.observability_service import ObservabilityService
from ..services.diagnostics_engine_service import DiagnosticsEngineService
from ..services.centralized_error_service import CentralizedErrorService
from ..services.release_hardening_service import ReleaseHardeningService

class ServiceContainer:
    _instance = None

    def __init__(self, base_data_dir: str = None):
        if base_data_dir is None:
            data_dir = os.getenv("PROGRAMDATA") or "C:\\ProgramData"
            base_data_dir = os.path.join(data_dir, "VigiLo")
            
        os.makedirs(base_data_dir, exist_ok=True)
        self.base_data_dir = base_data_dir
        self.captures_dir = os.path.join(base_data_dir, "AntiTheftCaptures")
        os.makedirs(self.captures_dir, exist_ok=True)

        # File paths
        state_file = os.path.join(base_data_dir, "device_state.json")
        timeline_db = os.path.join(base_data_dir, "timeline.db")
        audit_log = os.path.join(base_data_dir, "audit.log")
        identity_file = os.path.join(base_data_dir, "identity.dat")
        policy_file = os.path.join(base_data_dir, "policies.json")
        metadata_file = os.path.join(base_data_dir, "release_metadata.json")

        # Repositories
        self.state_repo = DeviceStateRepository(state_file)
        self.timeline_repo = TimelineRepository(timeline_db)
        self.audit_repo = AuditLogRepository(audit_log)
        self.identity_repo = DeviceIdentityRepository(identity_file)

        # Services - Core
        self.audit_logger = AuditLoggerService(self.audit_repo)
        self.audit_logger.initialize()

        self.device_state_service = DeviceStateService(self.state_repo, self.audit_logger)
        self.device_state_service.initialize()

        self.timeline_service = IncidentTimelineService(self.timeline_repo, self.audit_logger)
        self.timeline_service.initialize()

        self.report_service = IncidentReportService(self.timeline_service, self.captures_dir)
        self.report_service.initialize()

        self.health_service = HealthMonitorService()
        self.health_service.initialize()

        self.trust_service = TrustService()
        self.trust_service.initialize()

        # Services - Phase 5 Hardening
        self.notification_service = NotificationService()
        self.notification_service.initialize()

        self.identity_service = DeviceIdentityService(self.identity_repo)
        self.identity_service.initialize()

        self.pairing_service = SecurePairingService(self.identity_service)
        self.pairing_service.initialize()

        self.tamper_service = TamperDetectionService(self.audit_logger, self.timeline_service)
        self.tamper_service.initialize()

        self.permission_engine = PermissionEngineService(self.device_state_service, self.audit_logger)
        self.permission_engine.initialize()

        self.security_policy_service = SecurityPolicyService(policy_file)
        self.security_policy_service.initialize()

        self.command_auth_service = CommandAuthorizationService(self.permission_engine, self.security_policy_service)
        self.command_auth_service.initialize()

        self.observability_service = ObservabilityService()
        self.observability_service.initialize()

        self.diagnostics_service = DiagnosticsEngineService(self.health_service, self.trust_service, self.notification_service)
        self.diagnostics_service.initialize()

        self.error_service = CentralizedErrorService(self.audit_logger, self.timeline_service)
        self.error_service.initialize()

        self.release_service = ReleaseHardeningService(metadata_file)
        self.release_service.initialize()

    @classmethod
    def get_instance(cls, base_data_dir: str = None) -> 'ServiceContainer':
        if cls._instance is None or (base_data_dir is not None and cls._instance.base_data_dir != base_data_dir):
            cls._instance = ServiceContainer(base_data_dir)
        return cls._instance
