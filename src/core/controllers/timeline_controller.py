from typing import List, Optional
from ..models.incident_event import IncidentEvent
from ..services.timeline_service import IncidentTimelineService

class TimelineController:
    def __init__(self, service: IncidentTimelineService):
        self.service = service

    def record_incident(self, event_type: str, severity: str, description: str, metadata: dict = None) -> IncidentEvent:
        return self.service.record_event(event_type, severity, description, metadata)

    def get_events(self, filter_type: Optional[str] = None, limit: int = 500) -> List[IncidentEvent]:
        return self.service.get_timeline(filter_type, limit)

    def export_json(self, filepath: str) -> bool:
        return self.service.export_json(filepath)
