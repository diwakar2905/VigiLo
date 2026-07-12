# security/policy.py
import os
from security.interfaces import ISecurityPolicyEngine
from security.sanitizer import is_safe_path, sanitize_filename

class SecurityPolicyEngine(ISecurityPolicyEngine):
    def enforce_sandbox_jail(self, target_path: str, jail_path: str) -> bool:
        """Verifies if target_path lies strictly within jail_path."""
        return is_safe_path(jail_path, target_path, follow_symlinks=True)

    def sanitize_filename(self, filename: str) -> str:
        """Strips unsafe path operators from file names."""
        return sanitize_filename(filename)
