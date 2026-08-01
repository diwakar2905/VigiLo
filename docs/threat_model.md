# VigiLo Threat Model & Security Architecture

## 1. Threat Scenarios & Mitigations (STRIDE Framework)

### Spoofing (Identity Impersonation)
- **Threat**: Unauthorized user sending commands via Telegram bot.
- **Mitigation**: `commander.py` strictly validates incoming message `user_id == CHAT_ID`. Unrecognized sender IDs are ignored immediately without execution.

### Tampering (Data Alteration)
- **Threat**: An intruder modifying local timeline logs or evidence photos to hide presence.
- **Mitigation**: Every event is hashed with SHA-256 upon creation. The Forensic Incident Report computes a master cryptographic digest covering all log entries and picture assets.

### Repudiation (Denial of Actions)
- **Threat**: User claiming state transitions or locks were performed by software error.
- **Mitigation**: All state changes are logged to an append-only `audit.log` file with timestamps, actor IDs, and explicit transition reasons.

### Information Disclosure (Privacy Leakage)
- **Threat**: Sensitive webcam photos or location telemetry being intercepted or sent to third-party cloud.
- **Mitigation**: VigiLo operates on a **100% local-first model**. Data is transferred ONLY over TLS directly to the user's self-owned Telegram bot endpoint (`api.telegram.org`).

### Denial of Service (System Failure)
- **Threat**: System crash causing monitoring to stop.
- **Mitigation**: Service runs with SYSTEM privileges, automatic restart handlers, offline queue buffering, and zero-polling event log hooks.

### Elevation of Privilege (Exploit Abuse)
- **Threat**: Malware utilizing VigiLo APIs to bypass Windows security mechanisms.
- **Mitigation**: VigiLo strictly adheres to standard Win32 APIs (`win32evtlog`, `LockWorkstation`). No kernel driver injection, hidden process creation, or security bypass mechanisms are utilized.
