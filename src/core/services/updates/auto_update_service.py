import os
import json
import hashlib
from typing import Optional
from ...interfaces.i_service import IService
from ...models.release_manifest import ReleaseManifest
from ...exceptions.vigi_exceptions import SecurityException, ConfigurationException

class AutoUpdateService(IService):
    def __init__(self, current_version: str = "3.5.0", channel: str = "Stable"):
        self.current_version = current_version
        self.channel = channel
        self._initialized = False

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def shutdown(self) -> None:
        self._initialized = False

    def check_for_updates(self, manifest_data: dict) -> Optional[ReleaseManifest]:
        manifest = ReleaseManifest(
            version=manifest_data.get("version", "3.5.0"),
            channel=manifest_data.get("channel", self.channel),
            release_date=manifest_data.get("release_date", "2026-08-01"),
            download_url=manifest_data.get("download_url", ""),
            sha256_checksum=manifest_data.get("sha256_checksum", ""),
            authenticode_signature_verified=manifest_data.get("authenticode_signature_verified", True),
            minimum_compatible_version=manifest_data.get("minimum_compatible_version", "3.0.0"),
            changelog=manifest_data.get("changelog", [])
        )

        if not manifest.authenticode_signature_verified:
            raise SecurityException("Update package rejected: Unverified digital signature.")

        if manifest.version > self.current_version:
            return manifest
        return None

    def verify_update_package(self, filepath: str, expected_sha256: str) -> bool:
        if not os.path.exists(filepath):
            return False
        try:
            with open(filepath, "rb") as f:
                computed = hashlib.sha256(f.read()).hexdigest()
            return computed.lower() == expected_sha256.lower()
        except Exception:
            return False
