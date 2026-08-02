import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Callable
from ..interfaces.i_service import IService
from .capability_registry import CapabilityRegistry, CapabilityDescriptor
from ..services.permission_engine_service import PermissionEngineService, PermissionRequirement, PermissionContext
from ..services.security_policy_service import SecurityPolicyService
from ..services.feature_flag_service import FeatureFlagService
from ..services.audit_logger_service import AuditLoggerService
from ..exceptions.vigi_exceptions import SecurityException, RecoverableException

@dataclass
class SecurityGatewayRequest:
    capability_id: str
    action_name: str
    caller_id: str
    context: Dict[str, Any] = field(default_factory=dict)
    handler: Optional[Callable[[], Any]] = None

@dataclass
class SecurityGatewayResponse:
    success: bool
    correlation_id: str
    capability_id: str
    decision: str  # GRANTED, DENIED
    result: Any = None
    failure_reason: Optional[str] = None
    execution_time_ms: float = 0.0

class SecurityGateway(IService):
    """Centralized single execution path for all privileged operations."""

    def __init__(
        self,
        capability_registry: CapabilityRegistry,
        permission_engine: PermissionEngineService,
        policy_service: SecurityPolicyService,
        feature_flag_service: FeatureFlagService,
        audit_logger: AuditLoggerService
    ):
        self.registry = capability_registry
        self.permission_engine = permission_engine
        self.policy_service = policy_service
        self.feature_flags = feature_flag_service
        self.audit_logger = audit_logger
        self._initialized = False

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def shutdown(self) -> None:
        self._initialized = False

    def execute_privileged_operation(self, request: SecurityGatewayRequest) -> SecurityGatewayResponse:
        start_time = time.time()
        correlation_id = f"COR-{uuid.uuid4().hex[:8].upper()}"

        # 1. Capability Lookup (< 1 ms)
        cap = self.registry.get_capability(request.capability_id)
        if not cap:
            return self._deny(request, correlation_id, f"Unknown capability '{request.capability_id}'.", start_time)

        # 2. Caller Validation
        if request.caller_id not in cap.allowed_callers and "*" not in cap.allowed_callers:
            return self._deny(request, correlation_id, f"Caller '{request.caller_id}' not authorized for '{request.capability_id}'.", start_time)

        # 3. Permission Engine Evaluation (< 2 ms)
        perm_ctx = PermissionContext(
            permission_id=cap.required_permission,
            actor_role="OWNER",
            runtime_privilege="USER",
            actor_name=request.caller_id
        )
        try:
            self.permission_engine.authorize(perm_ctx)
        except Exception as e:
            return self._deny(request, correlation_id, f"Permission check failed: {e}", start_time)

        # 4. Security Policy Evaluation (< 2 ms)
        try:
            self.policy_service.evaluate_command_policy(request.action_name)
        except Exception as e:
            return self._deny(request, correlation_id, f"Security Policy violation: {e}", start_time)

        # 5. Audit Event Dispatch
        self.audit_logger.log_event(
            category="SECURITY_GATEWAY_DECISION",
            action=request.action_name,
            actor=request.caller_id,
            details={
                "correlation_id": correlation_id,
                "capability_id": request.capability_id,
                "decision": "GRANTED"
            }
        )

        # 6. Execute Handler
        result = None
        if request.handler:
            try:
                result = request.handler()
            except Exception as e:
                elapsed_ms = (time.time() - start_time) * 1000
                return SecurityGatewayResponse(
                    success=False,
                    correlation_id=correlation_id,
                    capability_id=request.capability_id,
                    decision="GRANTED_BUT_HANDLER_FAILED",
                    failure_reason=str(e),
                    execution_time_ms=round(elapsed_ms, 2)
                )

        elapsed_ms = (time.time() - start_time) * 1000
        return SecurityGatewayResponse(
            success=True,
            correlation_id=correlation_id,
            capability_id=request.capability_id,
            decision="GRANTED",
            result=result,
            execution_time_ms=round(elapsed_ms, 2)
        )

    def _deny(self, request: SecurityGatewayRequest, correlation_id: str, reason: str, start_time: float) -> SecurityGatewayResponse:
        self.audit_logger.log_event(
            category="SECURITY_GATEWAY_DENIED",
            action=request.action_name,
            actor=request.caller_id,
            details={
                "correlation_id": correlation_id,
                "capability_id": request.capability_id,
                "reason": reason
            }
        )
        elapsed_ms = (time.time() - start_time) * 1000
        return SecurityGatewayResponse(
            success=False,
            correlation_id=correlation_id,
            capability_id=request.capability_id,
            decision="DENIED",
            failure_reason=reason,
            execution_time_ms=round(elapsed_ms, 2)
        )
