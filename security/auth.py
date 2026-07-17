# security/auth.py
"""Authorization manager for VigiLo.

Provides HMAC-SHA256 signed command tokens with:
  - 5-minute replay window
  - Per-nonce deduplication
  - Backward-compat plain-chat_id fallback (logs a warning)
"""

from __future__ import annotations

import hashlib
import hmac
import threading
import time
import uuid
from typing import Optional

from logs.logger import logger
from security.audit import (
    AuditLogger,
    PermissionDenied,
    SecurityEvent,
    UnauthorizedCommand,
)
from security.context import SecurityContext
from security.exceptions import AccessDeniedError, PolicyViolationError
from security.interfaces import IAuthorizationManager, ISessionManager
from security.policy import SecurityPolicyEngine
from security.privilege import PermissionManager, PermissionMatrix

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
_TOKEN_REPLAY_WINDOW_SECONDS: int = 300  # 5 minutes
_HKDF_INFO: bytes = b"vigilo-command-auth-v1"


def _derive_hmac_key(bot_token: str) -> bytes:
    """Derives a 32-byte HMAC key from the DPAPI-decrypted bot_token via HKDF-SHA256."""
    # RFC 5869 HKDF — Extract step using a fixed salt
    prk = hmac.new(
        key=b"vigilo-hkdf-salt-2026",
        msg=bot_token.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    # Expand step (single block, L=32)
    t = hmac.new(
        key=prk,
        msg=_HKDF_INFO + b"\x01",
        digestmod=hashlib.sha256,
    ).digest()
    return t


class AuthorizationManager(IAuthorizationManager):
    """HMAC-SHA256 signed token authorization manager.

    Parameters
    ----------
    permission_manager:
        Injected ``PermissionManager`` (defaults to a fresh instance).
    policy_engine:
        Injected ``SecurityPolicyEngine`` (defaults to a fresh instance).
    audit_logger:
        Injected ``AuditLogger`` (defaults to a fresh instance).
    bot_token:
        Raw (plaintext) Telegram bot token used to derive the HMAC key.
        When ``None`` the manager operates in *legacy mode* (plain chat_id compare only).
    """

    def __init__(
        self,
        permission_manager: Optional[PermissionManager] = None,
        policy_engine: Optional[SecurityPolicyEngine] = None,
        audit_logger: Optional[AuditLogger] = None,
        bot_token: Optional[str] = None,
    ) -> None:
        self.pm = permission_manager if permission_manager else PermissionManager()
        self.matrix = PermissionMatrix(self.pm)
        self.policy = policy_engine if policy_engine else SecurityPolicyEngine()
        self.audit = audit_logger if audit_logger else AuditLogger()

        # Nonce store: {nonce: expiry_timestamp}
        self._nonce_store: dict[str, float] = {}
        self._nonce_lock = threading.Lock()

        # HMAC key — derived once at init; None means legacy mode
        self._hmac_key: Optional[bytes] = None
        if bot_token and "YOUR_" not in bot_token:
            try:
                self._hmac_key = _derive_hmac_key(bot_token)
            except Exception as exc:
                logger.warning(
                    f"AuthorizationManager: HMAC key derivation failed: {exc}. Falling back to legacy mode."
                )

    # ----------------------------------------------------------------------- #
    # Public interface
    # ----------------------------------------------------------------------- #

    def authorize_request(
        self,
        sender_chat_id: str,
        authorized_chat_id: str,
        token: str | None = None,
    ) -> bool:
        """Verifies the sender's identity.

        Token path (preferred):
            Validates ``token`` as ``chat_id:unix_ts:nonce`` HMAC-SHA256.
            Rejects tokens outside the 5-minute replay window or with a
            previously-seen nonce.

        Legacy path (fallback):
            If ``token`` is ``None`` or no HMAC key is loaded, falls back to
            a plain chat_id string comparison and emits a WARNING-level log.
        """
        if not sender_chat_id or not authorized_chat_id:
            return False

        # --- Token path ------------------------------------------------------ #
        if token is not None and self._hmac_key is not None:
            return self._verify_token(sender_chat_id, authorized_chat_id, token)

        # --- Legacy fallback path -------------------------------------------- #
        logger.warning(
            "AuthorizationManager: Token not provided or HMAC key unavailable. "
            "Falling back to plain chat_id comparison (legacy mode)."
        )
        return str(sender_chat_id).strip() == str(authorized_chat_id).strip()

    def generate_token(self, chat_id: str) -> str:
        """Generates a short-lived HMAC-SHA256 signed token valid for 5 minutes.

        Format: ``chat_id:unix_timestamp:nonce:hmac_hex``
        """
        if self._hmac_key is None:
            raise RuntimeError(
                "Cannot generate token: HMAC key not loaded (no bot_token configured)."
            )

        timestamp: int = int(time.time())
        nonce: str = uuid.uuid4().hex
        message: str = f"{chat_id}:{timestamp}:{nonce}"
        sig: str = hmac.new(
            key=self._hmac_key,
            msg=message.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()
        return f"{message}:{sig}"

    # ----------------------------------------------------------------------- #
    # Private helpers
    # ----------------------------------------------------------------------- #

    def _verify_token(
        self, sender_chat_id: str, authorized_chat_id: str, token: str
    ) -> bool:
        """Validates the HMAC token and enforces replay-window + nonce uniqueness."""
        parts = token.split(":")
        if len(parts) != 4:
            logger.warning("AuthorizationManager: Malformed token (wrong field count).")
            self._audit_unauthorized(sender_chat_id, "malformed_token")
            return False

        token_chat_id, timestamp_str, nonce, received_sig = parts

        # 1. chat_id must match both the token's embedded ID and the authorized ID
        if (
            token_chat_id != str(sender_chat_id).strip()
            or token_chat_id != str(authorized_chat_id).strip()
        ):
            logger.warning("AuthorizationManager: Token chat_id mismatch.")
            self._audit_unauthorized(sender_chat_id, "chat_id_mismatch")
            return False

        # 2. Timestamp window
        try:
            token_ts = int(timestamp_str)
        except ValueError:
            logger.warning("AuthorizationManager: Non-integer timestamp in token.")
            self._audit_unauthorized(sender_chat_id, "invalid_timestamp")
            return False

        now = int(time.time())
        if abs(now - token_ts) > _TOKEN_REPLAY_WINDOW_SECONDS:
            logger.warning(
                f"AuthorizationManager: Token timestamp outside replay window "
                f"(age={abs(now - token_ts)}s, window={_TOKEN_REPLAY_WINDOW_SECONDS}s)."
            )
            self._audit_unauthorized(sender_chat_id, "token_expired")
            return False

        # 3. HMAC verification — constant-time compare
        message = f"{token_chat_id}:{timestamp_str}:{nonce}"
        expected_sig = hmac.new(
            key=self._hmac_key,  # type: ignore[arg-type]
            msg=message.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()
        if not hmac.compare_digest(expected_sig, received_sig):
            logger.warning("AuthorizationManager: HMAC signature mismatch.")
            self._audit_unauthorized(sender_chat_id, "hmac_mismatch")
            return False

        # 4. Nonce uniqueness (replay protection)
        nonce_key = f"{token_chat_id}:{nonce}"
        with self._nonce_lock:
            self._prune_nonces()
            if nonce_key in self._nonce_store:
                logger.warning(
                    f"AuthorizationManager: Replayed nonce detected: {nonce}."
                )
                self._audit_unauthorized(sender_chat_id, "replayed_nonce")
                return False
            self._nonce_store[nonce_key] = float(now + _TOKEN_REPLAY_WINDOW_SECONDS)

        return True

    def _prune_nonces(self) -> None:
        """Removes expired nonce entries. Must be called under ``_nonce_lock``."""
        now = time.time()
        expired = [k for k, exp in self._nonce_store.items() if exp < now]
        for k in expired:
            del self._nonce_store[k]

    def _audit_unauthorized(self, actor: str, reason: str) -> None:
        """Logs an UnauthorizedCommand audit event."""
        event = UnauthorizedCommand(
            actor=str(actor),
            command="authorize_request",
            details=f"Reason: {reason}",
        )
        self.audit.log_security_event(event)

    # ----------------------------------------------------------------------- #
    # authorize_action — unchanged from v1
    # ----------------------------------------------------------------------- #

    def authorize_action(
        self,
        action: str,
        calling_module: str,
        context_details: dict | None = None,
    ) -> bool:
        """Executes the security pipeline: Authenticate → Authorize → Policy → Audit.

        Raises structured exceptions on failure.
        """
        # 1. Capture OS security context metadata
        ctx = SecurityContext.capture(action, calling_module, "PENDING")

        # 2. Check declarative permission rules
        allowed = self.matrix.check_permission(action, context_details)
        if not allowed:
            ctx["result"] = "DENIED"
            event = PermissionDenied(
                actor=ctx["user"],
                action=action,
                details="Context permission check failed",
                context=ctx,
            )
            self.audit.log_security_event(event)
            raise AccessDeniedError(
                f"Access Denied: Context lacks permissions to execute '{action}'."
            )

        # 3. Check security policy constraints (sandbox jail)
        if self.policy and context_details and "target_path" in context_details:
            jail_path = context_details.get("jail_path", "")
            target_path = context_details.get("target_path", "")
            if not self.policy.enforce_sandbox_jail(target_path, jail_path):
                ctx["result"] = "VIOLATION"
                event = PermissionDenied(
                    actor=ctx["user"],
                    action=action,
                    details=f"Sandbox escape blocked: target={target_path}",
                    context=ctx,
                )
                self.audit.log_security_event(event)
                raise PolicyViolationError(
                    f"Security Policy Violation: Target path '{target_path}' resides outside sandbox."
                )

        # 4. Log success audit
        ctx["result"] = "SUCCESS"
        event = SecurityEvent(
            "ActionAuthorized",
            ctx["user"],
            action,
            "SUCCESS",
            "Authorized and validated successfully",
            ctx,
        )
        self.audit.log_security_event(event)
        return True


class SessionManager(ISessionManager):
    def __init__(self) -> None:
        self._sessions: dict[str, dict] = {}

    def start_session(self, session_id: str, context_details: dict) -> dict:
        """Starts a session tracking transaction logs."""
        session: dict = {
            "session_id": session_id,
            "created_at": time.time(),
            "context": context_details,
            "active": True,
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
