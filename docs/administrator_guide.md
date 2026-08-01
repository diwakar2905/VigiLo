# VigiLo Administrator Guide

## 1. System Requirements & Privileges

- **OS**: Windows 10 (1903+) or Windows 11
- **Privileges**: Administrator (`SeSecurityPrivilege`) required to hook into Windows Security Log Event ID 4625.
- **Service Mode**: Runs under `NT AUTHORITY\SYSTEM` account for boot-time protection prior to user logon.

---

## 2. Platform Directory Structure

```
C:\ProgramData\VigiLo\
├── device_state.json      # Device state persistence
├── timeline.db            # SQLite persistent incident log
├── audit.log              # Append-only audit logger
├── identity.dat           # DPAPI encrypted RSA identity & fingerprint
├── policies.json          # Declarative security policies
├── release_metadata.json  # Schema version & feature release manifest
└── AntiTheftCaptures/     # Local encrypted capture buffer
```

---

## 3. Managing Device Recovery States

Administrators can inspect and transition device state using the Desktop GUI or Telegram commands:
- `DISARMED`: Monitoring disabled, zero hardware access.
- `WATCH_MODE`: Failed login monitoring & webcam intruder capture active.
- `LOST_MODE`: Full recovery active (Workstation lock, Geo/WiFi triangulation, Forensic report generation).
