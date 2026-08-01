import time
from dataclasses import dataclass
from typing import Dict, Set, Optional
from ..interfaces.i_service import IService
from .permission_engine_service import PermissionEngineService, PermissionContext
from .security_policy_service import SecurityPolicyService
from ..models.correlation_context import CorrelationContext
from ..exceptions.vigi_exceptions import SecurityException, ReplayAttackDetectedException, UserException

@dataclass
class CommandRequest:
    command_text: str
    sender_id: str
    timestamp: float
    nonce: str
    role: str = "OWNER"
    correlation_context: Optional[CorrelationContext] = None

class CommandAuthorizationService(IService):
    def __init__(
        self,
        permission_engine: PermissionEngineService,
        security_policy: SecurityPolicyService,
        max_skew_seconds: int = 60,
        rate_limit_per_minute: int = 30
    ):
        self.permission_engine = permission_engine
        self.security_policy = security_policy
        self.max_skew_seconds = max_skew_seconds
        self.rate_limit_per_minute = rate_limit_per_minute

        self._seen_nonces: Set[str] = set()
        self._rate_limits: Dict[str, list] = {}  # sender_id -> timestamps
        self._initialized = False

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def shutdown(self) -> None:
        self._seen_nonces.clear()
        self._rate_limits.clear()
        self._initialized = False

    def authorize_command(self, request: CommandRequest) -> CorrelationContext:
        ctx = request.correlation_context or CorrelationContext.create_new()
        now = time.time()

        # 1. Timestamp validation (Anti-replay / Anti-skew)
        if abs(now - request.timestamp) > self.max_skew_seconds:
            raise ReplayAttackDetectedException(f"Command timestamp skewed by {abs(now - request.timestamp):.1f}s (> {self.max_skew_seconds}s limit)")

        # 2. Nonce Tracking (Anti-replay)
        if request.nonce in self._seen_nonces:
            raise ReplayAttackDetectedException(f"Duplicate nonce '{request.nonce}' detected. Potential replay attack.")
        self._seen_nonces.add(request.nonce)

        # Cleanup old nonces
        if len(self._seen_nonces) > 10000:
            self._seen_nonces.clear()

        # 3. Rate Limiting Check
        user_requests = self._rate_limits.get(request.sender_id, [])
        user_requests = [t for t in user_requests if now - t < 60]
        if len(user_requests) >= self.rate_limit_per_minute:
            raise UserException(f"Rate limit exceeded for sender '{request.sender_id}'. Max {self.rate_limit_per_minute} req/min.")
        user_requests.append(now)
        self._rate_limits[request.sender_id] = user_requests

        # 4. Security Policy Engine Evaluation
        cmd_name = request.command_text.strip().split()[0] if request.command_text else ""
        self.security_policy.evaluate_command_policy(cmd_name)

        # 5. Permission Engine Evaluation
        perm_context = PermissionContext(
            permission_id=self._map_command_to_permission(cmd_name),
            actor_role=request.role,
            runtime_privilege="USER",
            actor_name=request.sender_id
        )
        self.permission_engine.authorize(perm_context)

        return ctx

    def _map_command_to_permission(self, cmd_name: str) -> str:
        mapping = {
            "/capture": "webcam_capture",
            "/screen": "screenshot",
            "/lock": "lock_device",
            "/locate": "locate_device",
            "/report": "generate_report"
        }
        return mapping.get(cmd_name.lower(), "general_command")
