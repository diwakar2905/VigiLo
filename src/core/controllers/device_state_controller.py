from ..models.device_state import DeviceState, DeviceStateModel
from ..services.device_state_service import DeviceStateService

class DeviceStateController:
    def __init__(self, service: DeviceStateService):
        self.service = service

    def get_current_state(self) -> DeviceState:
        return self.service.get_current_state()

    def set_state(self, target_state: DeviceState, reason: str, actor: str = "USER") -> bool:
        return self.service.transition_to(target_state, reason, actor)

    def is_feature_allowed(self, feature_name: str) -> bool:
        return self.service.is_feature_allowed(feature_name)
