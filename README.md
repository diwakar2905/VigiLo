# 🛡️ VigiLo

### Privacy-First Windows Intrusion Detection & Device Recovery Platform

Know immediately when someone tries to access your Windows PC. Capture evidence automatically. Recover your device with confidence.

---

![VigiLo Banner](setup/vigilo_logo.png)

---

## ⚡ Highlights

✅ **Detects Failed Logins**: Inspects Security logs for wrong passwords in real-time.

✅ **Webcam Evidence**: Auto-captures camera photos of the intruder.

✅ **Encrypted Telegram Alerts**: Streams warning photos and stats directly to your private chat.

✅ **Open Source & Privacy First**: No external servers, no telemetry, no tracking.

---

## 🚀 Quick Start

1.  **Create a Telegram Bot**: Message [@BotFather](https://t.me/BotFather) on Telegram and send `/newbot` to get your Token.
2.  **Retrieve Chat ID**: Send a message to your new bot, then visit `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` to get your ID.
3.  **Run Installer**: Run [**`VigiLo_Setup.exe`**](dist/VigiLo_Setup.exe) from the `dist` folder.
4.  **Configure**: Enter your Token and Chat ID inside the installation wizard.
5.  **Validate**: Verify the agent is listening by sending the `/ping` command over Telegram.

---

## ❓ Why VigiLo?

Losing a laptop is stressful. Most Windows devices provide limited evidence when someone attempts unauthorized access.

VigiLo continuously monitors your system for intrusion events and immediately collects evidence such as:
*   Failed login attempt timestamps
*   Webcam capture photo files of the intruder
*   Detailed machine resource statistics
*   Network-based geolocation data

Everything is delivered directly to your private Telegram bot. **No cloud required.**

---

## 🔒 Privacy First

*   **Zero Analytics**: VigiLo does not collect usage telemetry.
*   **Local Storage**: Temporary buffered images reside solely in your local profiles.
*   **Direct Delivery**: All photos and audits are uploaded directly from your machine to Telegram's secure API. You remain in complete control of your data.

---

## 🔒 Why You Can Trust VigiLo

*   **Fully Open Source**: Every line of code is auditable by the community.
*   **No Telemetry**: VigiLo never collects or reports user usage metrics.
*   **No Proprietary Cloud**: You run your own command node without third-party databases.
*   **DPAPI Shielded**: Sensitive configuration credentials are encrypted using native Windows session keys.
*   **Independent Auditing**: Security issues can be reported privately under coordinated disclosure policies.
*   **Designed for Transparency**: Code verification, build steps, and tests are open for public review.

---

## 📋 Feature Comparison

| Feature | VigiLo | Standard OS Tools | Traditional Antivirus |
| :--- | :---: | :---: | :---: |
| **Open Source** | ✅ Yes | ❌ No | ❌ No |
| **Telegram Alerts** | ✅ Yes | ❌ No | ❌ No |
| **Offline Buffering** | ✅ Yes | ❌ No | ❌ No |
| **Webcam Evidence** | ✅ Yes | ❌ No | ❌ No |
| **Privacy First** | ✅ Yes | ❌ No | ❌ No |

---

## 🛠️ Performance Metrics

*   **Idle CPU Usage**: `< 1.0%`
*   **Memory Footprint**: `~35 MB`
*   **Service Startup Time**: `< 2.0s`
*   **Network Overhead**: Zero idle network traffic; bandwidth is only consumed when events occur or commands are received.

---

## 🧱 Threat Model Boundaries

### Designed For:
*   ✔ Stolen or lost laptop recovery
*   ✔ Unauthorized physical local access checks
*   ✔ Tracking failed password login entries
*   ✔ Silent remote desktop screenshots

### Not Designed For:
*   ✘ Defeating nation-state target exploits
*   ✘ Active kernel-level rootkit detection
*   ✘ Replacing full endpoint antivirus software
*   ✘ Hardware disk-encryption management

---

## 📐 System Architecture

### High-Level Component View
```
Windows Security Log
        │
        ▼
   VigiLo Service
        │
        ▼
  Runtime Host
        │
 ┌──────┼────────┐
 │      │        │
 ▼      ▼        ▼
Camera Queue Telegram
        │
        ▼
    Audit Log
```

### Detailed Execution Flow
```mermaid
sequenceDiagram
    autonumber
    actor Intruder
    participant WinOS as Windows Security Log
    participant Monitor as VigiLo Service (SYSTEM)
    participant Camera as Webcam (DirectShow)
    participant Queue as Offline Upload Queue
    participant Telegram as Telegram Bot API

    Intruder->>WinOS: Failed login attempt (Event ID 4625)
    loop Every 0.1 seconds
        Monitor->>WinOS: Scan events
    end
    WinOS-->>Monitor: Forward Event 4625
    Note over Monitor: Threshold met (2 failures)
    Monitor->>Camera: Trigger webcam capture
    Camera-->>Monitor: Save capture to local folder
    Monitor->>Queue: Add file to queue buffer
    alt System is online
        Queue->>Telegram: Post captured photo
        Telegram-->>Queue: HTTP 200 Success
    else System is offline
        Note over Queue: Retain photo in captures folder
        Queue->>Queue: Poll for connection recovery
    end
```

For the detailed specifications, see the **[VigiLo Engineering & Product Bible](docs/README.md)**.

---

## 📂 Documentation

Quickly access our comprehensive product specifications and engineering handbooks:

*   📖 **[Master Index](docs/README.md)**: Product overview and handbook navigation structure.
*   📐 **[System Architecture](docs/02_architecture_and_core.md)**: System topology, configuration platforms, and service managers.
*   💻 **[Developer Guide](docs/01_vision_and_prd.md)**: Requirements, setup guides, and personae definitions.
*   🛠️ **[Engineering Handbook](docs/04_engineering_and_standards.md)**: Coding conventions, SOLID rules, and design patterns.
*   🤝 **[Contributing Guidelines](docs/06_open_source_and_adr.md)**: Repository branching, PR templates, and ADR guidelines.
*   🚀 **[Future Roadmap](docs/08_ai_and_cto_handbook.md)**: CTO decisions lists and long-term milestones.

---

## 🚀 Roadmap

*   [x] Supervised Service Runtime Platform (Phase 3)
*   [x] Unified Security Matrix Core (Phase 2)
*   [x] Atomic Configuration Manager (Phase 1)
*   [ ] Windows IPC Pipe Interface
*   [ ] Graphical Control Panel Dashboard
*   [ ] Enterprise Policy Templates (AD GPOs)

---

## 💬 Frequently Asked Questions (FAQ)

#### Does VigiLo require an active internet connection?
VigiLo runs offline. If a login attempt occurs while offline, it buffers the photos locally and uploads them automatically when connection is restored.

#### Can I self-host the command channel?
Yes. All alerts are routed directly to your private Telegram bot using the custom Token you control.

#### Is Administrator access required?
Yes. Administrative privileges are required to parse the Windows Security Event Channel.

---

## 🛡️ Security Vulnerabilities
If you identify a security issue, please do not create a public issue. Review and follow the instructions in our [SECURITY.md](SECURITY.md) guidelines. Responsible disclosure is highly appreciated.

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).

---

**Made with 🐕 by Diwakar Mishra and the VigiLo Open Source Contributors.**
