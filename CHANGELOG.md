# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [3.0.0] - 2026-07-12

This release represents a complete architectural rewrite and security hardening phase, transforming WatchDog from an engineering script collection into a modular Windows security application.

### Added
*   **DPAPI Encryption**: Added transparent Windows Data Protection API (DPAPI) wrappers (`security/crypt.py`) to encrypt the Telegram bot token and chat ID in the `config.json` file at rest.
*   **Folder DACL Hardening**: The installer now automatically locks the `C:\Program Files\WatchDog` directory using Windows CLI `icacls`, restricting Write/Modify permissions to `SYSTEM` and local `Administrators` to prevent unprivileged DLL/binary hijacking.
*   **Named Mutex Guards**: Implemented Win32 named Mutex single-instance guards (`Global\WatchDogServiceMutex` and `Local\WatchDogCommanderMutex`) to prevent duplicate processes from fighting over webcam or HTTP long polling interfaces.
*   **Log Re-Anchoring**: Added self-recovery to the Windows Event Log Monitor (`core/event_monitor.py`). If the Security event log wraps or is cleared, the monitor automatically re-anchors its record pointer instead of looping on missing indices.
*   **Clean Package Structure**: Reorganized files into distinct logical modules: `api`, `config`, `core`, `logs`, `modules`, `security`, `services`, `ui`, and `utils`.
*   **In-Memory Speech**: Replaced the dynamic VBS file dropper with native COM `SAPI.SpVoice` dispatch and ctypes `MessageBoxW` overlays.
*   **Compatibility Wrappers**: Thin redirection modules placed inside legacy `service/` and `setup/` directories to maintain complete backward compatibility with older import calls.

---

## [2.0.0] - Legacy Stable Release

First implementation of background event log monitors and Telegram remote commander tools.
