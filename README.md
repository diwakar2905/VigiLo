# 🔒 WATCHDOG

A lightweight, hidden background service that captures photos of intruders attempting to access your Windows laptop with wrong passwords. Plus, a remote command center controlled via Telegram.

Detailed Explanation on [Medium Article](https://medium.com/@drizzlehx/catch-me-if-you-can-building-an-offensive-anti-theft-system-for-windows-58e65fc4c672)

## ✨ Features

- 🚀 **Instant Detection** - Detects failed login attempts in 0.1 seconds
- 📸 **Fast Capture** - Takes photo in 0.5 seconds using webcam
- 📱 **Remote Command Center** - Control your PC via Telegram (`/capture`, `/screen`, `/locate`...)
- 👻 **Hidden Execution** - Runs completely invisible in background
- 🔄 **Auto-Restart** - Survives crashes with 999 retry attempts
- 🌐 **Offline Queue** - Saves photos when offline, uploads when connected
- 🔐 **Boot Protection** - Starts before login on every boot (SYSTEM privileges)
- 📡 **WiFi & Geo Location** - Triangulate location using nearby WiFi networks
- ⚡ **Zero Maintenance** - Set it and forget it

## 📋 Requirements

- Windows 10/11
- Telegram Bot Token & Chat ID (See guide below)

---

## 🛠️ Step 1: Create Telegram Bot

Before installing, you need a Telegram Bot to receive alerts.

1.  Open Telegram and search for **@BotFather**.
2.  Send the message `/newbot`.
3.  Follow the instructions to name your bot.
4.  **BotFather** will give you a **Token** (e.g., `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`).
5.  **Copy this Token**.

## 🆔 Step 2: Get Your Chat ID

You need your unique Chat ID so the bot knows where to send the photos.

1.  Search for your new bot in Telegram and click **Start**.
2.  Send any message to your bot (e.g., "Hello").
3.  Open your browser and visit this link (replace `<YOUR_BOT_TOKEN>` with the token from Step 0):
    ```
    https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
    ```
4.  Look for a result like this:
    ```json
    "chat": {
        "id": 123456789,
        "first_name": "YourName",
        ...
    }
    ```
5.  **Copy the numbers** (`123456789`). This is your **Chat ID**.

---

## 🚀 Step 3: Installation

1.  Download the **`WatchDog_Installer_v3.rar`**
2.  Extract it in a folder.
3.  Run the installer.
4.  Enter your **Bot Token** and **Chat ID** when prompted.
5.  Click **Install**.

That's it! WatchDog is now protecting your system.

---

## 🎮 Remote Commands (Commander)

Once installed, you can send these commands to your bot:

| Command | Description |
| :--- | :--- |
| `/ping` | Check if the system is online and listening. |
| `/capture` | Instantly take a photo using the webcam. |
| `/listen [sec]` | 🎤 Record audio from microphone (default 5s). |
| `/screen` | Take a silent screenshot of the desktop. |
| `/stat` | Get System Statistics (CPU, RAM, Battery, Boot Time). |
| `/locate` | Get location report (IP + WiFi Triangulation). |
| `/ls`, `/cd` | 📂 Browse files on the system. |
| `/download [file]` | ⬇️ Download a file from the laptop. |
| `/lock` | Instantly lock the workstation. |
| `/msg "text"` | Pop up a notepad message on the screen (e.g., "Hello Thief"). |
| `/help` | Show list of available commands. |

## 🛡️ How It Works

1. **System Service (WatchDog)**: Runs as `SYSTEM` on boot. Watches Windows Security Log for `Event 4625` (Wrong Password). Triggers webcam capture on detection.
2. **User Agent (Commander)**: Runs as `User` on login. Polls Telegram for commands. Executes user-context actions (screenshot, notepad, etc.).

## 🐛 Troubleshooting

### Commander commands not working?
- The Commander only runs **after** a user logs in (it needs a desktop session for screenshots/GUI).
- Ensure `AntiTheft_Commander` task is running.

### Monitor not starting after shutdown?
- Disable Windows Fast Startup in Power Options.
- Check `C:\Program Files\WatchDog\monitor.exe` exists.

## 📝 License

MIT License - Feel free to use and modify

---

**Made by drizzlehx**
