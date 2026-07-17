# security/core.py
"""Global security subsystem singleton for VigiLo.

All modules that need security primitives should import ``security_core``
from this module rather than constructing their own instances.
"""

from __future__ import annotations

from security.audit import AuditLogger
from security.auth import AuthorizationManager, SessionManager
from security.crypt import SecretManager
from security.hash import HashManager
from security.integrity import IntegrityManager
from security.policy import SecurityPolicyEngine
from security.privilege import PermissionManager, PermissionMatrix
from security.secure_memory import SecureMemory


class SecurityCore:
    """Assembles and owns all security subsystem singletons."""

    def __init__(self, bot_token: str | None = None) -> None:
        self.secret_manager = SecretManager()
        self.integrity_manager = IntegrityManager()
        self.permission_manager = PermissionManager()
        self.permission_matrix = PermissionMatrix(self.permission_manager)
        self.policy_engine = SecurityPolicyEngine()
        self.audit_logger = AuditLogger()
        self.session_manager = SessionManager()
        self.hash_manager = HashManager()
        self.secure_memory = SecureMemory()

        # AuthorizationManager receives the plaintext bot_token so it can
        # derive the HMAC key at startup.  When bot_token is None (e.g. during
        # early test bootstrap) the manager falls back to legacy mode.
        self.authorization_manager = AuthorizationManager(
            permission_manager=self.permission_manager,
            policy_engine=self.policy_engine,
            audit_logger=self.audit_logger,
            bot_token=bot_token,
        )

    def reinitialize_auth(self, bot_token: str) -> None:
        """Re-derives the HMAC key after the bot token becomes available.

        Call this once during setup/install after the config is written and
        decrypted — e.g. from ``VigiLoEngine.__init__`` after
        ``ConfigManager.load()`` succeeds.
        """
        self.authorization_manager = AuthorizationManager(
            permission_manager=self.permission_manager,
            policy_engine=self.policy_engine,
            audit_logger=self.audit_logger,
            bot_token=bot_token,
        )


# Global singleton — constructed without a bot_token initially.
# ``security_core.reinitialize_auth(token)`` is called from the engine
# once the config is loaded and decrypted.
security_core = SecurityCore()
