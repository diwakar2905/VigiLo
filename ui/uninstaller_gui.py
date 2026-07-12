# ui/uninstaller_gui.py
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import threading
import time
import shutil
try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

# Custom imports
from ui.styles import BG, BG2, BG3, ACCENT, GREEN, WARN, DIM, FG, apply_styles
from security.privilege import is_admin
from utils.system import get_resource_path
from core.uninstall_engine import UninstallEngine

# Force Taskbar ID
try:
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('vigilo.security.uninstaller.v3')
except:
    pass

APP_NAME    = "VigiLo Uninstaller"
INSTALL_DIR = r"C:\Program Files\VigiLo"
EXECUTABLE_NAME = "VigiLo.exe"

class UninstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("620x460")
        self.resizable(False, False)
        self.configure(bg=BG)

        # Title bar icon load
        try:
            icon_path = get_resource_path("app_icon.ico")
            if not os.path.exists(icon_path):
                icon_path = os.path.join(os.getcwd(), "setup", "app_icon.ico")

            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
                if Image:
                    _img = Image.open(icon_path).resize((64, 64), Image.LANCZOS)
                    self._icon = ImageTk.PhotoImage(_img)
                    self.wm_iconphoto(True, self._icon)
        except Exception as e:
            print(f"Icon load error: {e}")

        # Styles
        style = ttk.Style()
        apply_styles(style)

        # Top bar
        top = tk.Frame(self, bg="#181818", height=36)
        top.pack(fill="x")
        top.pack_propagate(False)
        tk.Label(top, text="🐕  VigiLo Security Uninstaller",
                 font=("Segoe UI", 11, "bold"), fg=FG, bg="#181818",
                 pady=8, padx=16).pack(side="left")

        # Container
        container = ttk.Frame(self, padding="28 8")
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (ConfirmPage, UninstallPage, DonePage):
            name  = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("ConfirmPage")

    def show_frame(self, name):
        self.frames[name].tkraise()


class ConfirmPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Header
        ttk.Label(self, text="Uninstall VigiLo", style="Header.TLabel").pack(pady=(6, 2), anchor="w")
        ttk.Label(self, text="This will completely remove VigiLo Security from your system.",
                  style="SubHeader.TLabel").pack(anchor="w", pady=(0, 14))

        # What will be removed card
        info = ttk.LabelFrame(self, text=" What will be removed ", padding=12)
        info.pack(fill="x", pady=(0, 10))

        items = [
            ("🗑", "Installation folder contents", INSTALL_DIR),
            ("🗑", "SYSTEM scheduled boot service", "VigiLo_Service"),
            ("🗑", "USER scheduled logon agent", "VigiLo_Commander"),
            ("🗑", "Registry Run startup keys", "VigiLoMonitor"),
        ]
        for icon, label, detail in items:
            row = tk.Frame(info, bg=BG2)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=icon, font=("Segoe UI Emoji", 11), bg=BG2, fg=FG).pack(side="left", padx=(0, 8))
            tk.Label(row, text=label, font=("Segoe UI", 10, "bold"), bg=BG2, fg=FG).pack(side="left")
            tk.Label(row, text=f"  —  {detail}", font=("Segoe UI", 9), bg=BG2, fg=DIM).pack(side="left")

        # Warning Card
        warn_frame = tk.Frame(self, bg=BG3, pady=8, padx=12)
        warn_frame.pack(fill="x", pady=(0, 14))
        tk.Label(warn_frame,
                 text="⚠️  This action cannot be undone. Your Telegram bot credentials\n"
                      "    will remain intact on Telegram, but the monitoring service will stop.",
                 font=("Segoe UI", 9), fg=WARN, bg=BG3,
                 justify="left").pack(anchor="w")

        # Admin privilege status check
        if not is_admin():
            adm_row = tk.Frame(self, bg=BG)
            adm_row.pack(fill="x", pady=(0, 6))
            tk.Label(adm_row, text="⚠️  Administrator privileges are required to perform uninstallation.",
                     font=("Segoe UI", 9, "bold"), fg=WARN, bg=BG).pack(side="left")

        # Control Buttons
        btn_bar = tk.Frame(self, bg=BG)
        btn_bar.pack(side="bottom", fill="x", pady=(8, 0))

        tk.Button(
            btn_bar, text="Cancel",
            command=sys.exit,
            font=("Segoe UI", 10), bg="#3c3c3c", fg=FG,
            activebackground="#4a4a4a", activeforeground="white",
            relief="flat", padx=20, pady=8, cursor="hand2"
        ).pack(side="left")

        if not is_admin():
            tk.Button(
                btn_bar, text="Relaunch as Admin  →",
                command=self._relaunch_admin,
                font=("Segoe UI", 10, "bold"), bg=ACCENT, fg="white",
                activebackground="#5BA0E0", activeforeground="white",
                relief="flat", padx=24, pady=8, cursor="hand2"
            ).pack(side="right")
        else:
            tk.Button(
                btn_bar, text="Uninstall  →",
                command=self._start,
                font=("Segoe UI", 10, "bold"), bg="#C0392B", fg="white",
                activebackground="#E74C3C", activeforeground="white",
                relief="flat", padx=28, pady=8, cursor="hand2"
            ).pack(side="right")

    def _start(self):
        self.controller.show_frame("UninstallPage")
        self.controller.frames["UninstallPage"].begin()

    def _relaunch_admin(self):
        import ctypes
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()


class UninstallPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Removing VigiLo…", style="Header.TLabel").pack(pady=(6, 4), anchor="w")
        self.status_var = tk.StringVar(value="Initializing uninstallation...")
        ttk.Label(self, textvariable=self.status_var, style="SubHeader.TLabel").pack(anchor="w", pady=(0, 8))

        self.progress = ttk.Progressbar(self, orient="horizontal", mode="determinate", length=500)
        self.progress.pack(fill="x", pady=(0, 6), ipady=2)

        log_frame = ttk.LabelFrame(self, text=" Cleanup Log ", padding=5)
        log_frame.pack(fill="both", expand=True, pady=4)

        sb = ttk.Scrollbar(log_frame)
        sb.pack(side="right", fill="y")

        self.log_text = tk.Text(
            log_frame, font=("Consolas", 9),
            bg="#1e1e1e", fg=GREEN,
            relief="flat", highlightthickness=0,
            state="disabled", wrap="word",
            yscrollcommand=sb.set,
            padx=8, pady=6
        )
        self.log_text.pack(fill="both", expand=True)
        sb.config(command=self.log_text.yview)

    def log(self, msg, color=None):
        self.log_text.config(state="normal")
        tag = f"t{self.log_text.index('end')}"
        self.log_text.insert("end", f"  {msg}\n", tag)
        if color:
            self.log_text.tag_config(tag, foreground=color)
        self.log_text.see("end")
        self.log_text.config(state="disabled")
        self.status_var.set(msg)
        self.update_idletasks()

    def set_progress(self, val):
        self.progress["value"] = val
        self.update_idletasks()

    def begin(self):
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        engine = UninstallEngine()
        
        def log_cb(msg):
            self.log(msg)
            
        def progress_cb(val):
            self.set_progress(val)

        success = engine.uninstall(progress_callback=progress_cb, log_callback=log_cb)

        if success:
            time.sleep(1.2)
            self.after(0, lambda: self.controller.show_frame("DonePage"))
        else:
            self.log("ERROR: Uninstallation sequence encountered warnings.", WARN)
            messagebox.showwarning("Uninstallation Complete with warnings", 
                                   "Some files could not be removed automatically.\n"
                                   f"You may need to manually delete the directory: {INSTALL_DIR}")
            self.after(0, lambda: self.controller.show_frame("DonePage"))


class DonePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Uninstall Complete", style="Header.TLabel").pack(pady=(8, 4), anchor="w")
        ttk.Label(self, text="VigiLo Security has been fully removed from this system.",
                  style="SubHeader.TLabel").pack(anchor="w", pady=(0, 16))

        card = tk.Frame(self, bg=BG2, pady=12, padx=16)
        card.pack(fill="x", pady=(0, 12))

        removed = [
            ("✓", "Scheduled tasks removed successfully", "AntiTheft_Service & AntiTheft_Commander"),
            ("✓", "Registry startup hooks cleaned", "HKLM Run key removed"),
            ("✓", "Installation binaries deleted", INSTALL_DIR),
            ("✓", "ProgramData captures buffer cleaned", "Offline image caches removed"),
        ]
        for icon, title, detail in removed:
            row = tk.Frame(card, bg=BG2)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=icon, font=("Segoe UI", 11, "bold"), fg=GREEN, bg=BG2).pack(side="left", padx=(0, 10))
            tk.Label(row, text=title, font=("Segoe UI", 10, "bold"), fg=FG, bg=BG2).pack(side="left")
            tk.Label(row, text=f"  —  {detail}", font=("Segoe UI", 9), fg=DIM, bg=BG2).pack(side="left")

        note = tk.Frame(self, bg=BG3, pady=8, padx=12)
        note.pack(fill="x", pady=(0, 16))
        tk.Label(note,
                 text="ℹ️  Your Telegram bot credentials and bot tokens remain intact.\n"
                      "   You can edit/delete your bot via @BotFather on Telegram at any time.",
                 font=("Segoe UI", 9), fg=DIM, bg=BG3, justify="left").pack(anchor="w")

        btn_bar = tk.Frame(self, bg=BG)
        btn_bar.pack(side="bottom", fill="x", pady=(8, 0))
        tk.Label(btn_bar, text="© 2026 VigiLo Security  —  All Rights Reserved",
                 font=("Segoe UI", 8), fg=DIM, bg=BG).pack(side="left")
        tk.Button(
            btn_bar, text="Close",
            command=sys.exit,
            font=("Segoe UI", 10, "bold"), bg="#3c3c3c", fg=FG,
            activebackground="#4a4a4a", activeforeground="white",
            relief="flat", padx=30, pady=8, cursor="hand2"
        ).pack(side="right")


if __name__ == "__main__":
    if not is_admin():
        # Elevate to administrator
        from security.privilege import elevate
        elevate()
        
    # Standard temp-directory self-copy workaround to prevent locking of uninstaller binary itself
    if is_admin():
        current_dir = os.getcwd().lower()
        if INSTALL_DIR.lower() in current_dir or INSTALL_DIR.lower() in sys.executable.lower():
            try:
                temp_dir = os.path.join(os.environ["TEMP"], "wd_uninstall")
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                
                temp_exe = os.path.join(temp_dir, "uninstall.exe")
                shutil.copy2(sys.executable, temp_exe)
                
                import subprocess
                subprocess.Popen([temp_exe])
                sys.exit()
            except Exception as e:
                # If self-copy fails, fall back to in-place uninstallation
                pass

    app = UninstallerApp()
    app.mainloop()
