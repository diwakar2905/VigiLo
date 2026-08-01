from typing import Dict, Any
from ..services.secure_pairing_service import SecurePairingService

class PairingController:
    def __init__(self, service: SecurePairingService):
        self.service = service

    def initiate_pairing(self, client_id: str) -> Dict[str, Any]:
        return self.service.initiate_pairing(client_id)

    def verify_pairing(self, challenge_id: str, secret_token: str) -> bool:
        return self.service.verify_pairing_response(challenge_id, secret_token)

    def get_qr_payload(self) -> str:
        return self.service.generate_qr_payload()
