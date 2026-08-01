import threading
import time
import requests
import json
import os
import ctypes
import sys
from datetime import datetime

# Global configuration
BOT_TOKEN = None
CHAT_ID = None
CAPTURES_DIR = None
CONFIG = None
CONTAINER = None

def init_commander(config, captures_dir):
    global BOT_TOKEN, CHAT_ID, CAPTURES_DIR, CONFIG, CONTAINER
    CONFIG = config
    BOT_TOKEN = config['telegram']['bot_token']
    CHAT_ID = str(config['telegram']['chat_id'])
    CAPTURES_DIR = captures_dir

    if not getattr(sys, 'frozen', False):
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from src.core.controllers.container import ServiceContainer
        CONTAINER = ServiceContainer.get_instance()
    except Exception as e:
        print(f"[WARN] Commander ServiceContainer note: {e}")
        CONTAINER = None

def send_reply(text):
    """Send text reply to Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, json=payload, timeout=10)
    except:
        pass

def send_photo(photo_path, caption=None):
    """Send photo to Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        with open(photo_path, "rb") as f:
            files = {"photo": f}
            data = {"chat_id": CHAT_ID}
            if caption:
                data["caption"] = caption
            requests.post(url, data=data, files=files, timeout=20)
    except Exception as e:
        print(f"[ERROR] Upload failed: {e}")

