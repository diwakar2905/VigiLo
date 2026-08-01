from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any

class HealthStatus(Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"

@dataclass
class HealthObject:
    component_name: str
    status: HealthStatus
    message: str
    last_check: str
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_name": self.component_name,
            "status": self.status.value,
            "message": self.message,
            "last_check": self.last_check,
            "metrics": self.metrics
        }
