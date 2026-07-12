# security/auth.py
import time
from security.interfaces import IAuthorizationManager, ISessionManager
from security.context import SecurityContext
from security.exceptions import AccessDeniedError, PolicyViolationError
from security.audit import PermissionDenied, SecurityEvent
from security.privilege import PermissionManager, PermissionMatrix
from security.policy import SecurityPolicyEngine
from security.audit import AuditLogger

class AuthorizationManager(IAuthorizationManager):
    def __init__(self, permission_manager=None, policy_engine=None, audit_logger=None):
        self.pm = permission_manager if permission_manager else PermissionManager()
        self.matrix = PermissionMatrix(self.pm)
        self.policy = policy_engine if policy_engine else SecurityPolicyEngine()
        self.audit = audit_logger if audit_logger else AuditLogger()

    def authorize_request(self, sender_chat_id: str, authorized_chat_id: str) -> bool:
        """Verifies if sender_chat_id matches the authorized_chat_id value."""
        if not sender_chat_id or not authorized_chat_id:
            return False
        return str(sender_chat_id).strip() == str(authorized_chat_id).strip()

    def authorize_action(self, action: str, calling_module: str, context_details: dict = None) -> bool:
        """
        Executes the security pipeline: Authenticate -> Authorize -> Validate Policy -> Audit.
        Raises structured exceptions on failure.
        """
        # 1. Capture OS security context metadata
        ctx = SecurityContext.capture(action, calling_module, "PENDING")
        
        # 2. Check declarative permission rules
        allowed = self.matrix.check_permission(action, context_details)
        if not allowed:
            ctx["result"] = "DENIED"
            event = PermissionDenied(actor=ctx["user"], action=action, details="Context permission check failed", context=ctx)
            self.audit.log_security_event(event)
            raise AccessDeniedError(f"Access Denied: Context lacks permissions to execute '{action}'.")

        # 3. Check security policy constraints
        if self.policy and context_details and "target_path" in context_details:
            jail_path = context_details.get("jail_path", "")
            target_path = context_details.get("target_path", "")
            if not self.policy.enforce_sandbox_jail(target_path, jail_path):
                ctx["result"] = "VIOLATION"
                event = PermissionDenied(actor=ctx["user"], action=action, details=f"Sandbox escape blocked: target={target_path}", context=ctx)
                self.audit.log_security_event(event)
                raise PolicyViolationError(f"Security Policy Violation: Target path '{target_path}' resides outside sandbox.")

        # 4. Log Success Audit
        ctx["result"] = "SUCCESS"
        event = SecurityEvent("ActionAuthorized", ctx["user"], action, "SUCCESS", "Authorized and validated successfully", ctx)
        self.audit.log_security_event(event)
        return True

class SessionManager(ISessionManager):
    def __init__(self):
        self._sessions = {}

    def start_session(self, session_id: str, context_details: dict) -> dict:
        """Starts a session tracking transaction logs."""
        session = {
            "session_id": session_id,
            "created_at": time.time(),
            "context": context_details,
            "active": True
        }
        self._sessions[session_id] = session
        return session

    def validate_session(self, session_id: str) -> bool:
        """Validates if the session context is active and not timed out (max 2 hours)."""
        if session_id not in self._sessions:
            return False
        session = self._sessions[session_id]
        if time.time() - session["created_at"] > 7200:
            session["active"] = False
        return session["active"]
