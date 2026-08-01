from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any

class VigiLoEdition(Enum):
    COMMUNITY = "Community"
    PROFESSIONAL = "Professional"
    TEAMS = "Teams"
    ENTERPRISE = "Enterprise"

@dataclass
class EditionConfig:
    edition: VigiLoEdition = VigiLoEdition.COMMUNITY
    max_devices: int = 1
    features_unlocked: List[str] = field(default_factory=lambda: [
        "device_states", "device_dashboard", "timeline", "reports",
        "recovery_wizard", "push_health", "trust_framework",
        "notification_abstraction", "device_identity", "secure_pairing",
        "tamper_detection", "permission_engine", "security_policies",
        "command_auth", "observability", "diagnostics", "correlation_ids",
        "error_framework", "release_hardening", "self_healing", "crash_reporting"
    ])

    def is_feature_enabled(self, feature_id: str) -> bool:
        return feature_id in self.features_unlocked

    def to_dict(self) -> Dict[str, Any]:
        return {
            "edition": self.edition.value,
            "max_devices": self.max_devices,
            "features_unlocked": self.features_unlocked
        }
