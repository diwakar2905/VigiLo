import hashlib
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any

from .incident_event import IncidentEvent

@dataclass
class IncidentReportModel:
    report_id: str
    device_name: str
    device_id: str
    os_version: str
    generated_at: str
    timeline_events: List[IncidentEvent]
    image_hashes: Dict[str, str]  # filename -> sha256
    audit_summary_hash: str = ""

    def __post_init__(self):
        if not self.audit_summary_hash:
            self.audit_summary_hash = self.compute_summary_hash()

    def compute_summary_hash(self) -> str:
        event_hashes = "".join([e.sha256_hash for e in self.timeline_events])
        img_hashes = "".join([f"{k}:{v}" for k, v in sorted(self.image_hashes.items())])
        raw = f"{self.report_id}|{self.device_id}|{self.generated_at}|{event_hashes}|{img_hashes}"
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "report_id": self.report_id,
            "device_name": self.device_name,
            "device_id": self.device_id,
            "os_version": self.os_version,
            "generated_at": self.generated_at,
            "timeline_events": [e.to_dict() for e in self.timeline_events],
            "image_hashes": self.image_hashes,
            "audit_summary_hash": self.audit_summary_hash
        }
