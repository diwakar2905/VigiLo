from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class PermissionDescriptor:
    permission_id: str
    name: str
    justification: str
    privacy_impact: str
    is_granted: bool
    is_required: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "permission_id": self.permission_id,
            "name": self.name,
            "justification": self.justification,
            "privacy_impact": self.privacy_impact,
            "is_granted": self.is_granted,
            "is_required": self.is_required
        }
