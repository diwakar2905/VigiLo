# VigiLo v2 Security and Codebase Audit Report

## 1. Authorization Request Hardening Audit
- **Current State**: `security/auth.py`'s `AuthorizationManager.authorize_request` performs a simple, plain string comparison of `sender_chat_id` and `authorized_chat_id` after stripping whitespace. 
- **Security Vulnerability**: This string comparison is the single point of failure. If the polling channel is compromised or simulated, there is no cryptographic guarantee of sender authenticity or request integrity.
- **Remediation**: We will replace the plain string comparison with a cryptographically signed, timestamped token scheme. The token will contain `chat_id:timestamp:nonce:hmac` and will be verified using an HMAC-SHA256 key derived from the decrypted, DPAPI-protected Telegram `bot_token`. Replay protection will be enforced using a 5-minute sliding window and nonce tracking.

---

## 2. Service Layer Duplication and Command Path Trace
- **Duplication Audit**: 
  - The directory `services/service/` contains legacy compatibility wrappers (`camera.py`, `commander.py`, `monitor.py`, `uploader.py`) that delegate tasks to modern implementations.
  - None of the active codebase imports or uses these wrappers. `services/telegram_polling.py` is the canonical commander implementation.
  - **Resolution**: Consolidate the codebase by deleting the redundant `services/service/` directory and its files.
- **Command Gating & Sandbox Jail Trace**:
  - Currently, sandbox jail enforcement in `security/policy.py` is only executed when `target_path` is present in `context_details`.
  - In `services/telegram_polling.py`, only the `/download` command populates `target_path` and `jail_path`.
  - There is a bug in `/download` gating: it queries `sandbox_root` on `FileManagerModule`, which does not exist (the property name is `jail_root`), causing it to fall back to the user's home directory.
  - `/ls` and `/cd` are mapped to the `"AccessFiles"` action but do not populate `target_path` or `jail_path` in `context_details`, thereby bypassing the sandbox jail checks in `authorize_action`.
  - `/ping` and `/help` do not route through `authorize_action` at all.
  - **Remediation**: 
    - Correct the attribute query from `sandbox_root` to `jail_root`.
    - Update `/ls` and `/cd` handlers to populate `target_path` and `jail_path` in `ctx_details`.
    - Map `/ping` and `/help` to actions so they are routed through `authorize_action` for full audit trails and rate limiting.

---

## 3. Module Authorization Flow Audit
- **Current State**: Both `modules/file_manager.py` and `modules/locking.py` are instantiated and executed inside `services/telegram_polling.py`.
- **Gating Status**: They are not called directly by external integrations, but the command routing for file manager actions `/ls` and `/cd` was bypassing the `SecurityPolicyEngine` jail validation.
- **Remediation**: Ensuring `/ls` and `/cd` populate `ctx_details` completely fixes this vulnerability, ensuring the security layer validates all sandbox file accesses before executing module code.

---

## 4. Configuration Migration Path
- **Current State**: `config/migration.py` uses sequential migration methods (`_migrate_vX_to_vY`) to upgrade schemas to `CURRENT_CONFIG_VERSION`.
- **Handling Future Schema Changes**: For future phases (face enrollment, vault paths, WhatsApp channel config, insurance-report templates), we will:
  - Add default schemas/fields to `config/schema.py`.
  - Increment `CURRENT_CONFIG_VERSION` in `config/defaults.py`.
  - Implement the corresponding migration function (e.g., `_migrate_v1_to_v2`) in `config/migration.py` to populate new fields with default values, ensuring existing installations load legacy configuration files without errors.

---

## 5. Phase 1 Resolution Status
- **Harden `authorize_request`**: Resolved. Replaced plain string checks with a cryptographically signed HMAC-SHA256 token verification scheme. Added nonce tracking (replay protection) and a 5-minute sliding window. Verified in `tests/test_auth.py`.
- **Legacy Service Wrappers**: Resolved. Deleted the redundant wrapper directory `services/service/`.
- **Sandbox Gating of `/ls`, `/cd`**: Resolved. Commands now populate full context details (`target_path` and `jail_path`) so that the policy engine enforces sandbox boundaries.
- **`/download` Sandbox Root Query Bug**: Resolved. Fixed attribute query reference from `sandbox_root` to `jail_root`.
- **Command Audit & Rate Limiting**: Resolved. Enforced sliding-window command rate limits (20 requests per minute) inside `TelegramPollingService.start` before dispatching, and mapped `/ping` and `/help` to flow through the authentication chain.

