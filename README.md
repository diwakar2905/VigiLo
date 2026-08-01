# 🛡️ VigiLo — Privacy-First Windows Device Recovery Platform

> A commercial-grade, open-source, local-first Windows Device Recovery Platform built for absolute user trust, deterministic device state management, forensic evidence capture, and transparent platform security.

---

## ✨ Positioning & Architectural Principles

VigiLo is **NOT** an antivirus, RAT, spyware, or generic endpoint security software. It is a **Privacy-First Device Recovery Platform**.

- 🔒 **100% Local-First**: No cloud servers, no third-party data tracking, zero telemetry collection.
- 🚦 **Deterministic Device State Machine**: `DISARMED` ↔ `WATCH MODE` ↔ `LOST MODE`. Features are strictly gated by state permissions.
- 🛡️ **Trust & Permission Explainer**: Full transparency on every OS API and hardware access requirement.
- 📜 **Tamper-Evident Incident Timeline**: Persistent SQLite/JSON log with cryptographic **SHA-256** hashing per event.
- 📋 **Forensic Report Generator**: Export verifiable PDF and JSON forensic reports containing device info, OS builds, timeline records, and image hashes.
- ❤️ **Push-Based Health Aggregator**: Real-time status monitoring across all services without high-CPU polling loops.
- 🧙 **Guided Recovery Wizard**: Step-by-step UI workflow guiding device owners through loss reporting, evidence gathering, locking, and report compilation.

---

## 🎮 Telegram Control Center Commands

| Command | Category | Description |
| :--- | :--- | :--- |
| `/mode` | State Machine | Show current Device State (`DISARMED`, `WATCH_MODE`, `LOST_MODE`) |
| `/disarm` | State Machine | Set device state to `DISARMED` (Pauses intruder monitoring) |
| `/watch` | State Machine | Set device state to `WATCH_MODE` (Active local intruder protection) |
| `/lost` | State Machine | Set device state to `LOST_MODE` (Full recovery & evidence logging) |
| `/report` | Reporting | Generate & upload tamper-evident Forensic Incident PDF report |
| `/timeline` | Audit | Display recent persistent incident events |
| `/trust` | Privacy | View OS permissions & explicit privacy justifications |
| `/ping` | Health | Verify platform status and uptime |
| `/capture` | Evidence | Capture webcam photo (Allowed in Watch/Lost modes) |
| `/screen` | Evidence | Take silent desktop screenshot (Allowed in Lost mode) |
| `/locate` | Recovery | IP geolocation & nearby WiFi BSSID triangulation report |
| `/lock` | Recovery | Instantly trigger native Windows `LockWorkstation` |
| `/msg [text]` | Emergency | Display emergency pop-up message on workstation |

---

## 🖥️ Desktop Dashboard & Recovery Wizard

Launch the Desktop UI app:
```bash
python -m src.ui.dashboard_app
```

Tabs Included:
1. **Home**: Device name, Device ID, Current Mode toggle buttons, Runtime & Protection status badges.
2. **Protection**: Feature permission matrix detailing allowed vs. prohibited capabilities for each mode.
3. **Timeline**: Interactive event log with search, JSON export, and PDF Report compilation.
4. **Health**: 3x3 grid of push-monitored subsystem health cards.
5. **Logs**: Append-only audit trail viewer.
6. **Settings**: Configurable Telegram token and security thresholds.
7. **About**: Technical platform summary and explicit privacy justifications.

---

## 🧪 Testing & Verification

Run the full test suite with PyTest:
```bash
python -m pytest tests/
```

---

## 📝 License & Open Source

MIT License - Developed with strict adherence to privacy, user transparency, and Windows platform integrity.
