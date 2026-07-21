import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import ctypes
import json
import shutil
import subprocess
import threading
import time
import webbrowser
try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

# Force Taskbar Icon Persistence early
try:
    myappid = 'watchdog.security.installer.v3'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

# ---------------------------------------------------------------------------
# CONSTANTS & PATHS
# ---------------------------------------------------------------------------
APP_NAME            = "WatchDog Setup"
INSTALL_DIR         = r"C:\Program Files\WatchDog"
EXECUTABLE_NAME     = "WatchDog.exe"         # name written into the install dir
SOURCE_PAYLOAD_NAME = "WatchDog.exe"         # name produced by PyInstaller (dist/WatchDog.exe)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class InstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("680x580")  # Slightly taller to fit T&C + instruction panel
        self.resizable(False, False)
        
        # ── Icon (title bar + taskbar) ────────────────────────────────────────
        try:
            icon_path = get_resource_path("app_icon.ico")
            if not os.path.exists(icon_path):
                icon_path = os.path.join(os.getcwd(), "setup", "app_icon.ico")

            if os.path.exists(icon_path):
                # Title-bar icon
                self.iconbitmap(icon_path)
                # Taskbar icon — wm_iconphoto with a PIL image
                # True = apply to this window AND all future child toplevels
                if Image:
                    _img = Image.open(icon_path).resize((64, 64), Image.LANCZOS)
                    self._icon = ImageTk.PhotoImage(_img)
                    self.wm_iconphoto(True, self._icon)
        except Exception as e:
            print(f"Icon load error: {e}")

        # ── Style Configuration ────────────────────────────────────────────
        style = ttk.Style()
        style.theme_use('clam')
        
        # Professional dark-slate palette (VS Code / modern Windows installer tone)
        BG      = "#1e1e1e"   # main background
        BG2     = "#252526"   # card / panel background
        ACCENT  = "#4A90D9"   # calm steel-blue accent
        GREEN   = "#4EC994"   # muted green for admin badge
        DIM     = "#858585"   # muted/dimmed text
        FG      = "#d4d4d4"   # primary text
        
        self.configure(bg=BG)
        
        style.configure("TFrame",           background=BG)
        style.configure("TLabel",           background=BG,  foreground=FG,     font=("Segoe UI", 10))
        style.configure("TButton",          font=("Segoe UI", 10))
        style.configure("Header.TLabel",    font=("Segoe UI", 20, "bold"),  foreground=ACCENT, background=BG)
        style.configure("SubHeader.TLabel", font=("Segoe UI", 10),          foreground=DIM,    background=BG)
        style.configure("Warning.TLabel",   font=("Segoe UI", 10),          foreground="#ce9178", background=BG)
        style.configure("TLabelframe",      background=BG2,  relief="flat")
        style.configure("TLabelframe.Label",background=BG2,  foreground=ACCENT, font=("Segoe UI", 10, "bold"))
        style.configure("Padded.TEntry",    padding=(8, 4, 4, 4),
                        fieldbackground="#3c3c3c", foreground=FG,
                        insertcolor=FG)
        style.configure("Horizontal.TProgressbar", troughcolor="#3c3c3c",
                        background=ACCENT, thickness=8)

        # Top header strip
        top = tk.Frame(self, bg="#181818", height=36)
        top.pack(fill="x")
        top.pack_propagate(False)
        tk.Label(top, text="🐕  WatchDog Security Installer",
                 font=("Segoe UI", 11, "bold"), fg="#d4d4d4", bg="#181818",
                 pady=8, padx=16).pack(side="left")

        # Main Container
        self.container = ttk.Frame(self, padding="30 8")
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (TermsPage, WelcomePage, ConfigPage, InstallPage, SuccessPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Start on the Welcome / landing page
        self.show_frame("WelcomePage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def get_config_data(self):
        return self.frames["ConfigPage"].get_data()


# ════════════════════════════════════════════════════════════════════════════
# PAGE 0 — TERMS & CONDITIONS
# ════════════════════════════════════════════════════════════════════════════
TERMS_TEXT = """\
WATCHDOG SECURITY SOFTWARE — END-USER LICENSE AGREEMENT (EULA)
Version 3.0  |  Effective: 2025
──────────────────────────────────────────────────────────────────────

1. ACCEPTANCE
   By clicking "I Agree & Continue" you agree to be legally bound by
   this Agreement. If you do not accept these terms, do not install.

2. SOFTWARE DESCRIPTION
   WatchDog is an anti-theft monitoring utility that:
   •  Runs as a hidden background service on Windows.
   •  Monitors failed login attempts via Windows Event ID 4625.
   •  Captures intruder photos using the device camera.
   •  Sends alerts and photos to your configured Telegram Bot.

3. AUTHORISED USE
   You may install WatchDog ONLY on devices that you own or are
   explicitly authorised to manage. Covert installation on devices
   you do NOT own is strictly prohibited and may violate applicable law.

4. PRIVACY & DATA COLLECTION
   WatchDog does NOT transmit any data to the developers or third
   parties. All images and events are sent exclusively to the Telegram
   Bot you configure. You are solely responsible for the security of
   your Bot Token and Chat ID.

5. CAMERA & SYSTEM ACCESS
   This software requires access to:
   ▸ Windows Task Scheduler  — for persistence across reboots
   ▸ Windows Security Log    — to detect failed login attempts
   ▸ Device Camera           — to photograph the intruder
   ▸ Internet / Telegram API — to deliver alerts to your phone
   By proceeding you grant these permissions for the above purposes.

6. DISCLAIMER OF WARRANTIES
   THE SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND.
   THE AUTHORS SHALL NOT BE LIABLE FOR ANY DIRECT, INDIRECT, OR
   CONSEQUENTIAL DAMAGES ARISING FROM ITS USE OR MISUSE.

7. OPEN SOURCE & CREDITS
   WatchDog is an open-source project (MIT License).
   Source: https://github.com/codes-by-utkarsh/WatchDog
   Developed by: Utkarsh Srivastava, Kuldeep Choudhary, Rishi Shah.

8. GOVERNING LAW
   This agreement is governed by Indian law. Disputes shall be
   subject to the jurisdiction of competent courts in India.

BY PROCEEDING YOU CONFIRM THAT YOU HAVE READ, UNDERSTOOD, AND AGREE
TO ALL TERMS AND CONDITIONS OUTLINED ABOVE.
"""

class TermsPage(ttk.Frame):
    """Step 1 — shown after Get Started; user must agree before proceeding."""
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # ── Header ────────────────────────────────────────────────────────
        ttk.Label(self, text="License Agreement", style="Header.TLabel").pack(pady=(4, 2), anchor="w")
        ttk.Label(self, text="Please read the following agreement carefully before installing WatchDog.",
                  style="SubHeader.TLabel").pack(anchor="w", pady=(0, 6))

        # ── Bottom controls FIRST so they are never hidden by the expanding widget
        bottom = tk.Frame(self, bg="#1e1e1e")
        bottom.pack(side="bottom", fill="x", pady=(8, 4))

        self.agreed_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            bottom,
            text="  I have read and accept the Terms and Conditions above.",
            variable=self.agreed_var,
            command=self._on_toggle,
            font=("Segoe UI", 10),
            fg="#d4d4d4", bg="#1e1e1e",
            activeforeground="#4A90D9",
            activebackground="#1e1e1e",
            selectcolor="#3c3c3c",
            cursor="hand2"
        ).pack(anchor="w", pady=(0, 8))

        btn_row = tk.Frame(bottom, bg="#1e1e1e")
        btn_row.pack(fill="x")

        # ← Back to Welcome
        tk.Button(
            btn_row, text="←  Back",
            command=lambda: controller.show_frame("WelcomePage"),
            font=("Segoe UI", 10), bg="#3c3c3c", fg="#d4d4d4",
            activebackground="#4a4a4a", activeforeground="#ffffff",
            relief="flat", padx=16, pady=7, cursor="hand2"
        ).pack(side="left", padx=(0, 6))

        # Decline
        tk.Button(
            btn_row, text="Decline & Exit",
            command=self._decline,
            font=("Segoe UI", 10), bg="#3c3c3c", fg="#ce9178",
            activebackground="#4a4a4a", activeforeground="#e8b4a0",
            relief="flat", padx=16, pady=7, cursor="hand2"
        ).pack(side="left")

        # Proceed (starts disabled)
        self.proceed_btn = tk.Button(
            btn_row, text="I Agree — Continue  →",
            command=self._proceed,
            font=("Segoe UI", 10, "bold"),
            bg="#4A90D9", fg="#ffffff",
            activebackground="#5BA0E0", activeforeground="#ffffff",
            relief="flat", padx=24, pady=7, cursor="hand2",
            state="disabled"
        )
        self.proceed_btn.pack(side="right")

        # ── Scrollable EULA text — packed AFTER bottom so it fills the rest
        txt_frame = ttk.LabelFrame(self, text=" End-User License Agreement ", padding=4)
        txt_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(txt_frame)
        scrollbar.pack(side="right", fill="y")

        self.txt = tk.Text(
            txt_frame,
            font=("Consolas", 9),
            bg="#2d2d30", fg="#c8c8c8",
            wrap="word", relief="flat",
            highlightthickness=0,
            yscrollcommand=scrollbar.set,
            padx=10, pady=8,
            state="normal"
        )
        self.txt.pack(fill="both", expand=True)
        self.txt.insert("1.0", TERMS_TEXT)
        self.txt.config(state="disabled")
        scrollbar.config(command=self.txt.yview)

    def _on_toggle(self):
        self.proceed_btn.config(
            state="normal" if self.agreed_var.get() else "disabled"
        )

    def _proceed(self):
        if not self.agreed_var.get():
            messagebox.showwarning("Agreement Required",
                                   "You must accept the Terms and Conditions to continue.")
            return
        # After agreeing, advance to the configuration step
        self.controller.show_frame("ConfigPage")

    def _decline(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit without installing?"):
            sys.exit()

class WelcomePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Content Frame
        # Bottom Action Area
        action_area = ttk.Frame(self)
        action_area.pack(side="bottom", fill="x", pady=(0, 10)) # Reduced padding to save vertical space

        # Content Frame
        content = ttk.Frame(self)
        content.pack(fill="both", expand=True)

        # Header
        label = ttk.Label(content, text="WatchDog Security", style="Header.TLabel")
        label.pack(pady=(15, 5), anchor="center")
        
        # Subheader / Description
        desc_text = (
            "Advanced Anti-Theft Protection for Windows.\n"
            "Runs silently, Capture intruders & Alerts you instantly."
        )
        ttk.Label(content, text=desc_text, style="SubHeader.TLabel", justify="center").pack(pady=(0, 10), anchor="center")

        # Feature List Container (Centered Block)
        features_frame = ttk.Frame(content)
        features_frame.pack(pady=5, anchor="center")
        
        # Inner-align text to left, but the frame itself is centered
        features = [
            ("🛡️", "Secure Background Service"),
            ("📸", "Instant Camera Capture"),
            ("📱", "Telegram Remote Control")
        ]
        
        for i, (icon, text) in enumerate(features):
            # Icon Column
            lbl = ttk.Label(features_frame, text=icon, font=("Segoe UI", 12), width=3, anchor="center")
            lbl.grid(row=i, column=0, padx=(0, 10), pady=3)
            # Text Column
            ttk.Label(features_frame, text=text, font=("Segoe UI", 11)).grid(row=i, column=1, sticky="w", pady=3)

        # Branding Graphic (Filling the empty space)
        try:
            branding_path = get_resource_path("branding.png")
            if not os.path.exists(branding_path):
                branding_path = os.path.join(os.getcwd(), "setup", "branding.png")
            
            if os.path.exists(branding_path):
                img = Image.open(branding_path)
                # Resize to fit nicely (smaller to fix layout)
                img.thumbnail((160, 90)) 
                self.branding_img = ImageTk.PhotoImage(img)
                branding_lbl = ttk.Label(content, image=self.branding_img)
                branding_lbl.pack(pady=2)
        except Exception as e:
            print(f"Branding load error: {e}")

        # Developer Buttons
        dev_frame = ttk.Frame(content)
        dev_frame.pack(side="bottom", anchor="w", padx=0, pady=(0, 5)) # Absolute Left

        ttk.Label(dev_frame, text="Developed by:", font=("Segoe UI", 10, "bold"),
                  foreground="#858585").pack(anchor="w", pady=(0, 4))

        devs = [
            ("Utkarsh Srivastava (drizzlehx)", "https://www.github.com/codes-by-utkarsh"),
            ("Kuldeep Choudhary (Karlos-5160)", "https://www.github.com/Karlos-5160"),
            ("Rishi Shah (rishis26)",           "https://www.github.com/rishis26")
        ]

        # Clean developer link buttons
        for name, url in devs:
            tk.Button(
                dev_frame, text=f"  {name}",
                command=lambda u=url: webbrowser.open(u),
                font=("Segoe UI", 10), bg="#2d2d30", fg="#4A90D9",
                activebackground="#3a3a3d", activeforeground="#6aaae0",
                relief="flat", bd=0, highlightthickness=0,
                cursor="hand2", anchor="w", padx=8, pady=3
            ).pack(fill="x", pady=1)

        # Admin Check
        if not is_admin():
            ttk.Label(action_area, text="⚠️  Administrator privileges required",
                      style="Warning.TLabel").pack(side="left", padx=10)
            tk.Button(
                action_area, text="Relaunch as Admin",
                command=self.relaunch_admin,
                font=("Segoe UI", 10), bg="#3c3c3c", fg="#d4d4d4",
                activebackground="#4a4a4a", activeforeground="white",
                relief="flat", padx=15, pady=8, cursor="hand2"
            ).pack(side="right")
        else:
            tk.Button(
                action_area, text="Get Started  →",
                command=lambda: controller.show_frame("TermsPage"),
                font=("Segoe UI", 11, "bold"), bg="#4A90D9", fg="#ffffff",
                activebackground="#5BA0E0", activeforeground="#ffffff",
                relief="flat", padx=28, pady=10, cursor="hand2"
            ).pack(side="right")

    def relaunch_admin(self):
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

class ConfigPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Header
        ttk.Label(self, text="Configuration", style="Header.TLabel").pack(pady=(4, 2), anchor="w")
        ttk.Label(self, text="Connect your Telegram Bot to receive security alerts.",
                  style="SubHeader.TLabel").pack(anchor="w", pady=(0, 6))

        # ── How-to guide (collapsible-feel panel) ────────────────────────
        guide_frame = ttk.LabelFrame(self, text=" 📖  How to get your Bot Token & Chat ID ", padding=8)
        guide_frame.pack(fill="x", pady=(0, 8))

        steps_text = (
            "STEP 1 — Create a Telegram Bot:\n"
            "  • Open Telegram → search for  @BotFather  (blue tick, official).\n"
            "  • Send the command:  /newbot\n"
            "  • Follow the prompts — choose a display name, then a username\n"
            "    (must end in 'bot', e.g. MyWatchDog_bot).\n"
            "  • BotFather replies with your  BOT TOKEN  — copy it below.\n\n"
            "STEP 2 — Find your Chat ID:\n"
            "  • Paste your Bot Token above, then click  \"🔍 Get My Chat ID\".\n"
            "  • This opens a Telegram URL in your browser — first send any\n"
            "    message to your new bot on Telegram, then refresh that page.\n"
            "  • Look for  \"id\":XXXXXXXXX  inside  \"chat\":{...}  — that is\n"
            "    your Chat ID. Paste it in the field below."
        )
        guide_lbl = tk.Text(
            guide_frame, font=("Segoe UI", 9),
            bg="#2d2d30", fg="#c8c8c8",
            height=10, relief="flat", highlightthickness=0,
            wrap="word", padx=8, pady=6, state="normal"
        )
        guide_lbl.insert("1.0", steps_text)
        # Highlight keywords in accent blue
        for kw in ["@BotFather", "/newbot", "BOT TOKEN", "🔍 Get My Chat ID",
                   '"id"', '"chat"']:
            start = "1.0"
            while True:
                pos = guide_lbl.search(kw, start, stopindex="end")
                if not pos:
                    break
                end_pos = f"{pos}+{len(kw)}c"
                guide_lbl.tag_add("highlight", pos, end_pos)
                start = end_pos
        guide_lbl.tag_config("highlight", foreground="#4A90D9", font=("Segoe UI", 9, "bold"))
        guide_lbl.config(state="disabled")
        guide_lbl.pack(fill="x")

        # ── Credentials form ─────────────────────────────────────────────
        form_frame = ttk.LabelFrame(self, text=" Telegram Credentials ", padding=10)
        form_frame.pack(fill="x", pady=(0, 4))

        # Token row
        tok_row = ttk.Frame(form_frame)
        tok_row.pack(fill="x", pady=(0, 6))
        ttk.Label(tok_row, text="Bot Token:", font=("Segoe UI", 10, "bold"), width=10).pack(side="left")
        self.token_entry = ttk.Entry(tok_row, font=("Consolas", 11), style="Padded.TEntry")
        self.token_entry.pack(side="left", fill="x", expand=True)

        # Chat ID row
        chat_row = ttk.Frame(form_frame)
        chat_row.pack(fill="x", pady=(0, 6))
        ttk.Label(chat_row, text="Chat ID:", font=("Segoe UI", 10, "bold"), width=10).pack(side="left")
        self.chat_id_entry = ttk.Entry(chat_row, font=("Consolas", 11), style="Padded.TEntry")
        self.chat_id_entry.pack(side="left", fill="x", expand=True)

        # Action buttons row inside form
        btn_row = ttk.Frame(form_frame)
        btn_row.pack(fill="x", pady=(4, 0))

        # "Get Chat ID" button
        self.get_id_btn = tk.Button(
            btn_row, text="🔍 Get My Chat ID",
            command=self._open_get_updates,
            font=("Segoe UI", 9), bg="#3c3c3c", fg="#4A90D9",
            activebackground="#4a4a4a", activeforeground="#6aaae0",
            relief="flat", padx=12, pady=5, cursor="hand2"
        )
        self.get_id_btn.pack(side="left")

        # Test connection
        self.test_btn = tk.Button(
            btn_row, text="📡 Test Connection",
            command=self.test_connection,
            font=("Segoe UI", 9), bg="#3c3c3c", fg="#4EC994",
            activebackground="#4a4a4a", activeforeground="#6ad4a8",
            relief="flat", padx=12, pady=5, cursor="hand2"
        )
        self.test_btn.pack(side="right")

        # Navigation
        nav_frame = ttk.Frame(self)
        nav_frame.pack(side="bottom", fill="x", pady=(0, 10))
        
        bk_btn = tk.Button(
            nav_frame, text="← Back",
            command=lambda: controller.show_frame("WelcomePage"),
            font=("Segoe UI", 10), bg="#3c3c3c", fg="#d4d4d4",
            activebackground="#4a4a4a", activeforeground="white",
            relief="flat", padx=20, pady=9, cursor="hand2"
        )
        bk_btn.pack(side="left")
        
        next_btn = tk.Button(
            nav_frame, text="Install Now  ▶",
            command=self.validate_and_proceed,
            font=("Segoe UI", 11, "bold"), bg="#4A90D9", fg="white",
            activebackground="#5BA0E0", activeforeground="white",
            relief="flat", padx=36, pady=9, cursor="hand2"
        )
        next_btn.pack(side="right")

    def _open_get_updates(self):
        """Open the Telegram getUpdates URL in the browser so the user can
        read their Chat ID.  The token must be filled in first."""
        token = self.token_entry.get().strip()
        if not token:
            messagebox.showwarning(
                "Token Required",
                "Please paste your Bot Token first, then click this button.\n\n"
                "After opening the page, send any message to your bot on Telegram\n"
                "and refresh the browser page to see your Chat ID in the JSON."
            )
            return
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        webbrowser.open(url)
        messagebox.showinfo(
            "Browser Opened",
            f"Opened:\n{url}\n\n"
            "If the page shows empty results:\n"
            " 1. Go to Telegram and send any message to your bot.\n"
            " 2. Refresh the browser page.\n"
            " 3. Find  \"id\":XXXXXXXXX  inside the \"chat\" object — that's your Chat ID."
        )

    def test_connection(self):
        token = self.token_entry.get().strip()
        chat_id = self.chat_id_entry.get().strip()
        
        if not token or not chat_id:
            messagebox.showwarning("Missing Info", "Please enter both Token and Chat ID first.")
            return

        self.test_btn.config(state="disabled", text="Testing...")
        
        def run_test():
            try:
                import urllib.request, urllib.parse
                url  = f"https://api.telegram.org/bot{token}/sendMessage"
                data = urllib.parse.urlencode({
                    "chat_id": chat_id,
                    "text": "🔔 WatchDog Installer: Connection Successful!"
                }).encode()
                req  = urllib.request.Request(url, data=data, method="POST")
                with urllib.request.urlopen(req, timeout=7) as resp:
                    if resp.status == 200:
                        self.after(0, lambda: messagebox.showinfo(
                            "Success", "✅ Test message sent! Check your Telegram."))
                    else:
                        raise Exception(f"HTTP {resp.status}")
            except Exception as e:
                 self.after(0, lambda: messagebox.showerror("Connection Error", str(e)))
            finally:
                 self.after(0, lambda: self.test_btn.config(state="normal", text="📡 Test Connection"))

        threading.Thread(target=run_test, daemon=True).start()

    def get_data(self):
        return {
            "bot_token": self.token_entry.get().strip(),
            "chat_id": self.chat_id_entry.get().strip()
        }

    def validate_and_proceed(self):
        data = self.get_data()
        if not data["bot_token"] or not data["chat_id"]:
            messagebox.showerror("Error", "Please fill in all fields.")
            return
        self.controller.show_frame("InstallPage")
        self.controller.frames["InstallPage"].start_install()

class InstallPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Header
        label = ttk.Label(self, text="Installing WatchDog...", style="Header.TLabel")
        label.pack(pady=(10, 20))

        # Progress Status
        self.status_var = tk.StringVar(value="Initializing...")
        status_label = ttk.Label(self, textvariable=self.status_var, font=("Segoe UI", 11))
        status_label.pack(anchor="w", pady=5)

        # Progress Bar (Thicker appearance via layout or just better padding)
        self.progress = ttk.Progressbar(self, orient="horizontal", length=450, mode="determinate")
        self.progress.pack(pady=(0, 20), ipady=5)

        # Terminal-style Log
        log_frame = ttk.LabelFrame(self, text=" System Log ", padding=5)
        log_frame.pack(fill="both", expand=True, pady=5)
        
        self.log_text = tk.Text(log_frame, height=12, width=60, 
                               font=("Consolas", 9), state="disabled",
                               bg="#1e1e1e", fg="#4EC994",
                               relief="flat", highlightthickness=0)
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", "> " + message + "\n") # > Prefix for terminal feel
        self.log_text.see("end")
        self.log_text.config(state="disabled")
        self.status_var.set(message)
        self.update_idletasks()

    def start_install(self):
        threading.Thread(target=self.run_installation, daemon=True).start()

    def run_installation(self):
        try:
            self.progress['value'] = 0
            
            # 1. Prepare Directory
            self.log(f"Creating directory: {INSTALL_DIR}")
            if not os.path.exists(INSTALL_DIR):
                os.makedirs(INSTALL_DIR)
            time.sleep(0.5) # Pace: Pause
            self.progress['value'] = 20

            # 2. Extract Files
            self.log("Copying service executable...")
            src_exe = get_resource_path(SOURCE_PAYLOAD_NAME)
            if not os.path.exists(src_exe):
                # Fallback for dev mode
                src_exe = os.path.join(os.getcwd(), "dist", SOURCE_PAYLOAD_NAME)
            
            if not os.path.exists(src_exe):
                raise Exception(f"Source file not found: {src_exe}")

            dest_exe = os.path.join(INSTALL_DIR, EXECUTABLE_NAME)
            shutil.copy2(src_exe, dest_exe)
            
            # Copy Uninstaller
            self.log("Copying uninstaller...")
            try:
                src_uninstall = get_resource_path("uninstall.exe")
                if not os.path.exists(src_uninstall):
                    # Fallback
                    src_uninstall = os.path.join(os.getcwd(), "dist", "uninstall.exe")
                
                if os.path.exists(src_uninstall):
                    dest_uninstall = os.path.join(INSTALL_DIR, "uninstall.exe")
                    shutil.copy2(src_uninstall, dest_uninstall)
                else:
                    self.log("Warning: uninstall.exe not found in bundle.")
            except Exception as e:
                self.log(f"Warning: Failed to copy uninstaller: {e}")

            self.progress['value'] = 40
            time.sleep(0.6) # Pace: Pause after copying files

            # 3. Create Config
            self.log("Generating configuration...")
            config_data = self.controller.get_config_data()
            full_config = {
                "telegram": config_data,
                "security": {
                    "failed_attempt_threshold": 2,
                    "event_id": 4625,
                    "check_interval_seconds": 0.1
                },
                "camera": {"device_index": 0}
            }
            
            with open(os.path.join(INSTALL_DIR, "config.json"), "w") as f:
                json.dump(full_config, f, indent=4)
            time.sleep(0.8) # Pace: Pause
            self.progress['value'] = 60

            # 4. Cleanup Old Tasks
            self.log("Stopping old services...")
            subprocess.run(["taskkill", "/F", "/IM", EXECUTABLE_NAME], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run(["schtasks", "/Delete", "/TN", "AntiTheft_Service", "/F"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run(["schtasks", "/Delete", "/TN", "AntiTheft_Commander", "/F"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            time.sleep(0.4) # Pace: Pause
            self.progress['value'] = 70

            # 5. Create Tasks
            self.log("Registering System Service...")
            self.create_service_task(dest_exe)
            
            self.log("Registering User Commander...")
            self.create_commander_task(dest_exe)
            time.sleep(0.8) # Pace: Pause
            self.progress['value'] = 90

            # 6. Start Tasks
            self.log("Starting services...")
            subprocess.run(["schtasks", "/Run", "/TN", "AntiTheft_Service"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            subprocess.run(["schtasks", "/Run", "/TN", "AntiTheft_Commander"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            time.sleep(1.0) # Pace: Final completion pause
            self.progress['value'] = 100
            self.log("Installation Complete!")
            time.sleep(1)
            self.controller.show_frame("SuccessPage")

        except Exception as e:
            messagebox.showerror("Installation Failed", str(e))
            self.log(f"Error: {e}")

    def create_service_task(self, exe_path):
        # Use XML to avoid quoting/parsing issues with spaces in paths
        xml_content = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>WatchDog Security Service (System)</Description>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
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
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>true</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
    <RestartOnFailure>
      <Interval>PT1M</Interval>
      <Count>999</Count>
    </RestartOnFailure>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{exe_path}</Command>
      <Arguments>--service</Arguments>
      <WorkingDirectory>{os.path.dirname(exe_path)}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''
        
        xml_path = os.path.join(os.environ['TEMP'], "wd_service.xml")
        with open(xml_path, "w", encoding="utf-16") as f:
            f.write(xml_content)
            
        try:
            cmd = ['schtasks', '/Create', '/TN', 'AntiTheft_Service', '/XML', xml_path, '/F']
            subprocess.run(cmd, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        finally:
            if os.path.exists(xml_path):
                os.remove(xml_path)

    def create_commander_task(self, exe_path):
        # Current User, Logon Trigger
        # We need to get the current user ID for the task principal?
        # Actually for a user task, simpler XML or interactive creation might be better,
        # but XML allows us to specify "RunLevel Highest" easily.
        
        # NOTE: When running as Admin installer, "S-1-5-32-544" (Admins) or similar might be context.
        # But we want it to run for the LOGGED ON USER.
        # <GroupId>S-1-5-32-545</GroupId> (Users) doesn't work well for specific logon.
        # For simplicity in this wizard, we'll configure it to run for the *User who installs it* 
        # (assuming they are the owner) OR use the generic LogonTrigger for "Any User".
        
        xml_content = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>WatchDog User Agent (Commander)</Description>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <GroupId>S-1-5-32-545</GroupId>
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
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>true</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
    <RestartOnFailure>
      <Interval>PT1M</Interval>
      <Count>999</Count>
    </RestartOnFailure>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{exe_path}</Command>
      <Arguments>--commander</Arguments>
      <WorkingDirectory>{os.path.dirname(exe_path)}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''

        xml_path = os.path.join(os.environ['TEMP'], "wd_commander.xml")
        with open(xml_path, "w", encoding="utf-16") as f:
            f.write(xml_content)
            
        try:
            cmd = ['schtasks', '/Create', '/TN', 'AntiTheft_Commander', '/XML', xml_path, '/F']
            subprocess.run(cmd, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        finally:
            if os.path.exists(xml_path):
                os.remove(xml_path)

class SuccessPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Footer Frame (Packed FIRST to reserve bottom space)
        footer = ttk.Frame(self)
        footer.pack(side="bottom", fill="x", pady=5)

        # Close Button (Inside Footer)
        tk.Button(footer, text="Close", command=lambda: sys.exit(),
                 font=("Segoe UI", 12, "bold"), 
                 bg="#333333", fg="white", 
                 activebackground="#555555", activeforeground="white",
                 relief="flat", padx=30, pady=10, cursor="hand2").pack(side="top", pady=(0, 15))

        # Copyright Text (Inside Footer)
        ttk.Label(footer, text="© Copyright All Rights Reserved.", 
                 font=("Segoe UI", 9, "bold"), foreground="#333333").pack(side="bottom")

        # Main Container (Packed LAST to fill remaining space)
        content = ttk.Frame(self)
        content.pack(fill="both", expand=True, padx=20)

        # Success Header (Increased Size)
        lbl = ttk.Label(content, text="Installation Complete!", font=("Segoe UI", 24, "bold"), foreground="#28a745")
        lbl.pack(pady=(5, 0))

        # Subheader (Increased Size)
        ttk.Label(content, text="WatchDog Security is now active.", 
                 font=("Segoe UI", 13), foreground="#555555").pack(pady=(0, 10))

        # Status Checklist Frame
        status_frame = ttk.LabelFrame(content, text=" System Status ", padding=5)
        status_frame.pack(fill="x", pady=4)

        checklist = [
            ("✅", "System Service Installed", "Running (Auto-Start)"),
            ("✅", "Security Monitor Active", "Listening for Events"),
            ("✅", "Telegram Connection", "Configured & Ready")
        ]

        for i, (icon, title, status) in enumerate(checklist):
             # Icon (Larger)
             ttk.Label(status_frame, text=icon, font=("Segoe UI", 14)).grid(row=i, column=0, padx=5, pady=2)
             # Title (Larger)
             ttk.Label(status_frame, text=title, font=("Segoe UI", 12, "bold")).grid(row=i, column=1, sticky="w", padx=2)
             # Status Detail (Larger)
             ttk.Label(status_frame, text=status, font=("Segoe UI", 11), foreground="#666666").grid(row=i, column=2, sticky="w", padx=5)

        # Next Steps Section
        steps_frame = ttk.Frame(content)
        steps_frame.pack(fill="x", pady=16)
        
        ttk.Label(steps_frame, text="👉 Next Steps:", font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 2))
        
        steps_text = (
            "1. Lock your screen (Win + L).\n"
            "2. Enter a wrong password to trigger the alarm.\n"
            "3. Check your Telegram for the photo alert."
        )
        ttk.Label(steps_frame, text=steps_text, font=("Segoe UI", 11), justify="left").pack(anchor="w", padx=10, pady=(0, 6))

        # End of SuccessPage


if __name__ == "__main__":
    if not is_admin():
        # Re-run admin check in GUI class, but basic check here
        pass
    
    app = InstallerApp()
    app.mainloop()