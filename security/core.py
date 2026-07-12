# security/core.py
from security.crypt import SecretManager
from security.integrity import IntegrityManager
from security.privilege import PermissionManager, PermissionMatrix
from security.auth import AuthorizationManager, SessionManager
from security.policy import SecurityPolicyEngine
from security.audit import AuditLogger
from security.hash import HashManager
from security.secure_memory import SecureMemory

class SecurityCore:
    def __init__(self):
        self.secret_manager = SecretManager()
        self.integrity_manager = IntegrityManager()
        self.permission_manager = PermissionManager()
        self.permission_matrix = PermissionMatrix(self.permission_manager)
        self.authorization_manager = AuthorizationManager()
        self.policy_engine = SecurityPolicyEngine()
        self.audit_logger = AuditLogger()
        self.session_manager = SessionManager()
        self.hash_manager = HashManager()
        self.secure_memory = SecureMemory()

# Global Singleton Instance for clean imports
security_core = SecurityCore()
