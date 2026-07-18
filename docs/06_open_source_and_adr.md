# PART VI — Open Source & Repository

---

## Chapter 24 — Repository Structure

### 1. Repository Layout Conventions
The repository uses the following package structure:
*   `api/`: External platform integrations (Telegram).
*   `config/`: Configuration validation, serialization, and backup services.
*   `core/`: Lifecycle management and thread orchestration.
*   `security/`: DPAPI wrapper, policy engine, and audit logger.
*   `services/`: Background tasks and polling command servers.
*   `setup/`: Compilation scripts and setup wizards.

---

## Chapter 25 — Contribution Guide

### 1. Code Review Requirements
Before a pull request can be merged, it must meet the following criteria:
*   **Approval**: Requires approval from at least one core maintainer.
*   **Linting**: Must pass Black and Ruff formatting checks.
*   **Testing**: All unit tests must pass, and code coverage must remain above 80%.

---

## Chapter 26 — Issue & PR Templates

Standard markdown templates are provided in the repository to structure bug reports, feature requests, and pull request details.

---

## Chapter 27 — Architectural Decision Records (ADR)

### ADR-001: DPAPI Encryption for Configuration Secrets
*   **Status**: Accepted.
*   **Context**: Plaintext API tokens in configuration files pose a security risk.
*   **Decision**: Encrypt all secrets stored in `config.json` using Windows DPAPI, ensuring decryption is restricted to the active logon session.

### ADR-002: Thread Watchdog Recovery Logic
*   **Status**: Accepted.
*   **Context**: Unsupervised background threads can crash silently, leaving the system in an unmonitored state.
*   **Decision**: Implement a Thread Supervisor watchdog that monitors service heartbeats and restarts failed services with an exponential backoff.

### ADR-003: HMAC-Signed Command Authorization Scheme
*   **Status**: Accepted.
*   **Context**: Plain text Telegram chat_id checks are vulnerable to chat spoofing or message injection if the polling channel is compromised.
*   **Decision**: Gate every command with a cryptographically signed HMAC-SHA256 token derived via HKDF from the DPAPI-protected bot_token. Enforce a 5-minute sliding replay window and nonce-uniqueness tracking to protect against replay attacks.

### ADR-004: Command Rate Limiting
*   **Status**: Accepted.
*   **Context**: Denial of service or abuse of resource-heavy remote modules (e.g. camera, locator) via rapid successive command dispatches.
*   **Decision**: Enforce a sliding-window rate limit (default 20 commands per minute per chat_id) in the SecurityPolicyEngine and register rate-limit violations in the AuditLogger.

### ADR-005: Local Face Verification for False-Positive Reduction
*   **Status**: Accepted.
*   **Context**: Workstation owners occasionally enter their password or PIN incorrectly, triggering false-alarm intruder alerts.
*   **Decision**: Implement local, offline face verification using OpenCV's YuNet (face detection) and SFace (face recognition) ONNX models. Enlist face enrollment during first-run installation. If a failed login triggers an alert and the face matches the owner's reference profile, suppress the Telegram notification and log it as a false alarm. If no match is found, escalate immediately. Encrypt face embeddings via Windows DPAPI before storage.

### ADR-006: Automatic DPAPI-Gated Symmetric Folder Encryption (Vault)
*   **Status**: Accepted.
*   **Context**: Compromise of physical workstation data (unlocked state or intruder access) before the owner can intervene.
*   **Decision**: Implement an automatic in-place data protection vault. Upon intrusion alert escalation, encrypt-in-place all files in the designated target directory using symmetric Fernet encryption, renaming files to `.locked`. Securely generate and store the 32-byte Fernet key in the configuration file, encrypted via Windows DPAPI. Provide a remotely dispatchable `/unlock` Telegram command to reverse encryption and decrypt files back to their original state.

### ADR-007: Local Compilation of Forensic Evidence PDF Reports
*   **Status**: Accepted.
*   **Context**: Workstation theft recovery and insurance/police documentation require structured, tamper-proof forensic evidence compiled in a single package.
*   **Decision**: Create a local, asynchronous PDF compilation module using ReportLab. The module collects system metadata (hostname, OS, MAC, local IP, boot time, user session), face verification logs, and parses captured images to generate an intrusion timeline. If an intruder photo is available, embed it as photo evidence. Expose a `/report` Telegram polling command (gated via HKDF HMAC-SHA256 signature authorization) that triggers report compilation, uploads the document, and immediately cleans it up from the local filesystem to maintain host privacy.

### ADR-008: Alert Channel Expansion & WhatsApp Integration
*   **Status**: Accepted.
*   **Context**: Workstation security and recovery platforms must provide redundant, multi-channel alert delivery to bypass platform-specific API outages or user preference limitations.
*   **Decision**: Establish a generic `NotificationInterface` defining the contract for alert clients (text messages, photo, audio, and document uploads). Generalize `TelegramClient` to implement this interface. Write a custom `WhatsAppClient` targeting the WhatsApp Business Cloud API. Define a composite `NotificationRouter` implementing `NotificationInterface` that receives configurations and seamlessly broadcasts outbound alerts across all active channels (Telegram and/or WhatsApp) simultaneously. Update the system shutdown event and upload queue service to utilize this router.

### ADR-009: Multi-Device Status Sharing Companion Dashboard
*   **Status**: Accepted.
*   **Context**: Supporting families and enterprise fleets requires monitoring multiple VigiLo-protected workstations from a unified management dashboard rather than tracking individual Telegram bot chats.
*   **Decision**: Implement a high-fidelity web companion concept dashboard using a dark glassmorphism design. Display active status grids, locations, and intruder photo feeds for all connected devices. Simulate real-time event updates over a websocket interface, allowing administrators to dispatch remote commands (`/ping`, `/lock`, `/unlock`, `/report`, `/locate`) dynamically to any device.






