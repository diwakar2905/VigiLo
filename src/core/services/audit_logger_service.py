from datetime import datetime
from typing import Dict, Any
from ..interfaces.i_service import IService
from ..repositories.audit_log_repository import AuditLogRepository

class AuditLoggerService(IService):
    def __init__(self, repository: AuditLogRepository):
        self.repository = repository
        self._initialized = False

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def shutdown(self) -> None:
        self._initialized = False

    def log_event(self, category: str, action: str, actor: str, details: Dict[str, Any] = None) -> bool:
        if details is None:
            details = {}
        return self.repository.write_entry(category, action, actor, details)
