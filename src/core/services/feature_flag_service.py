import os
from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..interfaces.i_service import IService

@dataclass
class FeatureFlag:
    flag_id: str
    enabled: bool
    tier: str  # COMMUNITY, PROFESSIONAL, ENTERPRISE, EXPERIMENTAL
    description: str

class FeatureFlagService(IService):
    """Production Feature Flag Framework supporting tier gating and env var overrides."""

    def __init__(self, current_tier: str = "COMMUNITY"):
        self.current_tier = current_tier
        self._flags: Dict[str, FeatureFlag] = {}
        self._initialized = False

    def initialize(self) -> bool:
        self._register_default_flags()
        self._initialized = True
        return True

    def shutdown(self) -> None:
        self._flags.clear()
        self._initialized = False

    def _register_default_flags(self):
        defaults = [
            FeatureFlag("device_states", True, "COMMUNITY", "Device state machine management"),
            FeatureFlag("timeline", True, "COMMUNITY", "Persistent timeline event logging"),
            FeatureFlag("forensic_reports", True, "COMMUNITY", "PDF and JSON forensic report export"),
            FeatureFlag("recovery_wizard", True, "COMMUNITY", "6-step guided recovery wizard"),
            FeatureFlag("plugin_sdk", True, "COMMUNITY", "Third-party extension SDK"),
            FeatureFlag("webhooks", True, "COMMUNITY", "HMAC signed outgoing webhooks"),
            FeatureFlag("self_healing", True, "COMMUNITY", "Background self-healing watchdog"),
            FeatureFlag("diagnostics", True, "COMMUNITY", "Self-test diagnostics engine"),
            FeatureFlag("experimental_ai", False, "EXPERIMENTAL", "Experimental AI features")
        ]
        for flag in defaults:
            self._flags[flag.flag_id] = flag

    def is_enabled(self, flag_id: str) -> bool:
        # 1. Environment Variable Override (e.g. VIGILO_FLAG_EXPERIMENTAL_AI=1)
        env_val = os.getenv(f"VIGILO_FLAG_{flag_id.upper()}")
        if env_val is not None:
            return env_val.strip() in ["1", "true", "TRUE"]

        # 2. Flag Registry check
        flag = self._flags.get(flag_id)
        if not flag:
            return False
        
        return flag.enabled

    def set_flag(self, flag_id: str, enabled: bool) -> None:
        if flag_id in self._flags:
            self._flags[flag_id].enabled = enabled
