# security/exceptions.py


class SecurityError(Exception):
    """Base exception for all security-related errors."""

    pass


class AccessDeniedError(SecurityError):
    """Raised when authorization checks fail or privileges are insufficient."""

    pass


class PolicyViolationError(SecurityError):
    """Raised when an operation violates security policy rules."""

    pass


class DecryptionError(SecurityError):
    """Raised when credentials decryption fails."""

    pass


class IntegrityError(SecurityError):
    """Raised when system binary or configuration signature verification fails."""

    pass
