import os
import time
import json
import win32evtlog
import threading
import sys
try:
    import win32gui
    import win32con
except ImportError:
    win32gui = None
    win32con = None
import requests

# Ensure root directory is in path for imports
if not getattr(sys, 'frozen', False):
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import new modules
try:
    # Try local import (if running from inside service dir)
    from camera import capture_intruder_file
except ImportError:
    # Try package import (if running from root or exe)
    from service.camera import capture_intruder_file

# --------------------------------------------------
# PATHS (SERVICE SAFE)
# --------------------------------------------------
if getattr(sys, 'frozen', False):
    # Running as compiled EXE
    BASE_DIR = os.path.dirname(sys.executable)
    CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
else:
    # Running as Python script
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ROOT_DIR = os.path.dirname(BASE_DIR)
    CONFIG_PATH = os.path.join(ROOT_DIR, "config.json")

IMAGE_DIR = os.getenv("PROGRAMDATA") or "C:\\ProgramData"
CAPTURES_DIR = os.path.join(IMAGE_DIR, "AntiTheftCaptures")

if not os.path.exists(CAPTURES_DIR):
    try:
        os.makedirs(CAPTURES_DIR)
    except Exception as e:
        print(f"[ERROR] Could not create capture dir: {e}")

CAPTURE_COOLDOWN = 0.0  # Zero delay between possible captures
last_capture_time = 0

# --------------------------------------------------
# LOAD CONFIG (SAFE)
# --------------------------------------------------
def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

CONFIG = load_config()

# Telegram
BOT_TOKEN = CONFIG.get("telegram", {}).get("bot_token")
CHAT_ID = CONFIG.get("telegram", {}).get("chat_id")

# Security
FAILED_THRESHOLD = CONFIG.get("security", {}).get("failed_attempt_threshold", 2)
TARGET_EVENT_ID = CONFIG.get("security", {}).get("event_id", 4625)
CHECK_INTERVAL = CONFIG.get("security", {}).get("check_interval_seconds", 0.1)

# Camera
CAM_INDEX = CONFIG.get("camera", {}).get("device_index", 0)

# --------------------------------------------------
# UPLOAD WORKER (QUEUE HANDLER)
# --------------------------------------------------
def check_internet():
    try:
        import requests
        requests.get("https://www.google.com", timeout=1)
        return True
    except:
        return False

def send_telegram_photo(image_path):
    if not BOT_TOKEN or not CHAT_ID:
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    data = {"chat_id": CHAT_ID, "caption": "🚨 Wrong PIN attempt detected! (Buffered Image)"}

    try:
        import requests
        with open(image_path, "rb") as img:
            files = {"photo": img}
            resp = requests.post(url, data=data, files=files, timeout=20)
            return resp.status_code == 200
    except Exception as e:
        print(f"[DEBUG] Upload failed: {e}")
        return False

def upload_worker(stop_event):
    print("[*] Upload worker started (queue monitor)")
    while not stop_event.is_set():
        if not os.path.exists(CAPTURES_DIR):
            time.sleep(5)
            continue
            
        files = [f for f in os.listdir(CAPTURES_DIR) if f.endswith(".jpg") or f.endswith(".png")]
        if not files:
            time.sleep(5)
            continue

        print(f"[DEBUG] Found {len(files)} pending uploads. Checking internet...")
        
        if check_internet():
            print("[DEBUG] Internet connected. Processing queue...")
            for filename in files:
                # Skip user command files (Commander handles them)
                if filename.startswith("cmd_"):
                    continue

                filepath = os.path.join(CAPTURES_DIR, filename)
                print(f"[Attempting] {filename}")
                
                if send_telegram_photo(filepath):
                    print(f"[SUCCESS] Uploaded {filename}")
                    try:
                        os.remove(filepath)
                    except:
                        pass
                else:
                    print(f"[FAIL] Could not upload {filename}, retrying later.")
        else:
            print("[DEBUG] No internet. Waiting...")
        
        time.sleep(10)

# --------------------------------------------------
# CAMERA WRAPPER
# --------------------------------------------------
def capture_intruder():
    """Wrapper for shared camera logic"""
    print("[DEBUG] capture_intruder() called")
    saved_path = capture_intruder_file(CAPTURES_DIR, CAM_INDEX, prefix="alert_")
    if saved_path:
        print(f"[INFO] ✓ Captured: {saved_path}")
    else:
        print("[ERROR] Capture failed")

