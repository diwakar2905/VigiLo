<div align="center">

# 🛡️ VigiLo — Privacy-First Windows Device Recovery Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: Windows 10 | 11](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-blue.svg)](https://microsoft.com/windows)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://python.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Code Style: Clean Architecture](https://img.shields.io/badge/Architecture-Clean%20C--S--R--M-orange.svg)](docs/engineering_bible.md)

*A commercial-grade, open-source, local-first Windows Device Recovery Platform built for absolute user trust, deterministic device state management, forensic evidence capture, and transparent platform security.*

[Features](#-key-features) • [State Machine](#-device-state-machine) • [Quick Start](#-quick-start) • [Architecture](#-system-architecture) • [Contributing](CONTRIBUTING.md) • [License](#-license)

</div>

---

## 📌 Positioning Statement

VigiLo is **NOT** an antivirus, RAT, spyware, or generic endpoint security software.

It is a **Privacy-First Windows Device Recovery Platform**.

Every architectural decision reinforces **Trust, Transparency, Usability, and Reliability**.

- 🔒 **100% Local-First & Zero Cloud Dependencies**: Operates strictly on the owner's Windows machine. No external telemetry servers, third-party databases, or cloud tracking.
- 🚦 **Formal Device State Machine**: Strict feature scoping across `DISARMED`, `WATCH_MODE`, and `LOST_MODE`. Prohibits intrusive operations during normal local device usage.
- 🛡️ **Transparent Trust & Justification Framework**: Clear explanations presented for every OS permission requested (Camera, Admin, Event Logs).
- 📜 **Tamper-Evident Incident Timeline**: Persistent SQLite event logging with **SHA-256** cryptographic hash validation.
- 📋 **Forensic Report Generation**: Export verifiable PDF and JSON forensic reports formatted for personal records and law enforcement evidence.
- ❤️ **Push-Based Health Monitoring**: Real-time status aggregation across subsystems using an observer pattern with zero-polling CPU overhead.
- 🧙 **Guided Recovery Wizard**: Interactive 5-step desktop workflow guiding device owners through loss recovery, evidence collection, locking, and report generation.

---

## ✨ Key Features

| Feature | Description | Scope / Access Rule |
| :--- | :--- | :--- |
| **Instant Login Intruder Detection** | Hooks into Windows Event ID 4625 (Failed Logon) for 0.1s detection | Allowed in `WATCH_MODE` & `LOST_MODE` |
| **Webcam Snapshot Capture** | Takes photo of intruder attempting physical login | Allowed in `WATCH_MODE` & `LOST_MODE` |
| **Telegram Owner Alerts** | Transmits encrypted photo alerts directly to owner's Telegram bot | Allowed in `WATCH_MODE` & `LOST_MODE` |
| **Remote Workstation Lock** | Triggers native Windows `LockWorkstation` API | Restricted to `LOST_MODE` |
| **Geo-Location & WiFi Triangulation** | Gathers IP geolocation & scans nearby BSSIDs for Wigle mapping | Restricted to `LOST_MODE` |
| **Silent Desktop Screenshot** | Takes snapshot of active desktop session | Restricted to `LOST_MODE` |
| **Tamper-Evident Report Generator** | Exports cryptographically verified PDF/JSON forensic reports | Available in all modes |
| **Desktop Management Dashboard** | Professional 7-tab GUI application (`Home`, `Protection`, `Timeline`, `Health`, `Logs`, `Settings`, `About`) | Available in all modes |

---

## 🚦 Device State Machine

VigiLo replaces always-active monitoring with a deterministic **Device State Engine**:

```
        ┌─────────────┐
        │  DISARMED   │ ── (Monitoring disabled, runtime healthy, zero captures)
        └──────┬──────┘
               │  ▲
 Owner Disarms │  │ Owner Enables Guard
               ▼  │
        ┌─────────────┐
        │ WATCH MODE  │ ── (Local intruder protection: Failed login, Camera capture, Alert notice)
        └──────┬──────┘
               │  ▲
  Report Lost  │  │ Owner Recovers Device
               ▼  │
        ┌─────────────┐
        │  LOST MODE  │ ── (Full Recovery: Workstation Lock, Geo Triangulation, Report Generation)
        └─────────────┘
```

---

## 🎮 Telegram Control Center Commands

Owners can manage their device state and trigger recovery actions directly via Telegram:

```
🛡️ VigiLo Command Center
• /mode     - View current Device State
• /disarm   - Set state to DISARMED
• /watch    - Set state to WATCH MODE
• /lost     - Set state to LOST MODE
• /report   - Generate & upload Forensic PDF Report
• /timeline - View recent persistent incident log
• /trust    - View Privacy & Permission Justifications
• /ping     - Check platform status & uptime
• /capture  - Take webcam photo
• /screen   - Take desktop screenshot (Lost Mode)
• /locate   - Geolocation & WiFi Triangulation
• /lock     - Instantly Lock Workstation
• /msg      - Display emergency pop-up message
```

---

## 🚀 Quick Start

### 1. Prerequisites
- **Windows 10 / 11**
- **Python 3.10+**
- **Telegram Bot Token & Chat ID** (Obtained via [@BotFather](https://t.me/botfather))

### 2. Installation & Setup
```bash
# Clone repository
git clone https://github.com/diwakar2905/VigiLo.git
cd VigiLo

# Install python dependencies
pip install -r requirements.txt
```

### 3. Launch Desktop Dashboard
```bash
python -m src.ui.dashboard_app
```

---

## 🏗️ System Architecture

VigiLo strictly follows the **Controller -> Service -> Repository -> Model -> UI** pattern:

```
src/
├── core/
│   ├── controllers/      # Service Container & DI Layer
│   ├── interfaces/       # Base IService & Component Contracts
│   ├── models/           # DeviceState, IncidentEvent, IncidentReport, HealthObject
│   ├── repositories/     # SQLite Timeline, DeviceState JSON, AuditLog Append-Only
│   └── services/         # DeviceStateService, TimelineService, ReportService, HealthService, TrustService
├── ui/
│   ├── views/            # Home, Protection, Timeline, Health, Logs, Settings, About
│   ├── wizard/           # Guided 5-step Recovery Wizard Dialog
│   └── dashboard_app.py  # Main Tkinter Desktop Application
service/
├── monitor.py            # SYSTEM Background Service (Event 4625 Listener)
└── commander.py          # User Agent Telegram Long-Polling Listener
tests/                    # PyTest Unit & Integration Test Suite
docs/                     # Engineering Bible, Threat Model, ADRs
```

---

## 🧪 Testing

VigiLo enforces **>= 95%** coverage target for all core business logic modules.

Run the test suite locally:
```bash
python -m pytest tests/
```

---

## 👥 Open Source Contribution

We welcome contributions from open-source developers, Windows engineers, and security researchers!

Please review our:
- 📖 [Contribution Guidelines](CONTRIBUTING.md)
- 📐 [Engineering Bible](docs/engineering_bible.md)
- 🔒 [Threat Model & Security Policy](docs/threat_model.md)
- 📜 [Contributor Code of Conduct](CODE_OF_CONDUCT.md)

---

## 📄 License

VigiLo is licensed under the **MIT License**. See the [LICENSE](file:///c:/Users/diwak/Downloads/WatchDog-61675e7fe6254baf87bd0b158efba4b9e6192b34/WatchDog-61675e7fe6254baf87bd0b158efba4b9e6192b34/LICENSE) file for complete details.
