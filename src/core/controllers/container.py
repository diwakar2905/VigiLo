import os
import sys

from ..repositories.device_state_repository import DeviceStateRepository
from ..repositories.timeline_repository import TimelineRepository
from ..repositories.audit_log_repository import AuditLogRepository

from ..services.audit_logger_service import AuditLoggerService
from ..services.device_state_service import DeviceStateService
from ..services.timeline_service import IncidentTimelineService
from ..services.report_generator_service import IncidentReportService
from ..services.health_monitor_service import HealthMonitorService
from ..services.trust_service import TrustService

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

        # Repositories
        state_file = os.path.join(base_data_dir, "device_state.json")
        timeline_db = os.path.join(base_data_dir, "timeline.db")
        audit_log = os.path.join(base_data_dir, "audit.log")

        self.state_repo = DeviceStateRepository(state_file)
        self.timeline_repo = TimelineRepository(timeline_db)
        self.audit_repo = AuditLogRepository(audit_log)

        # Services
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

    @classmethod
    def get_instance(cls, base_data_dir: str = None) -> 'ServiceContainer':
        if cls._instance is None:
            cls._instance = ServiceContainer(base_data_dir)
        return cls._instance
