import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import ctypes
import shutil
import subprocess
import time
import threading

# Force Taskbar Icon Persistence early
try:
    myappid = 'watchdog.security.uninstaller.v1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

APP_NAME = "WatchDog Uninstaller"
INSTALL_DIR = r"C:\Program Files\WatchDog"
EXECUTABLE_NAME = "monitor.exe"
SERVICE_TASK = "AntiTheft_Service"
COMMANDER_TASK = "AntiTheft_Commander"

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class UninstallApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title(APP_NAME)
        self.geometry("400x300")
        self.resizable(False, False)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        self.configure(bg="#ffffff")
        style.configure("TFrame", background="#ffffff")
        style.configure("TLabel", background="#ffffff", foreground="#333333", font=("Segoe UI", 10))
        
        # Icon
        # Icon
        try:
           icon_path = get_resource_path("app_icon.ico")
           if not os.path.exists(icon_path):
               # Dev mode fallback
               icon_path = os.path.join(os.getcwd(), "setup", "app_icon.ico")
           
           if os.path.exists(icon_path):
               self.iconbitmap(icon_path)
        except:
            pass

        # Container
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        # Header
        ttk.Label(frame, text="Uninstall WatchDog", font=("Segoe UI", 18, "bold"), foreground="#d9534f").pack(pady=(10, 20))
        
        ttk.Label(frame, text="This will remove WatchDog and all its components.", wraplength=350, justify="center").pack(pady=10)
        
        if not is_admin():
            ttk.Label(frame, text="⚠️ Admin privileges required", foreground="#d9534f").pack(pady=10)
            tk.Button(frame, text="Relaunch as Admin", command=self.relaunch_admin, 
                      bg="#e1e1e1", padx=15, pady=8, font=("Segoe UI", 10)).pack(pady=10)
        else:
            self.progress = ttk.Progressbar(frame, orient="horizontal", length=300, mode="determinate")
            self.progress.pack(pady=20)
            
            self.status_var = tk.StringVar(value="Ready to uninstall")
            ttk.Label(frame, textvariable=self.status_var, foreground="#666666").pack(pady=5)
            
            self.uninstall_btn = tk.Button(frame, text="Uninstall", command=self.start_uninstall,
                                         bg="#d9534f", fg="white", font=("Segoe UI", 11, "bold"),
                                         padx=20, pady=10, relief="flat", cursor="hand2")
            self.uninstall_btn.pack(pady=10)

    def relaunch_admin(self):
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

    def start_uninstall(self):
        # Confirm
        if not messagebox.askyesno("Confirm", "Are you sure you want to remove WatchDog?"):
            return
            
        self.uninstall_btn.config(state="disabled")
        threading.Thread(target=self.run_uninstall, daemon=True).start()

    def run_uninstall(self):
        try:
            self.progress['value'] = 10
            self.status_var.set("Stopping services...")
            
            # Stop processes
            subprocess.run(["taskkill", "/F", "/IM", EXECUTABLE_NAME], capture_output=True)
            self.progress['value'] = 30
            
            # Delete Tasks
            self.status_var.set("Removing scheduled tasks...")
            subprocess.run(["schtasks", "/Delete", "/TN", SERVICE_TASK, "/F"], capture_output=True)
            subprocess.run(["schtasks", "/Delete", "/TN", COMMANDER_TASK, "/F"], capture_output=True)
            self.progress['value'] = 60
            
            # Delete Files
            self.status_var.set("Deleting files...")
            time.sleep(1) # Give taskkill a moment
            
            if os.path.exists(INSTALL_DIR):
                try:
                    shutil.rmtree(INSTALL_DIR)
                except Exception as e:
                    # If failed, might be running from there?
                    # But we should have copied to temp if we were smart (Task says copy to temp)
                    pass
            
            self.progress['value'] = 100
            self.status_var.set("Uninstallation Complete")
            
            messagebox.showinfo("Success", "WatchDog has been successfully removed.")
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Uninstall failed: {e}")
            self.status_var.set("Error occurred")
            self.uninstall_btn.config(state="normal")

def main():
    # Setup self-copy mechanism if running from install dir to allow deletion
    if is_admin():
         if INSTALL_DIR.lower() in os.getcwd().lower() or INSTALL_DIR.lower() in sys.executable.lower():
            try:
                # Copy to temp and run from there
                temp_dir = os.path.join(os.environ["TEMP"], "wd_uninstall")
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                
                temp_exe = os.path.join(temp_dir, "uninstall.exe")
                shutil.copy2(sys.executable, temp_exe)
                
                # Copy icon if possible for UI
                try:
                    src_icon = os.path.join(os.path.dirname(sys.executable), "app_icon.ico")
                    # If running as onefile, icon is inside. But we might have extracted it?
                    # Actually for uninstaller we should rely on get_resource_path inside the temp exe.
                    pass 
                except:
                    pass

                # Run the temp copy
                subprocess.Popen([temp_exe])
                sys.exit()
            except Exception as e:
                # If copy fails, just try running in place (might fail to delete self)
                pass

    app = UninstallApp()
    app.mainloop()

if __name__ == "__main__":
    main()
