import uuid
import hashlib
import platform
from datetime import datetime
from typing import Optional
from ..interfaces.i_service import IService
from ..models.device_identity import DeviceIdentityModel
from ..repositories.device_identity_repository import DeviceIdentityRepository

class DeviceIdentityService(IService):
    def __init__(self, repository: DeviceIdentityRepository):
        self.repository = repository
        self._current_identity: Optional[DeviceIdentityModel] = None
        self._initialized = False

    def initialize(self) -> bool:
        loaded = self.repository.load_identity_data()
        if loaded:
            self._current_identity = DeviceIdentityModel(
                device_uuid=loaded["device_uuid"],
                public_id=loaded["public_id"],
                fingerprint=loaded["fingerprint"],
                created_at=loaded["created_at"],
                rsa_public_key_pem=loaded["rsa_public_key_pem"]
            )
        else:
            self._current_identity = self._generate_new_identity()
            self.repository.save_identity_data(self._current_identity.to_dict())
        self._initialized = True
        return True

    def shutdown(self) -> None:
        self._initialized = False

    def get_identity(self) -> DeviceIdentityModel:
        if not self._current_identity:
            self.initialize()
        return self._current_identity

    def _generate_new_identity(self) -> DeviceIdentityModel:
        raw_uuid = str(uuid.uuid4())
        node_name = platform.node()
        os_spec = f"{platform.system()}-{platform.machine()}"
        
        fingerprint_raw = f"{raw_uuid}|{node_name}|{os_spec}"
        fingerprint = hashlib.sha256(fingerprint_raw.encode('utf-8')).hexdigest().upper()
        public_id = f"VIGI-{fingerprint[:12]}"
        
        # RSA Public Key PEM Header representation
        pub_key_mock = f"-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAu{fingerprint[:32]}...\n-----END PUBLIC KEY-----"

        return DeviceIdentityModel(
            device_uuid=raw_uuid,
            public_id=public_id,
            fingerprint=fingerprint,
            created_at=datetime.utcnow().isoformat(),
            rsa_public_key_pem=pub_key_mock
        )
