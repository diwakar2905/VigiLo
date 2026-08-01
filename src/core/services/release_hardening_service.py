import os
import json
from dataclasses import dataclass
from typing import Dict, Any, List
from ..interfaces.i_service import IService
from ..exceptions.vigi_exceptions import ConfigurationException

CURRENT_PLATFORM_VERSION = "3.5.0"
MINIMUM_COMPATIBLE_VERSION = "3.0.0"

@dataclass
class ReleaseMetadataModel:
    version: str
    build_timestamp: str
    compatible_schema_version: str
    features_enabled: List[str]

class ReleaseHardeningService(IService):
    def __init__(self, metadata_filepath: str):
        self.metadata_filepath = metadata_filepath
        self._initialized = False

    def initialize(self) -> bool:
        os.makedirs(os.path.dirname(self.metadata_filepath), exist_ok=True)
        if not os.path.exists(self.metadata_filepath):
            self._save_metadata(self.get_release_metadata())
        self._initialized = True
        return True

    def shutdown(self) -> None:
        self._initialized = False

    def get_release_metadata(self) -> ReleaseMetadataModel:
        return ReleaseMetadataModel(
            version=CURRENT_PLATFORM_VERSION,
            build_timestamp="2026-08-01T00:00:00Z",
            compatible_schema_version="3.5",
            features_enabled=[
                "device_states", "device_dashboard", "timeline", "reports",
                "recovery_wizard", "push_health", "trust_framework",
                "notification_abstraction", "device_identity", "secure_pairing",
                "tamper_detection", "permission_engine", "security_policies",
                "command_auth", "observability", "diagnostics", "correlation_ids",
                "error_framework", "release_hardening"
            ]
        )

    def check_version_compatibility(self, config_version: str) -> bool:
        if not config_version:
            return False
        return config_version >= MINIMUM_COMPATIBLE_VERSION

    def run_migrations_if_needed(self, current_config: Dict[str, Any]) -> Dict[str, Any]:
        cfg_ver = current_config.get("version", "1.0.0")
        if not self.check_version_compatibility(cfg_ver):
            raise ConfigurationException(f"Incompatible config version '{cfg_ver}'. Minimum required: {MINIMUM_COMPATIBLE_VERSION}")

        # Upgrade schema to 3.5.0
        current_config["version"] = CURRENT_PLATFORM_VERSION
        if "platform_hardening" not in current_config:
            current_config["platform_hardening"] = {
                "identity_enabled": True,
                "tamper_detection_enabled": True,
                "correlation_tracing_enabled": True
            }
        return current_config

    def _save_metadata(self, metadata: ReleaseMetadataModel) -> None:
        try:
            with open(self.metadata_filepath, "w", encoding="utf-8") as f:
                json.dump({
                    "version": metadata.version,
                    "build_timestamp": metadata.build_timestamp,
                    "compatible_schema_version": metadata.compatible_schema_version,
                    "features_enabled": metadata.features_enabled
                }, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Failed to save release metadata: {e}")