# --------------------------------------------------
# EVENT LOG MONITOR
# --------------------------------------------------
def monitor_failed_logins(stop_event):
    global last_capture_time
    server = "localhost"
    log_type = "Security"

    try:
        handle = win32evtlog.OpenEventLog(server, log_type)
        # 1. Position at the end
        back_flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        events = win32evtlog.ReadEventLog(handle, back_flags, 0)
        last_record = events[0].RecordNumber if events else 0

        print(f"[*] Anchored at record {last_record}")
        print("[*] Monitoring Security log (INSTANT MODE - Fast Detection)")

        start_time = time.time()
        failed_count = 0

        while not stop_event.is_set():
            try:
                # Use SEEK_READ to strictly read from the last known position forward
                flags = win32evtlog.EVENTLOG_FORWARDS_READ | win32evtlog.EVENTLOG_SEEK_READ
                events = win32evtlog.ReadEventLog(handle, flags, last_record)
                
                if not events:
                    time.sleep(0.5)
                    continue

                for event in events:
                    # Skip events we've already processed
                    if event.RecordNumber <= last_record:
                        continue
                        
                    last_record = event.RecordNumber

                    # Only process events that happened after we started monitoring
                    # (Optional safety, but RecordNumber handling is usually sufficient)
                    
                    if event.EventID == TARGET_EVENT_ID:
                        failed_count += 1
                        print(f"[ALERT] Failed login #{failed_count} (Event {event.RecordNumber})")

                        if failed_count >= FAILED_THRESHOLD:
                            now = time.time()
                            if now - last_capture_time >= CAPTURE_COOLDOWN:
                                print(f"[ACTION] Wrong Password Threshold Reached! Capturing...")
                                threading.Thread(target=capture_intruder, daemon=True).start()
                                last_capture_time = now
                                failed_count = 0  # Reset after capture
                            else:
                                print("[INFO] Capture on cooldown")
                                failed_count = 0 # Reset anyway
            
                time.sleep(0.5)

            except Exception as e:
                # If handle becomes invalid or other issues
                print(f"[ERROR] Event Loop: {e}")
                time.sleep(2)
                # Try to recover handle
                try: 
                    handle = win32evtlog.OpenEventLog(server, log_type) 
                except: pass

    except Exception as e:
        print(f"[CRITICAL] Event Log Error: {e}")

# --------------------------------------------------
# ENTRY POINT
# --------------------------------------------------
# --------------------------------------------------
# SHUTDOWN MONITOR
# --------------------------------------------------
def send_shutdown_alert():
    if not BOT_TOKEN or not CHAT_ID: return
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT_ID, "text": "⚠️ System Shutdown Detected! WatchDog is stopping."}, timeout=2)
    except:
        pass

def run_shutdown_monitor():
    if not win32gui: return
    
    def wnd_proc(hwnd, msg, wparam, lparam):
        if msg == win32con.WM_QUERYENDSESSION:
            print("[ALERT] Shutdown detected!")
            send_shutdown_alert()
            return 1
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    wc = win32gui.WNDCLASS()
    wc.lpfnWndProc = wnd_proc
    wc.lpszClassName = "WatchDogShutdown"
    wc.hInstance = win32gui.GetModuleHandle(None)
    
    try:
        win32gui.RegisterClass(wc)
    except: pass
    
    try:
        win32gui.CreateWindowEx(0, wc.lpszClassName, "WD_Shutdown_Listener", 0, 0, 0, 0, 0, 0, 0, 0, None)
        win32gui.PumpMessages()
    except: pass

# --------------------------------------------------
# ENTRY POINT
# --------------------------------------------------
def start_service(stop_event):
    print("[*] Service Mode: Starting Security Monitor & Upload Worker")
    
    # 1. Start Event Monitor
    monitor_thread = threading.Thread(
        target=monitor_failed_logins,
        args=(stop_event,),
        daemon=True
    )
    monitor_thread.start()

    # 2. Start Upload Worker
    upload_thread = threading.Thread(
        target=upload_worker,
        args=(stop_event,),
        daemon=True
    )
    upload_thread.start()

    # 3. Start Shutdown Monitor (Low Priority)
    shutdown_thread = threading.Thread(
        target=run_shutdown_monitor,
        daemon=True
    )
    shutdown_thread.start()

def start_commander():
    print("[*] Commander Mode: Starting Telegram Agent")
    try:
        import commander
    except ImportError:
        import service.commander as commander

    commander.init_commander(CONFIG, CAPTURES_DIR)
    # Run in main thread since it's the only thing running in this mode
    commander.start_commander_loop()

if __name__ == "__main__":
    mode = "service"
    if len(sys.argv) > 1:
        if "--commander" in sys.argv:
            mode = "commander"
    
    if mode == "commander":
        start_commander()
    else:
        # Service Mode
        print("[*] Running WatchDog Secure Monitor (SYSTEM SERVICE)...")
        dummy_event = threading.Event()
        start_service(dummy_event)

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            dummy_event.set()
