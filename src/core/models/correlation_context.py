import uuid
from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class CorrelationContext:
    correlation_id: str = field(default_factory=lambda: f"COR-{uuid.uuid4().hex[:8].upper()}")
    trace_id: str = field(default_factory=lambda: f"TRC-{uuid.uuid4().hex[:12].lower()}")
    audit_id: str = field(default_factory=lambda: f"AUD-{uuid.uuid4().hex[:8].upper()}")
    incident_id: str = field(default_factory=lambda: f"INC-{uuid.uuid4().hex[:8].upper()}")
    log_id: str = field(default_factory=lambda: f"LOG-{uuid.uuid4().hex[:8].upper()}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "correlation_id": self.correlation_id,
            "trace_id": self.trace_id,
            "audit_id": self.audit_id,
            "incident_id": self.incident_id,
            "log_id": self.log_id
        }

    @classmethod
    def create_new(cls) -> 'CorrelationContext':
        return cls()
