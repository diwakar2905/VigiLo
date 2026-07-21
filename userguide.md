# 🐕 WatchDog Security - End-User Guide & Documentation

Welcome to the **WatchDog Security** user guide. WatchDog is a lightweight, stealth anti-theft and monitoring suite designed for Windows 10 and 11. It operates silently in the background, instantly capturing webcam photographs of unauthorized individuals attempting to guess your password, and providing a powerful, remote Telegram-based command center to monitor and control your device from anywhere in the world.

---

## 📖 Table of Contents
1. [System Architecture Overview](#-system-architecture-overview)
2. [Prerequisites & Requirements](#-prerequisites--requirements)
3. [Setup Step 1: Create a Telegram Bot](#-setup-step-1-create-a-telegram-bot)
4. [Setup Step 2: Get Your Chat ID](#-setup-step-2-get-your-chat-id)
5. [Setup Step 3: Installation Methods](#-setup-step-3-installation-methods)
6. [Configuration Guide (`config.json`)](#-configuration-guide-configjson)
7. [Telegram Remote Commander Reference](#-telegram-remote-commander-reference)
8. [Advanced Windows Auditing configuration](#-advanced-windows-auditing-configuration)
9. [Troubleshooting & FAQs](#-troubleshooting--faqs)
10. [Uninstallation](#-uninstallation)

---

## ⚙️ System Architecture Overview

WatchDog is split into two independent, lightweight components to maximize system privilege access while maintaining access to the logged-in user's desktop session:

1. **WatchDog Secure Monitor (`--service`)**
   * **Privilege Level:** `SYSTEM` (highest system privilege)
   * **Trigger:** Starts on system boot, before any user logs in.
   * **Function:** Monitors the Windows Security Event Log for failed logon attempts (`Event ID 4625`). The moment a failure threshold is crossed, it takes a silent webcam photo, stores it in an offline queue, and uploads it to Telegram as soon as an internet connection is detected.

2. **WatchDog Commander (`--commander`)**
   * **Privilege Level:** `User` (under the active logged-in user session)
   * **Trigger:** Starts automatically upon user logon.
   * **Function:** Runs an invisible long-polling loop with Telegram. It executes user-context commands such as taking screenshots, recording audio, running pop-up dialogs, checking hardware metrics, browsing files, and locking the system.

```
                  ┌───────────────────────────────────────────┐
                  │            Windows Boot Event             │
                  └─────────────────────┬─────────────────────┘
                                        │
                                        ▼
                  ┌───────────────────────────────────────────┐
                  │       WatchDog Monitor Service (SYSTEM)   │
                  │   - Watches Event Log for Failed Logins   │
                  │   - Triggers Webcam Photo on Intrusion    │
                  └─────────────────────┬─────────────────────┘
                                        │
                         [If Windows Password Fails]
                                        │
                                        ▼
                  ┌───────────────────────────────────────────┐
                  │       Offline Queue -> Send to Telegram   │
                  │              (Webcam Photo)               │
                  └───────────────────────────────────────────┘
```

---

## 📋 Prerequisites & Requirements

Before deploying WatchDog, ensure your laptop/PC meets the following:
* **Operating System:** Windows 10 or Windows 11 (64-bit recommended).
* **Hardware:**
  * An integrated or USB-connected webcam (for intruder/remote photography).
  * A working microphone (for remote audio listening).
  * Wireless network card (optional, required for precise WiFi triangulation mapping).
* **Software/Network:**
  * Active internet connection (needed for real-time Telegram uploads).
  * Administrator permissions on the PC during setup to create system tasks.

---

## 🤖 Setup Step 1: Create a Telegram Bot

WatchDog alerts and photos are sent directly to your phone via a private Telegram bot. Setting it up takes less than 2 minutes:

1. Open Telegram on your phone or desktop.
2. Search for **@BotFather** (ensure it has the official blue verification badge).
3. Send the command: `/newbot`
4. Enter a display name for your bot (e.g., `My Laptop WatchDog`).
5. Choose a unique username for your bot. It **must** end in `bot` (e.g., `john_laptop_security_bot`).
6. BotFather will reply with a congratulatory message containing your **HTTP API Access Token** (formatted like: `1234567890:ABCdefGhIJKlmNoPQRsTUVwxyZ1234_567a`).
7. **Copy this Token** somewhere safe.

---

## 🆔 Setup Step 2: Get Your Chat ID

The bot needs to know your personal Telegram user account ID so it sends notifications *only* to you.

1. Click the link to your new bot provided by @BotFather, or search for its username in Telegram.
2. Click **Start** or send a dummy message (e.g., `/start` or `Hello`).
3. Open a web browser and navigate to the following URL (replace `<YOUR_BOT_TOKEN>` with the token from Step 1):
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
   ```
4. Find the section in the JSON response matching your message. Look for the `chat` object:
   ```json
   "chat": {
       "id": 123456789,
       "first_name": "YourName",
       "type": "private"
   }
   ```
5. **Copy the chat ID numbers** (e.g., `123456789`). This is your **Chat ID**.

---

## 🚀 Setup Step 3: Installation Methods

> [!IMPORTANT]
> WatchDog requires administrator privileges to register system-level scheduled tasks and enable failed password audit policies.

### Option A: The Graphical Installer (Recommended)
1. Run the `setup_gui.py` script or launch the compiled installer executable.
2. If prompted, click **Relaunch as Admin** to elevate the installer.
3. Review and accept the End-User License Agreement.
4. In the **Telegram Credentials** screen:
   * Paste your **Bot Token**.
   * Paste your **Chat ID** (or click **Get My Chat ID** to open the updates page in your web browser).
   * Click **Test Connection** to send a test message to your Telegram account.
5. Click **Install Now**. The installer will:
   * Create the directory `C:\Program Files\WatchDog`
   * Copy the software binaries and create a default config file.
   * Register the scheduled tasks `AntiTheft_Service` and `AntiTheft_Commander` in Windows.
   * Start the background processes.

### Option B: PowerShell Installation (For Administrators)
If you prefer a command-line setup or want to deploy it silently:
1. Open PowerShell **as Administrator**.
2. Navigate to the folder containing the WatchDog setup files.
3. Run the setup script:
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force
   .\setup\setup.ps1
   ```
4. This script will configure logon failure logging, terminate prior instances, write configuration files, and install scheduled tasks in the background.

---

## ⚙️ Configuration Guide (`config.json`)

The config file is stored at `C:\Program Files\WatchDog\config.json`. You can modify it at any time using a text editor (requires Admin privileges):

```json
{
    "telegram": {
        "bot_token": "YOUR_BOT_TOKEN_HERE",
        "chat_id": "YOUR_CHAT_ID_HERE"
    },
    "security": {
        "failed_attempt_threshold": 2,
        "event_id": 4625,
        "check_interval_seconds": 0.1
    },
    "camera": {
        "device_index": 0
    }
}
```

### Configuration Parameters Detailed:

* **`telegram.bot_token`**: The HTTP API Token generated by Telegram's @BotFather.
* **`telegram.chat_id`**: Your unique Telegram user chat ID.
* **`security.failed_attempt_threshold`**: The number of consecutive incorrect passwords before the webcam is triggered. Recommended: `2` (prevents capture on simple accidental typos).
* **`security.event_id`**: The Windows Event ID code representing failed logon attempts. Leave at `4625` (standard Windows logon failure).
* **`security.check_interval_seconds`**: How frequently the service checks the Windows Event Viewer security log. Default is `0.1` seconds for near-instantaneous capture.
* **`camera.device_index`**: The camera hardware index. Default is `0` (built-in laptop webcam). If your laptop has multiple cameras, change to `1` or `2` to target the correct front-facing sensor.

> [!NOTE]
> Restart the computer or restart the scheduled tasks using Task Scheduler after modifying `config.json` for changes to take effect.

---

## 🎮 Telegram Remote Commander Reference

Once installed, you can send commands directly to your private bot. Tap the menu button in the chat or type the following:

| Command | Arguments | Description | Context / Privilege |
| :--- | :--- | :--- | :--- |
| **`/ping`** | None | Verifies if the laptop is powered on, connected to the internet, and listening. | User |
| **`/capture`** | None | Takes an instant webcam photo and sends it to your chat. | User |
| **`/screen`** | None | Takes a silent screenshot of the primary monitor and uploads it. | User |
| **`/locate`** | None | Geolocation lookup. Resolves the external IP-address geo-coordinates (Google Maps link) and runs a command to scan nearby Wi-Fi network SSIDs and hardware MAC addresses (BSSIDs). | User |
| **`/stat`** | None | Fetches real-time telemetry: CPU utilization, Memory usage (RAM), Disk storage space left on Drive C, Battery level (and charging status), OS version, and system Boot Time. | User |
| **`/listen`** | `[seconds]` | Silent microphone capture. Records surrounding audio for a specified duration (default: `5` seconds, maximum: `30` seconds) and sends it as an audio message. | User |
| **`/lock`** | None | Immediately logs off the active desktop user and locks the Windows workstation. | User |
| **`/msg`** | `[your text]` | Triggers an intrusive popup dialog box containing your message on the thief's screen. The laptop speaker will read out loud "Incoming Security Alert" followed by your message via Text-to-Speech (TTS). | User |
| **`/ls`** | `[directory]` | Directory browser. Lists the folders and files in the specified path (or default folder if left blank). | User |
| **`/cd`** | `[directory]` | Changes the active directory path for subsequent operations. | User |
| **`/download`**| `[filepath]` | Initiates download of the specified file directly to your Telegram chat. | User |
| **`/help`** | None | Lists all available commands. | User |

> [!TIP]
> **Using WiFi Geolocation Triangulation:** If the `/locate` command returns nearby BSSIDs (e.g. `00:1A:2B:3C:4D:5E`), copy these MAC addresses and enter them into database sites such as [Wigle.net](https://wigle.net) to locate your device within meters, even when GPS is disabled on the laptop.

---

## 🛡️ Advanced Windows Auditing Configuration

WatchDog relies on the Windows Security log. Under default settings in some clean installs of Windows 10/11 Home or Enterprise, logon failure auditing might be turned off. The installer automatically attempts to enable it, but you can verify it manually:

### Verification via Command Line:
1. Open Command Prompt as Administrator.
2. Run:
   ```cmd
   auditpol /get /subcategory:"Logon"
   ```
3. Look for the **Failure** column. It must be set to **Success and Failure** or **Failure**.

### Manual Activation via Group Policy Editor (Windows Pro/Enterprise):
1. Press `Win + R`, type `gpedit.msc`, and press Enter.
2. Navigate to:
   * `Computer Configuration` -> `Windows Settings` -> `Security Settings` -> `Advanced Audit Policy Configuration` -> `System Audit Policies - Local Group Policy Object` -> `Logon/Logoff`
3. Double-click on **Audit Logon**.
4. Check both **Configure the following audit events** and select **Success** and **Failure**.
5. Click **Apply** and **OK**.

---

## 🐛 Troubleshooting & FAQs

### Q: Why are my remote commands (like `/screen` or `/msg`) not responding?
**A:** The WatchDog Commander (`--commander`) runs inside the logged-in user's desktop session. If the laptop is sitting at the lock screen (no user logged in), or the laptop is shut down/asleep, user-context commands cannot execute. However, the background Monitor service (`--service`) remains active at the lock screen under the `SYSTEM` account, and will still capture and queue webcam photos if an incorrect password is entered.

### Q: An intruder attempted to access the machine, but I didn't receive an alert.
**A:**
1. Check if the laptop is offline. If the device has no internet access, the photo is safely queued in `%PROGRAMDATA%\AntiTheftCaptures`. It will automatically upload as soon as the laptop connects to a network.
2. Verify that logon failure auditing is enabled (see [Advanced Windows Auditing Configuration](#-advanced-windows-auditing-configuration)).
3. Make sure the webcam isn't physically covered or in use by another application.

### Q: How do I prevent WatchDog from starting up?
**A:** If you need to temporarily pause protection:
1. Press `Win + R`, type `taskschd.msc`, and press Enter.
2. Click **Task Scheduler Library**.
3. Locate `AntiTheft_Service` or `AntiTheft_Commander`, right-click on them, and select **Disable**.

---

## ❌ Uninstallation

To remove all traces of WatchDog from your system:

### Method A: Automated Uninstaller
1. Go to the installation folder: `C:\Program Files\WatchDog`.
2. Double-click `uninstall.exe`.
3. If prompted, grant Admin approval.
4. Click the **Uninstall** button. The application will terminate running WatchDog tasks, delete registry scheduled tasks, wipe the installation directory, and clear any remaining captured photos.

### Method B: Manual Cleanup
If you wish to do this manually:
1. Open PowerShell as Administrator.
2. Force-stop the processes:
   ```powershell
   taskkill /F /IM WatchDog.exe
   taskkill /F /IM monitor.exe
   ```
3. Remove the scheduled tasks:
   ```powershell
   schtasks /Delete /TN "AntiTheft_Service" /F
   schtasks /Delete /TN "AntiTheft_Commander" /F
   ```
4. Delete the install folder and the cached captures folder:
   ```powershell
   Remove-Item -Recurse -Force "C:\Program Files\WatchDog"
   Remove-Item -Recurse -Force "C:\ProgramData\AntiTheftCaptures"
   ```
