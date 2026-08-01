import uuid
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from ..interfaces.i_service import IService
from ..models.incident_event import IncidentEvent
from ..repositories.timeline_repository import TimelineRepository
from .audit_logger_service import AuditLoggerService

class IncidentTimelineService(IService):
    def __init__(self, repository: TimelineRepository, audit_logger: AuditLoggerService):
        self.repository = repository
        self.audit_logger = audit_logger
        self._initialized = False

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def shutdown(self) -> None:
        self._initialized = False

    def record_event(self, event_type: str, severity: str, description: str, metadata: Dict[str, Any] = None) -> IncidentEvent:
        if metadata is None:
            metadata = {}
        
        event = IncidentEvent(
            incident_id=f"INC-{uuid.uuid4().hex[:8].upper()}",
            timestamp=datetime.utcnow().isoformat(),
            event_type=event_type,
            severity=severity,
            description=description,
            metadata=metadata
        )

        self.repository.add_event(event)
        self.audit_logger.log_event(
            category="TIMELINE_INCIDENT",
            action=event_type,
            actor="SYSTEM",
            details=event.to_dict()
        )
        return event

    def get_timeline(self, filter_type: Optional[str] = None, limit: int = 500) -> List[IncidentEvent]:
        return self.repository.get_events(filter_type=filter_type, limit=limit)

    def export_json(self, target_filepath: str) -> bool:
        try:
            events = self.get_timeline(limit=10000)
            data = [e.to_dict() for e in events]
            with open(target_filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to export timeline JSON: {e}")
            return False
