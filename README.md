<div align="center">

# 🛡️ VigiLo — Privacy-First Windows Device Recovery Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform: Windows 10 | 11](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-blue.svg)](https://microsoft.com/windows)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://python.org)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Code Style: Clean Architecture](https://img.shields.io/badge/Architecture-Clean%20C--S--R--M-orange.svg)](docs/engineering_bible.md)

*A commercial-grade, open-source, local-first Windows Device Recovery Platform built for absolute user trust, deterministic device state management, forensic evidence capture, and transparent platform security.*

[Features](#-key-features) • [State Machine](#-device-state-machine-graph) • [Architecture](#-system-architecture-graph) • [Data Flow](#-data-flow--incident-sequence-graph) • [Quick Start](#-quick-start) • [Contributing](CONTRIBUTING.md) • [License](#-license)

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

## 🚦 Device State Machine Graph

VigiLo replaces always-active monitoring with a deterministic **Device State Engine**:

```mermaid
stateDiagram-v2
    [*] --> DISARMED: Default / Maintenance Mode
    
    DISARMED --> WATCH_MODE: Owner Enables Local Guard
    note right of DISARMED
        • Monitoring Disabled
        • Notifications Paused
        • Zero Camera / File Access
    end note

    WATCH_MODE --> DISARMED: Owner Disarms Platform
    WATCH_MODE --> LOST_MODE: Owner Reports Device Lost
    note right of WATCH_MODE
        • Active Login Intruder Monitoring
        • Webcam Intruder Capture on Wrong PIN
        • Instant Telegram Owner Alerts
        • PROHIBITED: Lock, Locate, Audio, Files
    end note

    LOST_MODE --> WATCH_MODE: Owner Recovers Device
    LOST_MODE --> DISARMED: Owner Resets Platform
    note right of LOST_MODE
        • Workstation Lockdown Enabled
        • Geo-Location & WiFi Triangulation
        • Silent Desktop Screenshot
        • Forensic Report Generation
        • PROHIBITED: Malware execution, Files, Audio
    end note
```

---

## 🏗️ System Architecture Graph

VigiLo strictly follows the **Controller -> Service -> Repository -> Model -> UI** pattern:

```mermaid
graph TD
    subgraph UI_Layer ["UI & Command Layer"]
        UI_Dash[Desktop Dashboard App]
        UI_Wiz[Guided Recovery Wizard]
        Cmd_Tg[Telegram Command Center Handler]
    end

    subgraph Controller_Layer ["Controller Layer (ServiceContainer DI)"]
        StateCtrl[DeviceStateController]
        TimelineCtrl[TimelineController]
        HealthCtrl[HealthController]
        ReportCtrl[ReportController]
    end

    subgraph Service_Layer ["Service Layer (IService Business Logic)"]
        StateSvc[DeviceStateService]
        AuditSvc[AuditLoggerService]
        TimelineSvc[IncidentTimelineService]
        HealthSvc[HealthMonitorService]
        ReportSvc[IncidentReportService]
        TrustSvc[TrustService]
    end

    subgraph Repository_Layer ["Repository & Storage Layer"]
        StateRepo[DeviceStateRepository]
        TimelineRepo[TimelineRepository]
        AuditRepo[AuditLogRepository]
    end

    subgraph OS_Layer ["Windows Platform & Crypto API"]
        WinEvtLog[Windows Security Event Log - Event 4625]
        WinAPI[Win32 LockWorkstation / Netsh WiFi]
        CryptoAPI[SHA-256 Integrity Engine]
    end

    UI_Dash --> StateCtrl
    UI_Dash --> TimelineCtrl
    UI_Dash --> HealthCtrl
    UI_Wiz --> ReportCtrl
    Cmd_Tg --> StateSvc

    StateCtrl --> StateSvc
    TimelineCtrl --> TimelineSvc
    HealthCtrl --> HealthSvc
    ReportCtrl --> ReportSvc

    StateSvc --> StateRepo
    StateSvc --> AuditSvc
    TimelineSvc --> TimelineRepo
    TimelineSvc --> AuditSvc
    ReportSvc --> TimelineRepo
    ReportSvc --> CryptoAPI

    StateSvc --> WinEvtLog
    StateSvc --> WinAPI
```

---

## 🔄 Data Flow & Incident Sequence Graph

How VigiLo detects an intruder attempt, verifies feature permissions, hashes the record, and notifies the owner:

```mermaid
sequenceDiagram
    autonumber
    participant Intruder as Physical Intruder / Attacker
    participant WinLog as Windows Event Log (Event 4625)
    participant Monitor as VigiLo Background Monitor
    participant StateEngine as DeviceStateService
    participant CamHardware as Webcam Hardware
    participant TimelineDB as SQLite Timeline Repo (SHA-256)
    participant TgBot as Owner Telegram Client

    Intruder->>WinLog: Enters Wrong Windows Password / PIN
    WinLog->>Monitor: Triggers Event ID 4625 (< 0.1s)
    Monitor->>StateEngine: is_feature_allowed("win_login_monitor")?
    StateEngine-->>Monitor: Allowed (WATCH_MODE / LOST_MODE)
    Monitor->>CamHardware: Capture Intruder Photo
    CamHardware-->>Monitor: Saved Photo Asset
    Monitor->>TimelineDB: record_event("FAILED_LOGIN", SHA256_Hash)
    TimelineDB-->>Monitor: Event Persisted with Cryptographic Hash
    Monitor->>TgBot: Send Photo Alert + Warning Caption
    TgBot-->>Monitor: Telegram 200 OK Response
```

---

## 🧙 Guided Recovery Wizard Sequence Graph

```mermaid
sequenceDiagram
    autonumber
    participant Owner as Device Owner
    participant Wiz as Recovery Wizard UI
    participant StateSvc as DeviceStateService
    participant WinLock as Windows LockWorkstation
    participant EvidEngine as Evidence Collector
    participant RepGen as Report Generator Service

    Owner->>Wiz: Launch Recovery Wizard
    Wiz->>StateSvc: Step 1: Transition State to LOST_MODE
    StateSvc-->>Wiz: State Updated & Audited
    Wiz->>WinLock: Step 2: Lock Workstation Session
    WinLock-->>Wiz: Session Locked
    Wiz->>EvidEngine: Step 3: Trigger Evidence Snapshot
    EvidEngine-->>Wiz: Photo + Screenshot + SHA-256 Hashed
    Wiz->>RepGen: Step 4: Generate Forensic Report
    RepGen-->>Wiz: PDF & JSON Forensic Report Exported
    Wiz-->>Owner: Step 5: Guidance & Recovery Advice Complete
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
