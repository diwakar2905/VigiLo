from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class ReleaseManifest:
    version: str
    channel: str  # Stable, Beta, Nightly
    release_date: str
    download_url: str
    sha256_checksum: str
    authenticode_signature_verified: bool
    minimum_compatible_version: str
    changelog: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "channel": self.channel,
            "release_date": self.release_date,
            "download_url": self.download_url,
            "sha256_checksum": self.sha256_checksum,
            "authenticode_signature_verified": self.authenticode_signature_verified,
            "minimum_compatible_version": self.minimum_compatible_version,
            "changelog": self.changelog,
            "metadata": self.metadata
        }
