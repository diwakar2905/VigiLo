from dataclasses import dataclass
from typing import Dict, Any, Optional
from ..interfaces.i_service import IService
from ..models.device_state import DeviceState
from .device_state_service import DeviceStateService
from .audit_logger_service import AuditLoggerService
from ..exceptions.vigi_exceptions import SecurityException

@dataclass
class PermissionRequirement:
    permission_id: str
    required_state: DeviceState
    required_role: str  # OWNER, SYSTEM, ANONYMOUS
    audit_required: bool = True

@dataclass
class PermissionContext:
    permission_id: str
    actor_role: str
    runtime_privilege: str  # SYSTEM, USER
    actor_name: str = "UNKNOWN"

class PermissionEngineService(IService):
    def __init__(self, device_state_service: DeviceStateService, audit_logger: AuditLoggerService):
        self.device_state_service = device_state_service
        self.audit_logger = audit_logger
        self._permission_registry: Dict[str, PermissionRequirement] = {}
        self._initialized = False

    def initialize(self) -> bool:
        self._load_default_matrix()
        self._initialized = True
        return True

    def shutdown(self) -> None:
        self._permission_registry.clear()
        self._initialized = False

    def register_permission(self, req: PermissionRequirement) -> None:
        self._permission_registry[req.permission_id] = req

    def authorize(self, context: PermissionContext) -> bool:
        req = self._permission_registry.get(context.permission_id)
        current_state = self.device_state_service.get_current_state()

        if not req:
            # Fallback check on device state service
            allowed = self.device_state_service.is_feature_allowed(context.permission_id)
            if not allowed:
                self._audit_denial(context, "Feature not permitted in current DeviceState")
                raise SecurityException(f"Permission '{context.permission_id}' denied in current state '{current_state.value}'")
            return True

        # 1. State Requirement check
        if current_state == DeviceState.DISARMED and req.required_state != DeviceState.DISARMED:
            self._audit_denial(context, f"Requires state {req.required_state.value}, system is DISARMED")
            raise SecurityException(f"Operation '{context.permission_id}' prohibited when system is DISARMED.")

        # 2. Role Check
        if req.required_role == "OWNER" and context.actor_role not in ["OWNER", "SYSTEM"]:
            self._audit_denial(context, "Requires OWNER role")
            raise SecurityException(f"Operation '{context.permission_id}' requires OWNER role.")

        if req.audit_required:
            self.audit_logger.log_event(
                category="PERMISSION_AUTHORIZED",
                action=context.permission_id,
                actor=context.actor_name,
                details={"role": context.actor_role, "state": current_state.value}
            )

        return True

    def _audit_denial(self, context: PermissionContext, reason: str) -> None:
        self.audit_logger.log_event(
            category="PERMISSION_DENIED",
            action=context.permission_id,
            actor=context.actor_name,
            details={"reason": reason, "role": context.actor_role}
        )

    def _load_default_matrix(self) -> None:
        self.register_permission(PermissionRequirement("webcam_capture", DeviceState.WATCH_MODE, "OWNER"))
        self.register_permission(PermissionRequirement("win_login_monitor", DeviceState.WATCH_MODE, "SYSTEM"))
        self.register_permission(PermissionRequirement("lock_device", DeviceState.LOST_MODE, "OWNER"))
        self.register_permission(PermissionRequirement("locate_device", DeviceState.LOST_MODE, "OWNER"))
        self.register_permission(PermissionRequirement("screenshot", DeviceState.LOST_MODE, "OWNER"))
        self.register_permission(PermissionRequirement("generate_report", DeviceState.DISARMED, "OWNER"))
