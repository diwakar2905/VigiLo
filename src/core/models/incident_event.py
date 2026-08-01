import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional

@dataclass
class IncidentEvent:
    incident_id: str
    timestamp: str
    event_type: str
    severity: str  # INFO, WARNING, CRITICAL
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    sha256_hash: Optional[str] = None

    def __post_init__(self):
        if not self.sha256_hash:
            self.sha256_hash = self.compute_hash()

    def compute_hash(self) -> str:
        payload = f"{self.incident_id}|{self.timestamp}|{self.event_type}|{self.severity}|{self.description}|{json.dumps(self.metadata, sort_keys=True)}"
        return hashlib.sha256(payload.encode('utf-8')).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "severity": self.severity,
            "description": self.description,
            "metadata": self.metadata,
            "sha256_hash": self.sha256_hash
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IncidentEvent':
        return cls(
            incident_id=data["incident_id"],
            timestamp=data["timestamp"],
            event_type=data["event_type"],
            severity=data["severity"],
            description=data["description"],
            metadata=data.get("metadata", {}),
            sha256_hash=data.get("sha256_hash")
        )
