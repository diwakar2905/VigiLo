# 🔒 WatchDog

[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-blue.svg)](#)
[![Version](https://img.shields.io/badge/Version-3.0.0-blueviolet.svg)](CHANGELOG.md)
[![Contributions Welcome](https://img.shields.io/badge/Contributions-Welcome-brightgreen.svg)](CONTRIBUTING.md)

WatchDog is a **production-grade Windows security agent** that monitors unauthorized access attempts. When someone triggers a wrong password attempt, WatchDog captures an intruder photo via the device webcam, logs system telemetry, and sends immediate alerts to your private Telegram channel. 

It also functions as an encrypted remote command center, allowing you to lock, monitor, and query your device from anywhere via Telegram chat.

> [!IMPORTANT]
> **Privacy First**: WatchDog is completely self-hosted at the application layer. Your Telegram Bot Token, Chat ID, and captured files are stored locally on your device using Windows DPAPI encryption and uploaded directly to Telegram. No data is ever sent to the developers or third-party servers.

---

## ✨ Features at a Glance

*   🚀 **failed Login Detection**: Scans Windows Event Log for `Event 4625` (Wrong Password) and alerts you in **0.1 seconds**.
*   📸 **Webcam Intruder Capture**: Captures intruder photos instantly using OpenCV DirectShow warm-up optimizations.
*   🔒 **DPAPI Secrets Shield**: Encrypts Telegram Bot Tokens and Chat IDs on disk using the native Windows Data Protection API.
*   🛡️ **Folder Anti-Hijack**: Restricts installation folder permissions to SYSTEM and Administrators to prevent DLL injection attacks.
*   ⛓️ **Named Mutex locks**: Prevents duplicate process conflicts over camera and network resources.
*   🔄 **Auto-Recovery**: Automatically re-anchors event pointers on log clears to prevent high-CPU exception loops.
*   🌐 **Offline Queue**: Saves captured images locally when offline, uploading them as soon as internet connection returns.

---

## 🎮 Remote Commands (Telegram Commander)

Control your device from anywhere by sending these commands directly to your configured Telegram bot:

| Command | Icon | Description |
| :--- | :---: | :--- |
| `/ping` | 📡 | Check if the agent is online and listening. |
| `/capture` | 📸 | Instantly take a photo using the webcam. |
| `/listen [sec]`| 🎤 | Record audio from the microphone (default 5s). |
| `/screen` | 🖥️ | Take a silent screenshot of the desktop. |
| `/stat` | 📊 | Get CPU, RAM, Disk space, Battery level, and Boot time. |
| `/locate` | 📍 | Triangulate device location (IP GeoIP + WiFi spectrum scan). |
| `/ls`, `/cd` | 📂 | Browse files securely (sandboxed to User Profile). |
| `/download [file]`| ⬇️ | Download files from the device. |
| `/lock` | 🔒 | Instantly lock the Windows workstation. |
| `/msg "text"` | 🔔 | Display a popup and play a text-to-speech alert on screen. |
| `/help` | ❓ | View help details. |

---

## 🏗️ Clean Architecture Directory Layout

WatchDog is structured according to Clean Architecture standards:

```
WatchDog/
├── api/             # Outbound Telegram API clients
├── config/          # Configuration schema models and managers
├── core/            # System monitors, lifecycle engines, and deployment engines
├── logs/            # Rotating file logs manager (5MB bounds)
├── modules/         # Modular features (camera, audio, screenshot, files, locate)
├── security/        # DPAPI encryption, path sanitizers, and UAC controls
├── services/        # Telegram Poller and offline upload queue workers
├── setup/           # PyInstaller spec files, icons, and compilation script
├── ui/              # Dark stylesheet and wizard UI screens
├── dist/            # Compiled binaries output folder
├── main.py          # Unified entry point launcher
└── requirements.txt # Python package requirements
```

---

## 🛠️ Step-by-Step Installation

### 1. Create a Telegram Bot
1. Open Telegram and search for the official [**@BotFather**](https://t.me/BotFather).
2. Send the command `/newbot`.
3. Choose a display name and username (must end in `bot`, e.g., `MyWatchDogBot`).
4. Copy the generated **Bot Token**.

### 2. Retrieve Your Chat ID
1. Search for your new bot on Telegram and click **Start**.
2. Send any message (e.g. "Hello") to the bot.
3. Open your browser and visit:
   `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Copy the `id` value under the `chat` block (e.g., `123456789`).

### 3. Run the Installer Wizard
1. Download and run [**`WatchDog_Setup.exe`**](dist/WatchDog_Setup.exe).
2. Accept the EULA terms.
3. Paste your **Bot Token** and **Chat ID**.
4. Click **Install** to deploy.

---

## 💻 Developer Guide (Local Compilation)

To compile the service, uninstaller, and setup executables locally, run:
```bash
pip install -r requirements.txt pyinstaller
python setup/install_startup.py
```
This builds three executables inside the `dist/` directory:
1.  `WatchDog.exe` - Service payload.
2.  `uninstall.exe` - Uninstaller.
3.  `WatchDog_Setup.exe` - Installer (which bundles both payloads).

---

## 🤝 Contributing

We love contributions! Whether you want to fix a bug, improve performance, add new remote commands, or design a new UI dashboard, you are welcome here.

### How to Get Started:
1.  Review our [Contributing Guidelines](CONTRIBUTING.md) to understand our directory layout and security rules.
2.  Fork the repository and clone it to your local machine.
3.  Create a branch for your feature: `git checkout -b feature/cool-new-idea`.
4.  Make your changes, ensure they conform to SOLID principles, and run a compilation test (`python setup/install_startup.py`).
5.  Open a Pull Request (PR) describing what you changed.

> [!TIP]
> **Check Out Open Issues**: Look at our open issues list or start a discussion if you want to suggest new features or help with existing tasks!

---

## 🛡️ Security
If you discover a security vulnerability, please review our [Security Policy](SECURITY.md) for instructions on how to report it privately. Do not open public issues for security vulnerabilities.

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).

---

**Made with 🐕 by drizzle&middot;hx and the WatchDog Open Source Contributors.**
