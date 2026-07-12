# PART V — Threat Model & Security Platform

---

## Chapter 20 — Threat Model & Attack Surface

### 1. STRIDE Threat Model Matrix

| Threat Category | Threat Description | VigiLo Mitigation |
| :--- | :--- | :--- |
| **Spoofing** | Unauthorized commands sent to the Telegram bot. | Verification of incoming chat IDs against the authorized `chat_id`. |
| **Tampering** | Modification of configuration files on disk. | Configuration updates are verified against SHA-256 signatures stored in `.meta` files. |
| **Repudiation** | Denial of administrative actions. | Every action is logged as a structured JSON object in `logs/audit.log` with a unique ID. |
| **Information Disclosure** | Leakage of API tokens from configuration files. | Sensitive settings (e.g. Telegram tokens) are encrypted on disk using Windows DPAPI. |

---

## Chapter 21 — Windows Security Subsystems

### 1. Windows Data Protection API (DPAPI)
DPAPI provides symmetric encryption using keying material derived from the Windows logon session. This ensures that only processes running in the user's logon session can decrypt VigiLo settings.

### 2. Process Integrity Levels
Windows uses integrity levels to manage resource access:
*   **SYSTEM / High**: Used by the VigiLo service to monitor event logs.
*   **Medium**: Used by the user-session VigiLo Commander to handle Telegram polling.

---

## Chapter 22 — Cryptographic Lifecycles

*   **Entropy Additions**: Native DPAPI encryption incorporates user credentials to prevent decryption by other logon sessions.
*   **Secure Memory Wiping**: Wipes decrypted secrets from memory using `ctypes.memset` to minimize the risk of credential leakage in RAM.

---

## Chapter 23 — Secure Software Development Lifecycle (SSDLC)

*   **Static Scanning**: Automated dependency scanners run on every pull request to check for vulnerabilities.
*   **Fuzzing**: API parameter inputs are fuzzed to prevent buffer overflow or shell injection exploits.
