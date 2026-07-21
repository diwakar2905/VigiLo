import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import ctypes
import subprocess
import threading
import time
import shutil
try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

# ---------------------------------------------------------------------------
# TASKBAR ID
# ---------------------------------------------------------------------------
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
        'watchdog.security.uninstaller.v3'
    )
except Exception:
    pass

# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------
APP_NAME    = "WatchDog Uninstaller"
INSTALL_DIR = r"C:\Program Files\WatchDog"
EXECUTABLE_NAME = "WatchDog.exe"
TASK_NAMES  = ["AntiTheft_Service", "AntiTheft_Commander"]

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


# ---------------------------------------------------------------------------
# PROFESSIONAL DARK-SLATE PALETTE  (matches install_wizard.py)
# ---------------------------------------------------------------------------
BG     = "#1e1e1e"
BG2    = "#252526"
BG3    = "#2d2d30"
ACCENT = "#4A90D9"
GREEN  = "#4EC994"
WARN   = "#ce9178"
DIM    = "#858585"
FG     = "#d4d4d4"

# ===========================================================================
# MAIN APP
# ===========================================================================
class UninstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("620x460")
        self.resizable(False, False)
        self.configure(bg=BG)

        # ── Icon (title bar + taskbar) ────────────────────────────────────────
        try:
            _here = os.path.dirname(os.path.abspath(__file__))
            _icon_path = None
            for _candidate in [
                os.path.join(_here, "app_icon.ico"),
                os.path.join(_here, "..", "app_icon.ico"),
            ]:
                if os.path.exists(_candidate):
                    _icon_path = _candidate
                    break

            if _icon_path:
                # Title-bar icon
                self.iconbitmap(_icon_path)
                # Taskbar icon — requires a PhotoImage kept alive on self
                if Image:
                    _img = Image.open(_icon_path).resize((64, 64), Image.LANCZOS)
                    self._icon = ImageTk.PhotoImage(_img)
                    self.wm_iconphoto(True, self._icon)
        except Exception as _e:
            print(f"Icon load error: {_e}")

        # ── Style ────────────────────────────────────────────────────────────
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame",              background=BG)
        style.configure("TLabel",              background=BG, foreground=FG,     font=("Segoe UI", 10))
        style.configure("Header.TLabel",       background=BG, foreground=ACCENT, font=("Segoe UI", 20, "bold"))
        style.configure("SubHeader.TLabel",    background=BG, foreground=DIM,    font=("Segoe UI", 10))
        style.configure("Warning.TLabel",      background=BG, foreground=WARN,   font=("Segoe UI", 10))
        style.configure("TLabelframe",         background=BG2, relief="flat")
        style.configure("TLabelframe.Label",   background=BG2, foreground=ACCENT, font=("Segoe UI", 10, "bold"))
        style.configure("Horizontal.TProgressbar",
                        troughcolor="#3c3c3c", background=ACCENT, thickness=8)

        # ── Top bar ──────────────────────────────────────────────────────────
        top = tk.Frame(self, bg="#181818", height=36)
        top.pack(fill="x")
        top.pack_propagate(False)
        tk.Label(top, text="🐕  WatchDog Security Uninstaller",
                 font=("Segoe UI", 11, "bold"), fg=FG, bg="#181818",
                 pady=8, padx=16).pack(side="left")

        # ── Pages ────────────────────────────────────────────────────────────
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


