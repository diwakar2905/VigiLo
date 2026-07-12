# setup/install_startup.py
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_build(spec_name):
    spec_path = os.path.join(BASE_DIR, spec_name)
    print(f"\n--- Building {spec_name} ---")
    if not os.path.exists(spec_path):
        print(f"[X] Error: {spec_name} not found at {spec_path}!")
        return False
    
    try:
        # Run PyInstaller cleanly
        result = subprocess.run(
            ["pyinstaller", "--clean", spec_path], 
            cwd=BASE_DIR, 
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"[+] Build of {spec_name} successful")
            return True
        else:
            print(f"[X] Build of {spec_name} failed")
            print(result.stderr)
            return False
    except FileNotFoundError:
        print("[X] PyInstaller is not installed in the current environment.")
        print("    Please install it via: pip install pyinstaller")
        return False
    except Exception as e:
        print(f"[X] Exception during build of {spec_name}: {e}")
        return False

def main():
    print("=" * 60)
    print("  WatchDog Complete Executable Builder")
    print("=" * 60)
    
    # 1. Build WatchDog service payload first
    if not run_build("monitor.spec"):
        print("[X] Build aborted: Main WatchDog service payload failed.")
        return
        
    # 2. Build Uninstaller executable second
    if not run_build("WatchDog_Uninstall.spec"):
        print("[X] Build aborted: Uninstaller executable failed.")
        return
        
    # 3. Build Installer Wizard last (bundles both WatchDog.exe and uninstall.exe)
    if not run_build("WatchDog_Setup.spec"):
        print("[X] Build aborted: Installer wizard failed.")
        return
        
    print("\n" + "=" * 60)
    print("  All builds completed successfully!")
    print("  Artifacts generated under root 'dist/' folder:")
    print("  - WatchDog.exe (Main Payload)")
    print("  - uninstall.exe (Uninstaller)")
    print("  - WatchDog_Setup.exe (Installer Wizard)")
    print("=" * 60)
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
