# 📖 VigiLo User Guide — Commercial Device Security & Recovery Control Center

Welcome to **VigiLo**, a privacy-first, local-first Windows Device Recovery Platform. This user guide will help you set up, navigate, and utilize VigiLo to protect your laptop against unauthorized access and loss.

---

## 🎯 Quick Navigation
- [1. Getting Started & Device States](#1-getting-started--device-states)
- [2. Device Control Center Overview](#2-device-control-center-overview)
- [3. Using the Forensic Timeline Workbench](#3-using-the-forensic-timeline-workbench)
- [4. Guided 6-Step Device Recovery Wizard](#4-guided-6-step-device-recovery-wizard)
- [5. Device Pairing & Telegram Alerts](#5-device-pairing--telegram-alerts)
- [6. Troubleshooting & Diagnostics](#6-troubleshooting--diagnostics)

---

## 1. Getting Started & Device States

VigiLo operates using a deterministic **3-State Guard Engine**:

1. **`DISARMED` (Privacy & Maintenance Mode)**:
   - All background monitoring and hardware sensors are disabled.
   - Use this mode during normal laptop usage when you do not need active theft protection.
2. **`WATCH_MODE` (Active Local Intruder Guard)**:
   - Monitors Windows Event Log ID 4625 (Failed Logon attempts).
   - Captures an intruder photo using your webcam on an incorrect PIN or password.
   - Sends real-time Telegram / Webhook alerts to your phone.
   - *Intrusive actions (lock, location, screenshots) are prohibited in Watch Mode to prevent false alarms.*
3. **`LOST_MODE` (Full Device Recovery Mode)**:
   - Activated if your laptop is lost or stolen.
   - Immediately locks the workstation, captures desktop screenshots, and triangulates WiFi location.
   - Generates a signed, tamper-evident forensic PDF report for law enforcement.

---

## 2. Device Control Center Overview

The **Device Control Center** (`DeviceControlCenterApp`) provides an intuitive desktop interface designed according to Microsoft Fluent Design principles:

### Security Widgets Included
- **Device Health Card**: Displays Device Name, Public ID (`VIGI-xxxx`), Device State, and Protection Status (`PROTECTED`, `WARNING`, `CRITICAL`).
- **Runtime Status Widget**: Live health indicators for background services (Event Monitor, Camera, Vault, Audit Logger, Upload Queue).
- **System Health Widget**: Real-time CPU usage, RAM footprint, Disk Free space, and Windows Defender status.
- **Quick Recovery Actions Panel**: Fast buttons for Workstation Lock, Photo Capture, Desktop Screenshot, Forensic PDF Report, and launching the Guided Recovery Wizard.
- **Self-Test Diagnostics Launcher**: One-click diagnostic button testing 8 system probes (`PASS`, `WARNING`, `FAILED`).
- **Notification Center Widget**: Tracks active notification delivery queues and offline retries.

---

## 3. Using the Forensic Timeline Workbench

The **Forensic Timeline Workbench** allows you to reconstruct intrusion attempts step-by-step:

- **16 Supported Event Categories**: Inspect `FAILED_LOGIN`, `CAMERA_CAPTURE`, `SCREENSHOT`, `POLICY_VIOLATION`, `TAMPER_DETECTION`, and more.
- **Instant Full-Text Search**: Search by Incident ID, User Session, or Description in **< 50ms**.
- **Multi-Filter Controls**: Filter events by Severity (`CRITICAL`, `HIGH`, `WARNING`, `INFO`), Event Category, or Bookmarked status.
- **Multi-Tab Evidence Inspector**: Click any event card to inspect Overview metadata, Media Assets (webcam photos), SHA-256 Hashes, and Raw Windows Audit Logs.
- **Signed Investigation Export**: Save your investigation log as a signed JSON file for records.

---

## 4. Guided 6-Step Device Recovery Wizard

If your laptop is lost or stolen, launch the **Guided Recovery Wizard** (`Wizard -> Launch Recovery Wizard`):

1. **Step 1: Incident Summary**: Review device identity, last seen timestamp, battery level, network state, and location.
2. **Step 2: Select Recovery Goals**: Choose plain-language goals (`Locate Device`, `Collect Photo Evidence`, `Lock Workstation`, `Generate Report`).
3. **Step 3: Execute Actions**: Watch real-time execution progress with automatic retry handling.
4. **Step 4: Evidence Summary**: Review gathered webcam photos, screenshots, timeline logs, and SHA-256 integrity digests.
5. **Step 5: Generate Forensic PDF Report**: Export a signed digital forensic PDF report complete with cryptographic hash seals.
6. **Step 6: Recovery Completed**: Follow reassuring post-recovery recommendations (`Reset Windows Credentials`, `Enable Watch Mode`, `Backup Evidence PDF`, `Contact Law Enforcement`).

---

## 5. Device Pairing & Telegram Alerts

To receive intruder alerts on your mobile phone:
1. Open VigiLo Settings and generate a **Device Pairing QR Code**.
2. Scan the QR code or send your pairing challenge token to your private VigiLo Telegram Bot.
3. Once paired, VigiLo will dispatch real-time alerts with intruder photos whenever an incorrect PIN is entered on your laptop.

---

## 6. Troubleshooting & Diagnostics

If you encounter issues:
- **Run Diagnostics**: Click `Run Diagnostics` in the Control Center `Self-Test Diagnostics` tab.
- **Check Audit Logs**: Open the `Forensic Timeline Workbench` tab to inspect raw system events.
- **Architecture Validation**: Run `$env:PYTHONPATH="."; python scripts/security_validation.py` to audit security gateway compliance.
