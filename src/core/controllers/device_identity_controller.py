from ..models.device_identity import DeviceIdentityModel
from ..services.device_identity_service import DeviceIdentityService

class DeviceIdentityController:
    def __init__(self, service: DeviceIdentityService):
        self.service = service

    def get_device_identity(self) -> DeviceIdentityModel:
        return self.service.get_identity()
