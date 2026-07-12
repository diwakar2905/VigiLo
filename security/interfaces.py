# security/interfaces.py
from abc import ABC, abstractmethod

class ISecretManager(ABC):
    @abstractmethod
    def encrypt(self, plaintext: str) -> str:
        """Encrypts sensitive data, returning a base64 encoded string."""
        pass

    @abstractmethod
    def decrypt(self, ciphertext: str) -> str:
        """Decrypts sensitive data, returning a raw plaintext string."""
        pass

class IIntegrityManager(ABC):
    @abstractmethod
    def calculate_sha256(self, filepath: str) -> str:
        """Calculates SHA-256 hash of a file on disk."""
        pass

    @abstractmethod
    def verify_file(self, filepath: str, expected_hash: str) -> bool:
        """Verifies if the file's hash matches the expected hash."""
        pass

class IPermissionManager(ABC):
    @abstractmethod
    def is_admin(self) -> bool:
        """Checks if the current process is running with administrative privileges."""
        pass

    @abstractmethod
    def is_system(self) -> bool:
        """Checks if the current process is running in SYSTEM context."""
        pass

    @abstractmethod
    def acquire_mutex(self, mutex_name: str) -> object:
        """Acquires a named mutex handle for single-instance checks."""
        pass

class IAuthorizationManager(ABC):
    @abstractmethod
    def authorize_request(self, sender_chat_id: str, authorized_chat_id: str) -> bool:
        """Verifies if the sender's Telegram chat_id matches the authorized configuration."""
        pass

class ISecurityPolicyEngine(ABC):
    @abstractmethod
    def enforce_sandbox_jail(self, target_path: str, jail_path: str) -> bool:
        """Enforces directory path constraints to prevent sandbox escape vulnerabilities."""
        pass

    @abstractmethod
    def sanitize_filename(self, filename: str) -> str:
        """Removes illegal path traversal or control characters from file names."""
        pass

class IAuditLogger(ABC):
    @abstractmethod
    def log_event(self, event_type: str, actor: str, action: str, status: str, details: str = ""):
        """Records a structured security event entry to a dedicated audit stream."""
        pass

class ISessionManager(ABC):
    @abstractmethod
    def start_session(self, session_id: str, context_details: dict) -> dict:
        """Tracks active user logon/command session initialization."""
        pass

    @abstractmethod
    def validate_session(self, session_id: str) -> bool:
        """Checks if the session is currently active and within time constraints."""
        pass

class IHashManager(ABC):
    @abstractmethod
    def secure_hash(self, data: str, salt: str = "") -> str:
        """Generates a secure salt-based hash of target string data."""
        pass

class ISecureMemory(ABC):
    @abstractmethod
    def secure_wipe(self, string_obj: str) -> bool:
        """Overwrites memory buffers containing sensitive data with zeros."""
        pass

class ISecretRotator(ABC):
    @abstractmethod
    def rotate_secrets(self) -> bool:
        """Rotates credentials and updates local configurations."""
        pass