# ===========================================================================
# PAGE 1 — CONFIRM
# ===========================================================================
class ConfirmPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Header
        ttk.Label(self, text="Uninstall WatchDog", style="Header.TLabel").pack(pady=(6, 2), anchor="w")
        ttk.Label(self, text="This will completely remove WatchDog Security from your system.",
                  style="SubHeader.TLabel").pack(anchor="w", pady=(0, 14))

        # What will be removed card
        info = ttk.LabelFrame(self, text=" What will be removed ", padding=12)
        info.pack(fill="x", pady=(0, 10))

        items = [
            ("🗑", "Installation directory",  INSTALL_DIR),
            ("🗑", "Scheduled task",           "AntiTheft_Service"),
            ("🗑", "Scheduled task",           "AntiTheft_Commander"),
            ("🗑", "Running service process",  EXECUTABLE_NAME),
        ]
        for icon, label, detail in items:
            row = tk.Frame(info, bg=BG2)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=icon, font=("Segoe UI Emoji", 11),
                     bg=BG2, fg=FG).pack(side="left", padx=(0, 8))
            tk.Label(row, text=label, font=("Segoe UI", 10, "bold"),
                     bg=BG2, fg=FG).pack(side="left")
            tk.Label(row, text=f"  —  {detail}", font=("Segoe UI", 9),
                     bg=BG2, fg=DIM).pack(side="left")

        # Warning
        warn_frame = tk.Frame(self, bg=BG3, pady=8, padx=12)
        warn_frame.pack(fill="x", pady=(0, 14))
        tk.Label(warn_frame,
                 text="⚠  This action cannot be undone. Your Telegram bot and chat ID will\n"
                      "    remain intact — only the WatchDog software is removed.",
                 font=("Segoe UI", 9), fg=WARN, bg=BG3,
                 justify="left").pack(anchor="w")

        # Admin check
        if not is_admin():
            adm_row = tk.Frame(self, bg=BG)
            adm_row.pack(fill="x", pady=(0, 6))
            tk.Label(adm_row, text="⚠  Administrator privileges are required to uninstall.",
                     font=("Segoe UI", 9, "bold"), fg=WARN, bg=BG).pack(side="left")

        # Buttons (packed bottom-first to avoid being hidden)
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
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()


# ===========================================================================
# PAGE 2 — UNINSTALL PROGRESS
# ===========================================================================
class UninstallPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Header
        ttk.Label(self, text="Removing WatchDog…", style="Header.TLabel").pack(pady=(6, 4), anchor="w")
        self.status_var = tk.StringVar(value="Starting…")
        ttk.Label(self, textvariable=self.status_var, style="SubHeader.TLabel").pack(anchor="w", pady=(0, 8))

        # Progress bar
        self.progress = ttk.Progressbar(self, orient="horizontal",
                                        mode="determinate", length=500)
        self.progress.pack(fill="x", pady=(0, 6), ipady=2)

        # Log
        log_frame = ttk.LabelFrame(self, text=" Activity Log ", padding=5)
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

    # ── Helpers ──────────────────────────────────────────────────────────────
    def log(self, msg, colour=None):
        self.log_text.config(state="normal")
        tag = f"t{self.log_text.index('end')}"
        self.log_text.insert("end", f"  {msg}\n", tag)
        if colour:
            self.log_text.tag_config(tag, foreground=colour)
        self.log_text.see("end")
        self.log_text.config(state="disabled")
        self.status_var.set(msg)
        self.update_idletasks()

    def set_progress(self, v):
        self.progress["value"] = v
        self.update_idletasks()

    def begin(self):
        threading.Thread(target=self._run, daemon=True).start()

    # ── Main uninstall logic ──────────────────────────────────────────────────
    def _run(self):
        try:
            self.set_progress(0)

            # 1. Stop running process
            self.log("Stopping WatchDog service…")
            r = subprocess.run(
                ["taskkill", "/F", "/IM", EXECUTABLE_NAME],
                capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
            )
            if r.returncode == 0:
                self.log(f"  ✓ Process terminated.", GREEN)
            else:
                self.log(f"  — Service was not running (OK)", DIM)
            time.sleep(0.4)
            self.set_progress(20)

            # 2. Delete scheduled tasks
            for task in TASK_NAMES:
                self.log(f"Removing scheduled task: {task}…")
                r = subprocess.run(
                    ["schtasks", "/Delete", "/TN", task, "/F"],
                    capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW
                )
                if r.returncode == 0:
                    self.log(f"  ✓ {task} removed.", GREEN)
                else:
                    self.log(f"  — {task} not found (already removed)", DIM)
                time.sleep(0.3)

            self.set_progress(55)

            # 3. Remove install directory
            self.log(f"Deleting installation folder…")
            self.log(f"  {INSTALL_DIR}")
            if os.path.exists(INSTALL_DIR):
                # Retry loop: the killed process may have file locks briefly
                for attempt in range(5):
                    try:
                        shutil.rmtree(INSTALL_DIR)
                        self.log(f"  ✓ Folder deleted.", GREEN)
                        break
                    except PermissionError as e:
                        if attempt < 4:
                            self.log(f"  ⟳ File locked, retrying… ({attempt + 1}/5)", WARN)
                            time.sleep(1.0)
                        else:
                            raise
            else:
                self.log("  — Folder not found (already removed)", DIM)

            time.sleep(0.4)
            self.set_progress(85)

            # 4. Remove ProgramData captures folder (optional)
            captures = os.path.join(
                os.getenv("PROGRAMDATA", r"C:\ProgramData"), "AntiTheftCaptures"
            )
            self.log("Removing captured images folder…")
            if os.path.exists(captures):
                shutil.rmtree(captures, ignore_errors=True)
                self.log("  ✓ Captures folder deleted.", GREEN)
            else:
                self.log("  — Captures folder not found (OK)", DIM)

            time.sleep(0.5)
            self.set_progress(100)
            self.log("Uninstallation complete.", GREEN)
            time.sleep(1.2)
            self.after(0, lambda: self.controller.show_frame("DonePage"))

        except Exception as e:
            self.log(f"ERROR: {e}", WARN)
            self.after(0, lambda: messagebox.showerror(
                "Uninstall Failed",
                f"An error occurred during uninstallation:\n\n{e}\n\n"
                "You may need to manually delete the folder:\n"
                f"{INSTALL_DIR}"
            ))