def execute_command(command_text):
    """Parse and execute commands"""
    cmd = command_text.lower().strip().split()
    if not cmd:
        return

    action = cmd[0]
    print(f"[CMD] Received command: {action}")

    if action == "/ping":
        send_reply("🏓 Pong! WatchDog is watching. System is online.")

    elif action == "/capture":
        # Lazy import to save RAM
        try:
            from service.camera import capture_intruder_file
        except ImportError:
            from camera import capture_intruder_file
        
        send_reply("📸 Capturing photo...")
        filepath = capture_intruder_file(CAPTURES_DIR, prefix="cmd_")
        if filepath:
            send_photo(filepath, "📸 Remote capture requested")
            try:
                os.remove(filepath)
            except:
                pass
        else:
            send_reply("❌ Camera unavailable")

    elif action == "/screen":
        send_reply("🖥️ Taking screenshot...")
        try:
            import pyautogui
            import pyautogui
            timestamp = int(time.time())
            filename = f"cmd_screen_{timestamp}.png" # Prefix cmd_ to avoid monitor auto-upload
            filepath = os.path.join(CAPTURES_DIR, filename)
            
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            
            send_photo(filepath, "🖥️ Desktop Screenshot")
            os.remove(filepath)
        except Exception as e:
            send_reply(f"❌ Screenshot failed: {e}")

    elif action == "/lock":
        send_reply("🔒 Locking workstation...")
        try:
            ctypes.windll.user32.LockWorkStation()
            send_reply("✅ System locked.")
        except Exception as e:
            send_reply(f"❌ Lock failed: {e}")

    elif action == "/msg":
        # Usage: /msg Hello Thief
        message = " ".join(cmd[1:])
        if message:
            send_reply(f"📢 Showing Dialog: '{message}'")
            
            def show_vbs_msg(msg):
                import subprocess
                try:
                    # Create a temporary VBS script
                    vbs_path = os.path.join(CAPTURES_DIR, "message.vbs")
                    # Escape quotes in message
                    safe_msg = msg.replace('"', '""')
                    
                    # Professional VBScript with Text-to-Speech and System Modal
                    vbs_content = f'''
                    Set Sapi = Wscript.CreateObject("SAPI.SpVoice")
                    Sapi.Rate = 0
                    Sapi.Volume = 100
                    
                    ' Announce message
                    Sapi.Speak "Incoming Security Alert"
                    
                    ' Show Dialog (SystemModal + Exclamation + TopMost)
                    ' 4096 = SystemModal (Always on top)
                    ' 48 = Exclamation Icon
                    MsgBox vbCrLf & "{safe_msg}" & vbCrLf & vbCrLf, 4144, "⚠️ WatchDog Security Alert"
                    
                    ' Read the message
                    Sapi.Speak "{safe_msg}"
                    '''
                    
                    with open(vbs_path, "w", encoding="utf-8") as f:
                        f.write(vbs_content)
                    
                    # Run VBScript
                    subprocess.Popen(["wscript", vbs_path])
                    
                except Exception as e:
                    print(f"[ERROR] Failed to show dialog: {e}")

            threading.Thread(target=show_vbs_msg, args=(message,)).start()
        else:
            send_reply("⚠️ Usage: /msg [Your Message]")
            
    elif action == "/locate":
        send_reply("📡 Scanning WiFi Spectrum & Geolocation...")
        
        def fetch_loc():
            import subprocess
            
            # 1. Scan Nearby WiFi Networks (Triangulation Data)
            wifi_list = []
            try:
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                output = subprocess.check_output(
                    ["netsh", "wlan", "show", "networks", "mode=bssid"], 
                    startupinfo=si, 
                    encoding="utf-8", 
                    errors="ignore"
                )
                
                current_ssid = "Unknown"
                for line in output.split("\n"):
                    line = line.strip()
                    if line.startswith("SSID"):
                        # Format: "SSID 1 : Name"
                        parts = line.split(":", 1)
                        if len(parts) > 1:
                            current_ssid = parts[1].strip()
                    elif line.startswith("BSSID"):
                        # Format: "BSSID 1 : 00:xx:..."
                        parts = line.split(":", 1)
                        if len(parts) > 1:
                            bssid = parts[1].strip()
                            wifi_list.append(f"📶 {current_ssid}\n   `{bssid}`")
                    elif line.startswith("Signal"):
                         # Add signal to last entry
                         if wifi_list:
                             parts = line.split(":", 1)
                             if len(parts) > 1:
                                 wifi_list[-1] += f" ({parts[1].strip()})"
            except Exception as e:
                wifi_list.append(f"Scan Error: {e}")

            # 2. Get IP & Geo
            try:
                info = requests.get("http://ip-api.com/json/", timeout=10).json()
                if info.get("status") == "success":
                    map_link = f"https://maps.google.com/?q={info['lat']},{info['lon']}"
                    
                    # Format WiFi Data (Top 8 strong signals)
                    wifi_report = "\n".join(wifi_list[:8]) if wifi_list else "No WiFi networks found."
                    
                    msg = (f"📍 *Detailed Location Report*\n"
                           f"--------------------------------\n"
                           f"🌍 *IP-Based Info*:\n"
                           f"   City: {info['city']}\n"
                           f"   ISP: {info['isp']}\n"
                           f"   IP: {info['query']}\n"
                           f"   🔗 [Google Maps]({map_link})\n\n"
                           f"📡 *Nearby WiFi (Triangulation Data)*:\n"
                           f"{wifi_report}\n\n"
                           f"_Copy BSSIDs to Wigle.net for precise coord_")
                    send_reply(msg)
                else:
                    send_reply(f"❌ Geo-IP Failed. WiFi Scan:\n" + "\n".join(wifi_list[:5]))
            except Exception as e:
                send_reply(f"❌ Err: {e}")
        
        threading.Thread(target=fetch_loc).start()

    elif action == "/stat" or action == "/stats":
        send_reply("📊 Fetching system statistics...")
        try:
            import psutil
            import platform
            
            # CPU
            cpu_freq = psutil.cpu_freq()
            freq_curr = f"{cpu_freq.current:.1f}Mhz" if cpu_freq else "N/A"
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Memory
            ram = psutil.virtual_memory()
            ram_total = f"{ram.total / (1024**3):.1f}GB"
            ram_used = f"{ram.used / (1024**3):.1f}GB"
            ram_percent = ram.percent
            
            # Disk
            disk = psutil.disk_usage('C:\\')
            disk_total = f"{disk.total / (1024**3):.1f}GB"
            disk_free = f"{disk.free / (1024**3):.1f}GB"
            
            # Battery
            battery = psutil.sensors_battery()
            batt_status = "N/A"
            if battery:
                plugged = "🔌 Plugged In" if battery.power_plugged else "🔋 On Battery"
                batt_status = f"{battery.percent}% ({plugged})"

            stats_msg = (
                f"📊 *System Statistics*\n"
                f"------------------------\n"
                f"💻 *System*: {platform.system()} {platform.release()}\n"
                f"🧠 *CPU*: {cpu_usage}% (Freq: {freq_curr})\n"
                f"💾 *RAM*: {ram_used} / {ram_total} ({ram_percent}%)\n"
                f"💿 *Disk (C:)*: {disk_free} free / {disk_total}\n"
                f"⚡ *Battery*: {batt_status}\n"
                f"⏱️ *Boot Time*: {datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')}"
            )
            send_reply(stats_msg)
        except Exception as e:
            send_reply(f"❌ Failed to fetch stats: {e}")

    elif action == "/listen":
        duration = 5
        if len(cmd) > 1 and cmd[1].isdigit():
            duration = int(cmd[1])
            if duration > 30: duration = 30 # Limit to 30s
            
        send_reply(f"🎤 Recording {duration}s of audio...")
        
        def record_audio_task(sec):
            try:
                import pyaudio
                import wave
                
                CHUNK = 1024
                FORMAT = pyaudio.paInt16
                CHANNELS = 1
                RATE = 44100
                
                p = pyaudio.PyAudio()
                stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
                
                frames = []
                # Record
                for i in range(0, int(RATE / CHUNK * sec)):
                    data = stream.read(CHUNK)
                    frames.append(data)
                    
                stream.stop_stream()
                stream.close()
                p.terminate()
                
                filename = f"audio_{int(time.time())}.wav"
                filepath = os.path.join(CAPTURES_DIR, filename)
                
                wf = wave.open(filepath, 'wb')
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
                wf.close()
                
                # Send
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendAudio"
                with open(filepath, 'rb') as f:
                    requests.post(url, data={"chat_id": CHAT_ID}, files={"audio": f}, timeout=60)
                
                try:
                    os.remove(filepath)
                except:
                    pass
                
            except ImportError:
                 send_reply("❌ PyAudio not installed on server.")
            except Exception as e:
                send_reply(f"❌ Audio Error: {e}")

        threading.Thread(target=record_audio_task, args=(duration,)).start()

    elif action == "/ls":
        try:
            path = " ".join(cmd[1:]) if len(cmd) > 1 else "."
            files = os.listdir(path)
            # Limit output
            msg = "📂 Files:\n" + "\n".join(files[:20])
            if len(files) > 20: msg += f"\n...and {len(files)-20} more."
            send_reply(msg)
        except Exception as e:
            send_reply(f"❌ Error: {e}")

    elif action == "/cd":
        try:
            path = " ".join(cmd[1:])
            os.chdir(path)
            send_reply(f"📂 Changed dir to: {os.getcwd()}")
        except Exception as e:
            send_reply(f"❌ Error: {e}")

    elif action == "/download":
        filename = " ".join(cmd[1:])
        if os.path.exists(filename) and os.path.isfile(filename):
            send_reply(f"⬇️ Uploading '{filename}'...")
            try:
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
                with open(filename, 'rb') as f:
                    requests.post(url, data={"chat_id": CHAT_ID}, files={"document": f}, timeout=60)
            except Exception as e:
                send_reply(f"❌ Upload failed: {e}")
        else:
            send_reply("❌ File not found.")


    elif action in ["/disarm", "/watch", "/lost", "/mode", "/status"]:
        if CONTAINER:
            from src.core.models.device_state import DeviceState
            if action == "/disarm":
                CONTAINER.device_state_service.transition_to(DeviceState.DISARMED, "User command", "TelegramOwner")
                send_reply("🟢 Device state updated to: DISARMED (Monitoring disabled)")
            elif action == "/watch":
                CONTAINER.device_state_service.transition_to(DeviceState.WATCH_MODE, "User command", "TelegramOwner")
                send_reply("🟡 Device state updated to: WATCH MODE (Intruder detection active)")
            elif action == "/lost":
                CONTAINER.device_state_service.transition_to(DeviceState.LOST_MODE, "User command", "TelegramOwner")
                send_reply("🚨 Device state updated to: LOST MODE (Full protection & recovery active)")
            elif action in ["/status", "/mode"]:
                curr = CONTAINER.device_state_service.get_current_state().value
                send_reply(f"🛡️ Current Device State: *{curr}*")
        else:
            send_reply("⚠️ Core Container unavailable")

    elif action == "/report":
        if CONTAINER:
            send_reply("📄 Generating Incident Forensic Report...")
            report = CONTAINER.report_service.generate_report()
            out_pdf = os.path.join(CAPTURES_DIR, f"report_{report.report_id}.pdf")
            generated = CONTAINER.report_service.export_pdf(report, out_pdf)
            
            try:
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
                with open(generated, 'rb') as f:
                    requests.post(url, data={"chat_id": CHAT_ID, "caption": f"📋 VigiLo Forensic Report {report.report_id}"}, files={"document": f}, timeout=60)
            except Exception as e:
                send_reply(f"❌ Report export failed: {e}")
        else:
            send_reply("⚠️ Core Container unavailable")

    elif action == "/timeline":
        if CONTAINER:
            events = CONTAINER.timeline_service.get_timeline(limit=10)
            lines = [f"⏱️ *Recent Timeline Incidents ({len(events)})*:"]
            for ev in events:
                lines.append(f"• `[{ev.timestamp[:19]}]` *{ev.event_type}*: {ev.description}")
            send_reply("\n".join(lines))
        else:
            send_reply("⚠️ Core Container unavailable")

    elif action == "/trust":
        if CONTAINER:
            perms = CONTAINER.trust_service.get_permission_descriptors()
            lines = ["🛡️ *VigiLo Trust & Transparency Panel*:"]
            for p in perms:
                status_icon = "✅" if p.is_granted else "❌"
                lines.append(f"{status_icon} *{p.name}*\n   _Why_: {p.justification}\n")
            send_reply("\n".join(lines))
        else:
            send_reply("⚠️ Core Container unavailable")

    elif action == "/diagnose":
        if CONTAINER:
            rep = CONTAINER.diagnostics_service.run_full_diagnostics()
            lines = [f"🩺 *VigiLo Self-Diagnostics Report ({rep.overall_status})*:"]
            for c in rep.checks:
                icon = "✅" if c.status == "HEALTHY" else ("⚠️" if c.status == "WARNING" else "❌")
                lines.append(f"{icon} *{c.component_name}*: {c.message}")
            send_reply("\n".join(lines))
        else:
            send_reply("⚠️ Core Container unavailable")

    elif action == "/identity":
        if CONTAINER:
            ident = CONTAINER.identity_service.get_identity()
            msg = (
                f"🔑 *VigiLo Permanent Device Identity*\n"
                f"--------------------------------\n"
                f"🆔 *Public ID*: `{ident.public_id}`\n"
                f"📌 *UUID*: `{ident.device_uuid}`\n"
                f"🔏 *Fingerprint*: `{ident.fingerprint[:24]}...`\n"
                f"📅 *Registered*: `{ident.created_at[:19]}`"
            )
            send_reply(msg)
        else:
            send_reply("⚠️ Core Container unavailable")

    elif action == "/pair":
        if CONTAINER:
            ch = CONTAINER.pairing_service.initiate_pairing("TelegramOwner")
            send_reply(f"🔗 *Device Pairing Initiated*\nChallenge ID: `{ch['challenge_id']}`\nNonce: `{ch['nonce']}`\nExpires in 5 minutes.")
        else:
            send_reply("⚠️ Core Container unavailable")

    elif action == "/help":
        help_text = (
            "🛡️ *VigiLo Device Recovery Platform Center*\n\n"
            "• /mode     - Show current Device State\n"
            "• /disarm   - Set state to DISARMED\n"
            "• /watch    - Set state to WATCH MODE\n"
            "• /lost     - Set state to LOST MODE\n"
            "• /diagnose - Run automated Self-Diagnostics\n"
            "• /identity - View Permanent Device Identity & Fingerprint\n"
            "• /pair     - Initiate Secure Device Pairing\n"
            "• /report   - Generate & send Incident Report\n"
            "• /timeline - View recent persistent incident log\n"
            "• /trust    - View Privacy & Permission Justifications\n"
            "• /ping     - Check system status\n"
            "• /capture  - Take intruder photo\n"
            "• /screen   - Take screenshot (Lost Mode)\n"
            "• /locate   - Get Geo & WiFi Triangulation\n"
            "• /lock     - Instantly Lock Workstation\n"
            "• /msg      - Display Emergency Screen Message"
        )
        send_reply(help_text)

