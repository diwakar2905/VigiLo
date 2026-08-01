from datetime import datetime
from typing import Callable, List
from ..interfaces.i_service import IService
from ..models.device_state import DeviceState, DeviceStateModel, FeaturePermissionMatrix
from ..repositories.device_state_repository import DeviceStateRepository
from .audit_logger_service import AuditLoggerService

class DeviceStateService(IService):
    def __init__(self, repository: DeviceStateRepository, audit_logger: AuditLoggerService):
        self.repository = repository
        self.audit_logger = audit_logger
        self.current_model: DeviceStateModel = self.repository.load_state()
        self._listeners: List[Callable[[DeviceState], None]] = []
        self._initialized = False

    def initialize(self) -> bool:
        self.current_model = self.repository.load_state()
        self._initialized = True
        return True

    def shutdown(self) -> None:
        self._listeners.clear()
        self._initialized = False

    def get_current_state(self) -> DeviceState:
        return self.current_model.state

    def transition_to(self, target_state: DeviceState, reason: str, actor: str = "USER") -> bool:
        previous_state = self.current_model.state
        if previous_state == target_state:
            return True

        new_model = DeviceStateModel(
            state=target_state,
            updated_at=datetime.utcnow().isoformat(),
            updated_by=actor,
            transition_reason=reason
        )

        if self.repository.save_state(new_model):
            self.current_model = new_model
            self.audit_logger.log_event(
                category="STATE_TRANSITION",
                action=f"{previous_state.value} -> {target_state.value}",
                actor=actor,
                details={"reason": reason}
            )
            self._notify_listeners(target_state)
            return True
        return False

    def is_feature_allowed(self, feature_name: str) -> bool:
        return FeaturePermissionMatrix.is_feature_allowed(self.get_current_state(), feature_name)

    def subscribe(self, listener: Callable[[DeviceState], None]) -> None:
        if listener not in self._listeners:
            self._listeners.append(listener)

    def _notify_listeners(self, state: DeviceState) -> None:
        for listener in self._listeners:
            try:
                listener(state)
            except Exception as e:
                print(f"[ERROR] State listener exception: {e}")
