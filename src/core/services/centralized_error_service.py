import traceback
from typing import Dict, Any, Optional
from ..interfaces.i_service import IService
from .audit_logger_service import AuditLoggerService
from .timeline_service import IncidentTimelineService
from ..exceptions.vigi_exceptions import VigiLoBaseException, FatalException, SecurityException

class CentralizedErrorService(IService):
    def __init__(self, audit_logger: AuditLoggerService, timeline_service: IncidentTimelineService):
        self.audit_logger = audit_logger
        self.timeline_service = timeline_service
        self._initialized = False

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def shutdown(self) -> None:
        self._initialized = False

    def handle_error(self, error: Exception, context_name: str = "GENERAL", correlation_id: Optional[str] = None) -> bool:
        error_type = type(error).__name__
        message = str(error)
        stack_trace = traceback.format_exc()

        is_security = isinstance(error, SecurityException)
        is_fatal = isinstance(error, FatalException)
        severity = "CRITICAL" if (is_security or is_fatal) else "WARNING"

        details: Dict[str, Any] = {
            "error_type": error_type,
            "message": message,
            "context": context_name,
            "correlation_id": correlation_id
        }

        # 1. Audit Log Record
        self.audit_logger.log_event(
            category="EXCEPTION_HANDLED",
            action=error_type,
            actor="CentralizedErrorService",
            details=details
        )

        # 2. Timeline Event
        self.timeline_service.record_event(
            event_type="SYSTEM_ERROR",
            severity=severity,
            description=f"[{context_name}] {error_type}: {message}",
            metadata=details
        )

        print(f"[EX-LOG] [{severity}] [{context_name}] {error_type}: {message}")

        # Returns True if recoverable, False if fatal
        return not is_fatal
