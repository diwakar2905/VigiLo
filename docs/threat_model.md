# VigiLo Threat Model & STRIDE Security Analysis

## 1. Threat Scenarios & Mitigations

### Spoofing (Identity Impersonation)
- **Threat**: Attacker spoofing Telegram user ID or forging command requests.
- **Mitigation**: `CommandAuthorizationService` validates sender identity, enforces secret pairing challenge responses, and checks DPAPI-backed `DeviceIdentityModel` fingerprints.

### Tampering (Data & Binary Alteration)
- **Threat**: Attacker replacing `monitor.py` binary, modifying `config.json`, or disabling scheduled task `AntiTheft_Commander`.
- **Mitigation**: `TamperDetectionService` computes SHA-256 hashes of core binaries, monitors Task Scheduler status via `schtasks`, and generates immediate CRITICAL timeline incidents upon mismatch.

### Repudiation (Action Denial)
- **Threat**: User denying state changes or workstation locks were initiated.
- **Mitigation**: All operations propagate unified `CorrelationContext` (`correlation_id`, `trace_id`, `audit_id`, `incident_id`, `log_id`) written to append-only `audit.log`.

### Information Disclosure (Privacy Leakage)
- **Threat**: Intruder photos or key material leaking to external cloud servers.
- **Mitigation**: VigiLo operates on a **100% Local-First** model. Private RSA keys are stored via DPAPI obfuscation and never exposed over APIs or network channels.

### Denial of Service (Command Flooding)
- **Threat**: Attacker spamming Telegram commands to exhaust CPU/RAM.
- **Mitigation**: `CommandAuthorizationService` rate-limits commands to 30 requests per minute per sender ID and rejects stale timestamps (>60s skew).

### Elevation of Privilege (Exploit Abuse)
- **Threat**: Local process escalating privileges through VigiLo hooks.
- **Mitigation**: `PermissionEngineService` & `SecurityPolicyService` evaluate state, role, and runtime privileges for every API invocation with strict default-deny rules.