def set_bot_commands():
    """Update the command menu in Telegram to match available commands"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands"
    commands = [
        {"command": "ping", "description": "Check status"},
        {"command": "capture", "description": "Take photo"},
        {"command": "listen", "description": "Record audio"},
        {"command": "screen", "description": "Take screenshot"},
        {"command": "locate", "description": "Get location"},
        {"command": "stat", "description": "System statistics"},
        {"command": "lock", "description": "Lock PC"},
        {"command": "ls", "description": "List files"},
        {"command": "cd", "description": "Change directory"},
        {"command": "download", "description": "Download file"},
        {"command": "msg", "description": "Show message on screen"},
        {"command": "help", "description": "Show help"}
    ]
    try:
        requests.post(url, json={"commands": commands}, timeout=10)
    except:
        pass

def start_commander_loop():
    """Main polling loop using Long Polling"""
    offset = 0
    print("[*] Commander Service Started (Low-RAM Polling Mode)")
    
    session = requests.Session()
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
            params = {
                "offset": offset,
                "timeout": 30  # Wait up to 30s for new message (Low CPU/RAM)
            }
            
            response = session.get(url, params=params, timeout=40)
            result = response.json()

            if result.get("ok"):
                for update in result.get("result", []):
                    offset = update["update_id"] + 1
                    
                    if "message" in update:
                        message = update["message"]
                        user_id = str(message.get("from", {}).get("id"))
                        text = message.get("text", "")
                        
                        # Security: Only accept commands from OWNER
                        if user_id == CHAT_ID and text.startswith("/"):
                            # Run usage intensive tasks in thread
                            threading.Thread(target=execute_command, args=(text,)).start()
                            
        except Exception as e:
            # Silent error handling with backoff
            time.sleep(5)
            
        time.sleep(0.5)
