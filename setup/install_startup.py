import os
import subprocess
import shutil
import sys
import ctypes
import json

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate():
    """Re-run the script with admin privileges"""
    if not is_admin():
        print("[!] Not running as Administrator. Requesting elevation...")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit(0)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC_FILE = os.path.join(BASE_DIR, "monitor.spec")
BUILD_DIR = os.path.join(BASE_DIR, "build")
DIST_DIR = os.path.join(BASE_DIR, "dist")
SOURCE_CONFIG = os.path.join(BASE_DIR, "config.json")
EXE_PATH = os.path.join(DIST_DIR, "WatchDog.exe")
DEST_CONFIG = os.path.join(DIST_DIR, "config.json")

def build_exe():
    print("\n--- Building Project ---")
    if not os.path.exists(SPEC_FILE):
        print("[X] Error: monitor.spec not found!")
        return False
    
    try:
        # Run pyinstaller with --onefile for single executable
        result = subprocess.run(
            ["pyinstaller", "--clean", SPEC_FILE], 
            cwd=BASE_DIR, 
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("[✓] Build successful")
            print(f"    Executable: {EXE_PATH}")
            return True
        else:
            print("[X] Build failed")
            print(result.stderr)
            return False
            
    except FileNotFoundError:
        print("[X] PyInstaller not found. Installing...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("[✓] PyInstaller installed. Please run this script again.")
            return False
        except:
            print("[X] Failed to install PyInstaller. Please run: pip install pyinstaller")
            return False

def setup_files():
    print("\n--- Setting up Files ---")
    
    if not os.path.exists(EXE_PATH):
        print(f"[X] Executable not found at {EXE_PATH}")
        return False
    
    print(f"[✓] Executable found: {EXE_PATH}")
    
    if os.path.exists(SOURCE_CONFIG):
        print(f"    Copying config.json to {DIST_DIR}...")
        shutil.copy(SOURCE_CONFIG, DEST_CONFIG)
        print("[✓] Config copied")
    else:
        print("[!] Warning: config.json not found. Creating default...")
        default_config = {
            "telegram": {
                "bot_token": "YOUR_BOT_TOKEN",
                "chat_id": "YOUR_CHAT_ID"
            },
            "security": {
                "failed_attempt_threshold": 2,
                "event_id": 4625,
                "check_interval_seconds": 1
            },
            "camera": {
                "device_index": 0
            }
        }
        with open(DEST_CONFIG, 'w') as f:
            json.dump(default_config, f, indent=4)
        print("[!] Please edit config.json with your Telegram credentials!")
    
    return True

def delete_existing_task():
    """Delete existing task if it exists"""
    try:
        subprocess.run(
            ["schtasks", "/Delete", "/TN", "WatchDogMonitor", "/F"],
            capture_output=True,
            check=False
        )
    except:
        pass

def create_task():
    print("\n--- Creating Startup Task (Method 1: Scheduled Task) ---")
    task_name = "WatchDogMonitor"
    
    if not is_admin():
        print("[X] Administrator privileges required!")
        return False

    # Delete existing task first
    delete_existing_task()
    
    # Create task with XML for better control
    xml_content = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Anti-Theft Monitor - Detects failed login attempts</Description>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
      <Delay>PT0S</Delay>
    </BootTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
    <RestartOnFailure>
      <Interval>PT1M</Interval>
      <Count>3</Count>
    </RestartOnFailure>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{EXE_PATH}</Command>
      <WorkingDirectory>{DIST_DIR}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''
    
    # Save XML to temp file
    xml_path = os.path.join(DIST_DIR, "task.xml")
    with open(xml_path, 'w', encoding='utf-16') as f:
        f.write(xml_content)
    
    try:
        result = subprocess.run(
            ["schtasks", "/Create", "/TN", task_name, "/XML", xml_path, "/F"],
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"[✓] Scheduled Task '{task_name}' created successfully!")
        print("    Trigger: On system boot (10 second delay)")
        
        # Clean up XML file
        try:
            os.remove(xml_path)
        except:
            pass
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"[X] Failed to create task!")
        print(f"    Error: {e.stderr}")
        return False

def add_registry_startup():
    """Add registry entry for startup (backup method)"""
    print("\n--- Creating Registry Startup (Method 2: Registry Run Key) ---")
    
    if not is_admin():
        print("[X] Administrator privileges required!")
        return False
    
    try:
        import winreg
        
        # Open the Run key in HKEY_LOCAL_MACHINE (runs for all users)
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE)
        
        # Set the value
        winreg.SetValueEx(key, "WatchDogMonitor", 0, winreg.REG_SZ, f'"{EXE_PATH}"')
        winreg.CloseKey(key)
        
        print("[✓] Registry startup entry created!")
        print(f"    Location: HKLM\\{key_path}")
        print(f"    Value: AntiTheftMonitor = \"{EXE_PATH}\"")
        return True
        
    except Exception as e:
        print(f"[X] Failed to create registry entry: {e}")
        return False

def verify_task():
    print("\n--- Verifying Installation ---")
    try:
        result = subprocess.run(
            ["schtasks", "/Query", "/TN", "WatchDogMonitor", "/FO", "LIST"],
            capture_output=True,
            text=True,
            check=True
        )
        print("[✓] Task verified successfully!")
        print("\nTask Details:")
        for line in result.stdout.split('\n'):
            if any(key in line for key in ['TaskName', 'Status', 'Next Run Time', 'Last Run Time']):
                print(f"    {line.strip()}")
        return True
    except subprocess.CalledProcessError:
        print("[X] Task verification failed!")
        return False

def test_run():
    print("\n--- Testing Execution ---")
    print("Starting the monitor manually for 5 seconds to verify it works...")
    try:
        proc = subprocess.Popen(
            [EXE_PATH],
            cwd=DIST_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        import time
        time.sleep(5)
        proc.terminate()
        
        print("[✓] Monitor started successfully!")
        print("    If you see no errors above, the installation is complete.")
        return True
    except Exception as e:
        print(f"[X] Failed to start monitor: {e}")
        return False

def main():
    print("=" * 50)
    print("  Anti-Theft Startup Installer")
    print("=" * 50)
    
    # Check admin first
    if not is_admin():
        print("\n[!] This installer requires Administrator privileges.")
        print("    Attempting to elevate...")
        elevate()
        return
    
    print("\n[✓] Running as Administrator")
    
    # 1. Build
    if not build_exe():
        print("\n[X] Installation failed at build step.")
        input("Press Enter to exit...")
        return
        
    # 2. Setup Files
    if not setup_files():
        print("\n[X] Installation failed at setup step.")
        input("Press Enter to exit...")
        return
        
    # 3. Create Task
    task_success = create_task()
    
    # 4. Add Registry Startup (backup method)
    registry_success = add_registry_startup()
    
    if not task_success and not registry_success:
        print("\n[X] Installation failed! Neither startup method succeeded.")
        input("Press Enter to exit...")
        return
    elif not task_success:
        print("\n[!] Warning: Scheduled Task failed, but Registry startup succeeded.")
    elif not registry_success:
        print("\n[!] Warning: Registry startup failed, but Scheduled Task succeeded.")
    
    # 5. Verify
    if task_success:
        verify_task()
    
    # 6. Test
    # test_run()
    
    print("\n" + "=" * 50)
    print("  Installation Complete!")
    print("=" * 50)
    
    if task_success and registry_success:
        print("\n✓ Dual startup protection enabled!")
        print("  - Scheduled Task (runs on boot)")
        print("  - Registry Run Key (runs on user login)")
    print("\n")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
