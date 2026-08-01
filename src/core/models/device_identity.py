from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class DeviceIdentityModel:
    device_uuid: str
    public_id: str
    fingerprint: str
    created_at: str
    rsa_public_key_pem: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "device_uuid": self.device_uuid,
            "public_id": self.public_id,
            "fingerprint": self.fingerprint,
            "created_at": self.created_at,
            "rsa_public_key_pem": self.rsa_public_key_pem
        }
