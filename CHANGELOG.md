# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [3.5.0] - 2026-07-17

This release introduces the Phase 6 Fleet & Family Companion Dashboard.

### Added
*   **Fleet Companion Dashboard Web Application**: Implemented interactive HTML5, CSS3 (glassmorphism), and Javascript dashboard at `companion_dashboard/index.html`.
*   **Websocket Simulator**: Simulates real-time security logs, active pings, device locks, vault unlocks, forensic report uploads, and GPS map geolocation.
*   **High-Fidelity Assets**: Integrated generated camera feed intruder placeholder png.

---

## [3.4.0] - 2026-07-17

This release introduces the Phase 4 Recovery Evidence & Reporting.

### Added
*   **Report Compilation Module**: Implemented `ReportModule` utilizing ReportLab flowables to gather device specifications (hostname, OS, MAC, local IP, boot time, user session), face stats, and timeline.
*   **Intruder Photo Embedding**: Embeds the last captured intruder photo dynamically as forensic evidence in the PDF.
*   **Remote /report Command Polling**: Added `/report` Telegram command to trigger, upload, and instantly cleanup compiled PDF evidence documents.

---

## [3.3.0] - 2026-07-17

This release introduces the Phase 3 Data Protection Vault.

### Added
*   **Symmetric Vault Module**: Implemented `VaultModule` utilizing cryptography's Fernet for secure, in-place, recursive file encryption (`.locked`).
*   **Automatic DPAPI Key Generation**: Automatically generates a unique base64 Fernet key on engine startup if missing, saved via config manager and encrypted via Windows DPAPI.
*   **Intrusion Escalation Trigger**: Hooked vault locking to automatically trigger when a wrong password alert is escalated (owner face mismatch).
*   **Remote /unlock Commander Action**: Added `/unlock` Telegram command routing, letting the owner securely decrypt and restore files back to their original state remotely.

---

## [3.2.0] - 2026-07-17

This release introduces the Phase 2 AI False-Positive Reduction utilizing local face verification.

### Added
*   **Local Face Verification Module**: Implemented `FaceVerificationModule` utilizing OpenCV's YuNet (face detection) and SFace (face recognition) ONNX models for secure, on-device, fully-offline face verification.
*   **Installer Enrollment GUI**: Added `FaceEnrollPage` to the first-run installation wizard. Allows the user to download models, verify connection, capture 5 reference photos, extract face embeddings, and encrypt them.
*   **DPAPI Embedded Face Profile**: Embeddings are stored encrypted in the configuration via Windows DPAPI.
*   **Alert Suppression**: Failed login alerts are automatically checked against the owner's face. Matched attempts suppress notifications, saving disk space and privacy, and log a false alarm.
*   **Stats Tracking**: Records owner matches vs. intruder alert escalations locally in `face_stats.json`.

---

## [3.1.0] - 2026-07-17

This release introduces the Phase 1 security hardening and codebase consolidation for the VigiLo v2 "Recovery & Data Protection Platform".

### Added
*   **HMAC-Signed Authorization**: Introduced a cryptographically signed HMAC-SHA256 token verification scheme in `AuthorizationManager` to protect all incoming Telegram commands against replay attacks and chat spoofing.
*   **Command Rate Limiting**: Added per-chat_id sliding-window rate limiting to the `SecurityPolicyEngine` to prevent abuse of resource-intensive commands.
*   **Auditing and Diagnostics**: Added the `RateLimitExceeded` audit event and expanded coverage of sandbox escapes to all directory-related commands (`/ls`, `/cd`, `/download`).

### Changed
*   **Codebase Consolidation**: Deleted redundant legacy wrapper modules in `services/service/` (`camera.py`, `commander.py`, `monitor.py`, `uploader.py`).
*   **Sandbox Jail Fixes**: Corrected path traversal check parameters in `/download`, `/ls`, and `/cd` commands to properly query the module's `jail_root`.

---

## [3.0.0] - 2026-07-12
*   **DPAPI Encryption**: Added transparent Windows Data Protection API (DPAPI) wrappers (`security/crypt.py`) to encrypt the Telegram bot token and chat ID in the `config.json` file at rest.
*   **Folder DACL Hardening**: The installer now automatically locks the `C:\Program Files\VigiLo` directory using Windows CLI `icacls`, restricting Write/Modify permissions to `SYSTEM` and local `Administrators` to prevent unprivileged DLL/binary hijacking.
*   **Named Mutex Guards**: Implemented Win32 named Mutex single-instance guards (`Global\VigiLoServiceMutex` and `Local\VigiLoCommanderMutex`) to prevent duplicate processes from fighting over webcam or HTTP long polling interfaces.
*   **Log Re-Anchoring**: Added self-recovery to the Windows Event Log Monitor (`core/event_monitor.py`). If the Security event log wraps or is cleared, the monitor automatically re-anchors its record pointer instead of looping on missing indices.
*   **Clean Package Structure**: Reorganized files into distinct logical modules: `api`, `config`, `core`, `logs`, `modules`, `security`, `services`, `ui`, and `utils`.
*   **In-Memory Speech**: Replaced the dynamic VBS file dropper with native COM `SAPI.SpVoice` dispatch and ctypes `MessageBoxW` overlays.
*   **Compatibility Wrappers**: Thin redirection modules placed inside legacy `service/` and `setup/` directories to maintain complete backward compatibility with older import calls.

---

## [2.0.0] - Legacy Stable Release

First implementation of background event log monitors and Telegram remote commander tools.
