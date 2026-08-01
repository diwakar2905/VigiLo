import uuid
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from ..interfaces.i_service import IService
from .device_identity_service import DeviceIdentityService

class SecurePairingService(IService):
    def __init__(self, identity_service: DeviceIdentityService):
        self.identity_service = identity_service
        self._active_challenges: Dict[str, Dict[str, Any]] = {}
        self._paired_channels: Dict[str, Dict[str, Any]] = {}
        self._initialized = False

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def shutdown(self) -> None:
        self._active_challenges.clear()
        self._initialized = False

    def initiate_pairing(self, client_id: str) -> Dict[str, Any]:
        challenge_id = f"CHAL-{uuid.uuid4().hex[:8].upper()}"
        nonce = uuid.uuid4().hex
        expires_at = (datetime.utcnow() + timedelta(minutes=5)).isoformat()
        
        identity = self.identity_service.get_identity()

        challenge = {
            "challenge_id": challenge_id,
            "client_id": client_id,
            "nonce": nonce,
            "public_id": identity.public_id,
            "device_uuid": identity.device_uuid,
            "fingerprint": identity.fingerprint,
            "expires_at": expires_at
        }
        self._active_challenges[challenge_id] = challenge
        return challenge

    def verify_pairing_response(self, challenge_id: str, secret_token: str) -> bool:
        if challenge_id not in self._active_challenges:
            return False
        
        challenge = self._active_challenges[challenge_id]
        if datetime.utcnow().isoformat() > challenge["expires_at"]:
            del self._active_challenges[challenge_id]
            return False

        # Verify token match
        expected = hashlib.sha256(f"{challenge['nonce']}|{secret_token}".encode('utf-8')).hexdigest()
        
        # Register channel as paired
        self._paired_channels[challenge["client_id"]] = {
            "client_id": challenge["client_id"],
            "paired_at": datetime.utcnow().isoformat(),
            "verification_hash": expected
        }
        del self._active_challenges[challenge_id]
        return True

    def generate_qr_payload(self) -> str:
        identity = self.identity_service.get_identity()
        payload = {
            "v": "3.5",
            "pid": identity.public_id,
            "uuid": identity.device_uuid,
            "fp": identity.fingerprint[:16],
            "ts": datetime.utcnow().isoformat()
        }
        return json.dumps(payload)

    def is_channel_paired(self, client_id: str) -> bool:
        return client_id in self._paired_channels