# ===========================================================================
# PAGE 3 — DONE
# ===========================================================================
class DonePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Header
        ttk.Label(self, text="Uninstall Complete", style="Header.TLabel").pack(pady=(8, 4), anchor="w")
        ttk.Label(self, text="WatchDog Security has been fully removed from this system.",
                  style="SubHeader.TLabel").pack(anchor="w", pady=(0, 16))

        # Status card
        card = tk.Frame(self, bg=BG2, pady=12, padx=16)
        card.pack(fill="x", pady=(0, 12))

        removed = [
            ("✓", "Scheduled tasks removed",         "AntiTheft_Service & AntiTheft_Commander"),
            ("✓", "Installation folder deleted",     INSTALL_DIR),
            ("✓", "Service process terminated",      EXECUTABLE_NAME),
            ("✓", "Captured images folder deleted",  r"%PROGRAMDATA%\AntiTheftCaptures"),
        ]
        for icon, title, detail in removed:
            row = tk.Frame(card, bg=BG2)
            row.pack(fill="x", pady=3)
            tk.Label(row, text=icon, font=("Segoe UI", 11, "bold"),
                     fg=GREEN, bg=BG2).pack(side="left", padx=(0, 10))
            tk.Label(row, text=title, font=("Segoe UI", 10, "bold"),
                     fg=FG, bg=BG2).pack(side="left")
            tk.Label(row, text=f"  —  {detail}", font=("Segoe UI", 9),
                     fg=DIM, bg=BG2).pack(side="left")

        # Note
        note = tk.Frame(self, bg=BG3, pady=8, padx=12)
        note.pack(fill="x", pady=(0, 16))
        tk.Label(note,
                 text="ℹ  Your Telegram bot and chat ID are unaffected.\n"
                      "   You can delete the bot via @BotFather on Telegram at any time.",
                 font=("Segoe UI", 9), fg=DIM, bg=BG3, justify="left").pack(anchor="w")

        # Close button
        btn_bar = tk.Frame(self, bg=BG)
        btn_bar.pack(side="bottom", fill="x", pady=(8, 0))
        tk.Label(btn_bar, text="© 2025 WatchDog Security  —  All Rights Reserved",
                 font=("Segoe UI", 8), fg=DIM, bg=BG).pack(side="left")
        tk.Button(
            btn_bar, text="Close",
            command=sys.exit,
            font=("Segoe UI", 10, "bold"), bg="#3c3c3c", fg=FG,
            activebackground="#4a4a4a", activeforeground="white",
            relief="flat", padx=30, pady=8, cursor="hand2"
        ).pack(side="right")


# ===========================================================================
# ENTRY POINT
# ===========================================================================
if __name__ == "__main__":
    if not is_admin():
        # Auto-elevate: re-launch with admin rights
        result = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        # If elevation was declined (result <= 32) just open normally
        # so the user sees the "Relaunch as Admin" button instead of a crash
        if int(result) > 32:
            sys.exit()

    app = UninstallerApp()
    app.mainloop()
