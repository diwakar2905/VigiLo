from typing import Optional, Dict, Any

class VigiLoBaseException(Exception):
    """Base exception for all VigiLo platform errors."""
    def __init__(self, message: str, error_code: str = "ERR_UNKNOWN", details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

class SecurityException(VigiLoBaseException):
    """Raised on security policy violation, unauthorized access, or tamper attempt."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="ERR_SECURITY_VIOLATION", details=details)

class RecoverableException(VigiLoBaseException):
    """Raised for non-fatal transient failures that support automatic retries."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="ERR_RECOVERABLE_TRANSIENT", details=details)

class FatalException(VigiLoBaseException):
    """Raised when an unrecoverable system failure occurs requiring controlled shutdown/restart."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="ERR_FATAL_SYSTEM_FAILURE", details=details)

class ConfigurationException(VigiLoBaseException):
    """Raised on missing, corrupted, or invalid configuration parameters."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="ERR_INVALID_CONFIG", details=details)

class RuntimeException(VigiLoBaseException):
    """Raised during runtime service failures or OS integration errors."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="ERR_RUNTIME_FAILURE", details=details)

class UserException(VigiLoBaseException):
    """Raised on invalid user actions or unauthenticated operations."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="ERR_USER_ACTION_INVALID", details=details)

class ReplayAttackDetectedException(SecurityException):
    """Raised when a replayed command nonce or stale timestamp is detected."""
    def __init__(self, message: str = "Replay attack or invalid nonce detected"):
        super().__init__(message, details={"security_alert": "REPLAY_ATTACK"})
