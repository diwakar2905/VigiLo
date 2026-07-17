# ui/installer_gui.py
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import threading
import time
import webbrowser

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None

# Custom imports
from ui.styles import BG, ACCENT, GREEN, WARN, DIM, FG, apply_styles
from security.privilege import is_admin
from utils.system import get_resource_path
from core.install_engine import InstallEngine

APP_NAME = "VigiLo Setup"
TERMS_TEXT = """\
VIGILO SECURITY SOFTWARE — END-USER LICENSE AGREEMENT (EULA)
Version 3.0  |  Effective: 2025
──────────────────────────────────────────────────────────────────────

1. ACCEPTANCE
   By clicking "I Agree & Continue" you agree to be legally bound by
   this Agreement. If you do not accept these terms, do not install.

2. SOFTWARE DESCRIPTION
   VigiLo is an anti-theft monitoring utility that:
   •  Runs as a hidden background service on Windows.
   •  Monitors failed login attempts via Windows Event ID 4625.
   •  Captures intruder photos using the device camera.
   •  Sends alerts and photos to your configured Telegram Bot.

3. AUTHORISED USE
   You may install VigiLo ONLY on devices that you own or are
   explicitly authorised to manage. Covert installation on devices
   you do NOT own is strictly prohibited and may violate applicable law.

4. PRIVACY & DATA COLLECTION
   VigiLo does NOT transmit any data to the developers or third
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
    VigiLo is an open-source project (MIT License).
    Source: https://github.com/diwakar2905/VigiLo
    Developed by: Diwakar Mishra and Open Source Contributors.

8. GOVERNING LAW
   This agreement is governed by Indian law. Disputes shall be
   subject to the jurisdiction of competent courts in India.

BY PROCEEDING YOU CONFIRM THAT YOU HAVE READ, UNDERSTOOD, AND AGREE
TO ALL TERMS AND CONDITIONS OUTLINED ABOVE.
"""


class InstallerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("680x580")
        self.resizable(False, False)
        self.configure(bg=BG)

        # Force Taskbar Icon ID
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
                "vigilo.security.installer.v3"
            )
        except Exception:
            pass

        # Load Titlebar Icons
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

        # Header strip
        top = tk.Frame(self, bg="#181818", height=36)
        top.pack(fill="x")
        top.pack_propagate(False)
        tk.Label(
            top,
            text="🐕  VigiLo Security Installer",
            font=("Segoe UI", 11, "bold"),
            fg=FG,
            bg="#181818",
            pady=8,
            padx=16,
        ).pack(side="left")

        # Container
        self.container = ttk.Frame(self, padding="30 8")
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (
            TermsPage,
            WelcomePage,
            ConfigPage,
            FaceEnrollPage,
            InstallPage,
            SuccessPage,
        ):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.show_frame("WelcomePage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def get_config_data(self):
        data = self.frames["ConfigPage"].get_data()
        enroll_page = self.frames.get("FaceEnrollPage")
        if enroll_page:
            data["face_verification"] = enroll_page.get_data()
        return data


class TermsPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="License Agreement", style="Header.TLabel").pack(
            pady=(4, 2), anchor="w"
        )
        ttk.Label(
            self,
            text="Please read the following agreement carefully before installing VigiLo.",
            style="SubHeader.TLabel",
        ).pack(anchor="w", pady=(0, 6))

        bottom = tk.Frame(self, bg=BG)
        bottom.pack(side="bottom", fill="x", pady=(8, 4))

        self.agreed_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            bottom,
            text="  I have read and accept the Terms and Conditions above.",
            variable=self.agreed_var,
            command=self._on_toggle,
            font=("Segoe UI", 10),
            fg=FG,
            bg=BG,
            activeforeground=ACCENT,
            activebackground=BG,
            selectcolor="#3c3c3c",
            cursor="hand2",
        ).pack(anchor="w", pady=(0, 8))

        btn_row = tk.Frame(bottom, bg=BG)
        btn_row.pack(fill="x")

        tk.Button(
            btn_row,
            text="←  Back",
            command=lambda: controller.show_frame("WelcomePage"),
            font=("Segoe UI", 10),
            bg="#3c3c3c",
            fg=FG,
            activebackground="#4a4a4a",
            activeforeground="#ffffff",
            relief="flat",
            padx=16,
            pady=7,
            cursor="hand2",
        ).pack(side="left", padx=(0, 6))

        tk.Button(
            btn_row,
            text="Decline & Exit",
            command=self._decline,
            font=("Segoe UI", 10),
            bg="#3c3c3c",
            fg=WARN,
            activebackground="#4a4a4a",
            activeforeground="#e8b4a0",
            relief="flat",
            padx=16,
            pady=7,
            cursor="hand2",
        ).pack(side="left")

        self.proceed_btn = tk.Button(
            btn_row,
            text="I Agree — Continue  →",
            command=self._proceed,
            font=("Segoe UI", 10, "bold"),
            bg=ACCENT,
            fg="#ffffff",
            activebackground="#5BA0E0",
            activeforeground="#ffffff",
            relief="flat",
            padx=24,
            pady=7,
            cursor="hand2",
            state="disabled",
        )
        self.proceed_btn.pack(side="right")

        txt_frame = ttk.LabelFrame(self, text=" End-User License Agreement ", padding=4)
        txt_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(txt_frame)
        scrollbar.pack(side="right", fill="y")

        self.txt = tk.Text(
            txt_frame,
            font=("Consolas", 9),
            bg="#2d2d30",
            fg="#c8c8c8",
            wrap="word",
            relief="flat",
            highlightthickness=0,
            yscrollcommand=scrollbar.set,
            padx=10,
            pady=8,
            state="normal",
        )
        self.txt.pack(fill="both", expand=True)
        self.txt.insert("1.0", TERMS_TEXT)
        self.txt.config(state="disabled")
        scrollbar.config(command=self.txt.yview)

    def _on_toggle(self):
        self.proceed_btn.config(state="normal" if self.agreed_var.get() else "disabled")

    def _proceed(self):
        if not self.agreed_var.get():
            messagebox.showwarning(
                "Agreement Required",
                "You must accept the Terms and Conditions to continue.",
            )
            return
        self.controller.show_frame("ConfigPage")

    def _decline(self):
        if messagebox.askyesno(
            "Exit", "Are you sure you want to exit without installing?"
        ):
            sys.exit()


class WelcomePage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        action_area = ttk.Frame(self)
        action_area.pack(side="bottom", fill="x", pady=(0, 10))

        content = ttk.Frame(self)
        content.pack(fill="both", expand=True)

        label = ttk.Label(content, text="VigiLo Security", style="Header.TLabel")
        label.pack(pady=(15, 5), anchor="center")

        desc_text = (
            "Advanced Anti-Theft Protection for Windows.\n"
            "Runs silently, captures intruders & alerts you instantly."
        )
        ttk.Label(
            content, text=desc_text, style="SubHeader.TLabel", justify="center"
        ).pack(pady=(0, 10), anchor="center")

        features_frame = ttk.Frame(content)
        features_frame.pack(pady=5, anchor="center")

        features = [
            ("🛡️", "Secure Background Service"),
            ("📸", "Instant Camera Capture"),
            ("📱", "Telegram Remote Control"),
        ]

        for i, (icon, text) in enumerate(features):
            lbl = ttk.Label(
                features_frame,
                text=icon,
                font=("Segoe UI", 12),
                width=3,
                anchor="center",
            )
            lbl.grid(row=i, column=0, padx=(0, 10), pady=3)
            ttk.Label(features_frame, text=text, font=("Segoe UI", 11)).grid(
                row=i, column=1, sticky="w", pady=3
            )

        # Branding Graphic
        try:
            branding_path = get_resource_path("branding.png")
            if not os.path.exists(branding_path):
                branding_path = os.path.join(os.getcwd(), "setup", "branding.png")

            if os.path.exists(branding_path) and Image:
                img = Image.open(branding_path)
                img.thumbnail((160, 90))
                self.branding_img = ImageTk.PhotoImage(img)
                branding_lbl = ttk.Label(content, image=self.branding_img)
                branding_lbl.pack(pady=2)
        except Exception as e:
            print(f"Branding load error: {e}")

        dev_frame = ttk.Frame(content)
        dev_frame.pack(side="bottom", anchor="w", padx=0, pady=(0, 5))

        ttk.Label(
            dev_frame,
            text="Developed by:",
            font=("Segoe UI", 10, "bold"),
            foreground=DIM,
        ).pack(anchor="w", pady=(0, 4))

        devs = [
            ("Diwakar Mishra (diwakar2905)", "https://www.github.com/diwakar2905"),
        ]

        for name, url in devs:
            tk.Button(
                dev_frame,
                text=f"  {name}",
                command=lambda u=url: webbrowser.open(u),
                font=("Segoe UI", 10),
                bg="#2d2d30",
                fg=ACCENT,
                activebackground="#3a3a3d",
                activeforeground="#6aaae0",
                relief="flat",
                bd=0,
                highlightthickness=0,
                cursor="hand2",
                anchor="w",
                padx=8,
                pady=3,
            ).pack(fill="x", pady=1)

        if not is_admin():
            ttk.Label(
                action_area,
                text="⚠️  Administrator privileges required",
                style="Warning.TLabel",
            ).pack(side="left", padx=10)
            tk.Button(
                action_area,
                text="Relaunch as Admin",
                command=self.relaunch_admin,
                font=("Segoe UI", 10),
                bg="#3c3c3c",
                fg=FG,
                activebackground="#4a4a4a",
                activeforeground="white",
                relief="flat",
                padx=15,
                pady=8,
                cursor="hand2",
            ).pack(side="right")
        else:
            tk.Button(
                action_area,
                text="Get Started  →",
                command=lambda: controller.show_frame("TermsPage"),
                font=("Segoe UI", 11, "bold"),
                bg=ACCENT,
                fg="#ffffff",
                activebackground="#5BA0E0",
                activeforeground="#ffffff",
                relief="flat",
                padx=28,
                pady=10,
                cursor="hand2",
            ).pack(side="right")

    def relaunch_admin(self):
        import ctypes

        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()


class ConfigPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Configuration", style="Header.TLabel").pack(
            pady=(4, 2), anchor="w"
        )
        ttk.Label(
            self,
            text="Connect your Telegram Bot to receive security alerts.",
            style="SubHeader.TLabel",
        ).pack(anchor="w", pady=(0, 6))

        guide_frame = ttk.LabelFrame(
            self, text=" 📖  How to get your Bot Token & Chat ID ", padding=8
        )
        guide_frame.pack(fill="x", pady=(0, 8))

        steps_text = (
            "STEP 1 — Create a Telegram Bot:\n"
            "  • Open Telegram → search for  @BotFather  (blue tick, official).\n"
            "  • Send the command:  /newbot\n"
            "  • Follow the prompts — choose a display name, then a username\n"
            "    (must end in 'bot', e.g. MyVigiLo_bot).\n"
            "  • BotFather replies with your  BOT TOKEN  — copy it below.\n\n"
            "STEP 2 — Find your Chat ID:\n"
            '  • Paste your Bot Token above, then click  "🔍 Get My Chat ID".\n'
            "  • This opens a Telegram URL in your browser — first send any\n"
            "    message to your new bot on Telegram, then refresh that page.\n"
            '  • Look for  "id":XXXXXXXXX  inside  "chat":{...}  — that is\n'
            "    your Chat ID. Paste it in the field below."
        )
        guide_lbl = tk.Text(
            guide_frame,
            font=("Segoe UI", 9),
            bg="#2d2d30",
            fg="#c8c8c8",
            height=10,
            relief="flat",
            highlightthickness=0,
            wrap="word",
            padx=8,
            pady=6,
            state="normal",
        )
        guide_lbl.insert("1.0", steps_text)

        for kw in [
            "@BotFather",
            "/newbot",
            "BOT TOKEN",
            "🔍 Get My Chat ID",
            '"id"',
            '"chat"',
        ]:
            start = "1.0"
            while True:
                pos = guide_lbl.search(kw, start, stopindex="end")
                if not pos:
                    break
                end_pos = f"{pos}+{len(kw)}c"
                guide_lbl.tag_add("highlight", pos, end_pos)
                start = end_pos
        guide_lbl.tag_config(
            "highlight", foreground=ACCENT, font=("Segoe UI", 9, "bold")
        )
        guide_lbl.config(state="disabled")
        guide_lbl.pack(fill="x")

        form_frame = ttk.LabelFrame(self, text=" Telegram Credentials ", padding=10)
        form_frame.pack(fill="x", pady=(0, 4))

        tok_row = ttk.Frame(form_frame)
        tok_row.pack(fill="x", pady=(0, 6))
        ttk.Label(
            tok_row, text="Bot Token:", font=("Segoe UI", 10, "bold"), width=10
        ).pack(side="left")
        self.token_entry = ttk.Entry(
            tok_row, font=("Consolas", 11), style="Padded.TEntry"
        )
        self.token_entry.pack(side="left", fill="x", expand=True)

        chat_row = ttk.Frame(form_frame)
        chat_row.pack(fill="x", pady=(0, 6))
        ttk.Label(
            chat_row, text="Chat ID:", font=("Segoe UI", 10, "bold"), width=10
        ).pack(side="left")
        self.chat_id_entry = ttk.Entry(
            chat_row, font=("Consolas", 11), style="Padded.TEntry"
        )
        self.chat_id_entry.pack(side="left", fill="x", expand=True)

        btn_row = ttk.Frame(form_frame)
        btn_row.pack(fill="x", pady=(4, 0))

        self.get_id_btn = tk.Button(
            btn_row,
            text="🔍 Get My Chat ID",
            command=self._open_get_updates,
            font=("Segoe UI", 9),
            bg="#3c3c3c",
            fg=ACCENT,
            activebackground="#4a4a4a",
            activeforeground="#6aaae0",
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
        )
        self.get_id_btn.pack(side="left")

        self.test_btn = tk.Button(
            btn_row,
            text="📡 Test Connection",
            command=self.test_connection,
            font=("Segoe UI", 9),
            bg="#3c3c3c",
            fg=GREEN,
            activebackground="#4a4a4a",
            activeforeground="#6ad4a8",
            relief="flat",
            padx=12,
            pady=5,
            cursor="hand2",
        )
        self.test_btn.pack(side="right")

        nav_frame = ttk.Frame(self)
        nav_frame.pack(side="bottom", fill="x", pady=(0, 10))

        bk_btn = tk.Button(
            nav_frame,
            text="← Back",
            command=lambda: controller.show_frame("TermsPage"),
            font=("Segoe UI", 10),
            bg="#3c3c3c",
            fg=FG,
            activebackground="#4a4a4a",
            activeforeground="white",
            relief="flat",
            padx=20,
            pady=9,
            cursor="hand2",
        )
        bk_btn.pack(side="left")

        next_btn = tk.Button(
            nav_frame,
            text="Install Now  ▶",
            command=self.validate_and_proceed,
            font=("Segoe UI", 11, "bold"),
            bg=ACCENT,
            fg="white",
            activebackground="#5BA0E0",
            activeforeground="white",
            relief="flat",
            padx=36,
            pady=9,
            cursor="hand2",
        )
        next_btn.pack(side="right")

    def _open_get_updates(self):
        token = self.token_entry.get().strip()
        if not token:
            messagebox.showwarning(
                "Token Required",
                "Please paste your Bot Token first, then click this button.\n\n"
                "After opening the page, send any message to your bot on Telegram\n"
                "and refresh the browser page to see your Chat ID in the JSON.",
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
            ' 3. Find  "id":XXXXXXXXX  inside the "chat" object.',
        )

    def test_connection(self):
        token = self.token_entry.get().strip()
        chat_id = self.chat_id_entry.get().strip()

        if not token or not chat_id:
            messagebox.showwarning(
                "Missing Info", "Please enter both Token and Chat ID first."
            )
            return

        self.test_btn.config(state="disabled", text="Testing...")

        def run_test():
            try:
                import urllib.request
                import urllib.parse

                url = f"https://api.telegram.org/bot{token}/sendMessage"
                data = urllib.parse.urlencode(
                    {
                        "chat_id": chat_id,
                        "text": "🔔 VigiLo Installer: Connection Successful!",
                    }
                ).encode()
                req = urllib.request.Request(url, data=data, method="POST")
                with urllib.request.urlopen(req, timeout=7) as resp:
                    if resp.status == 200:
                        self.after(
                            0,
                            lambda: messagebox.showinfo(
                                "Success",
                                "✅ Connection successful! Test message sent to your Telegram.",
                            ),
                        )
                    else:
                        raise Exception(f"HTTP {resp.status}")
            except Exception as e:
                err_msg = str(e)
                self.after(
                    0,
                    lambda: messagebox.showerror(
                        "Connection Error", f"Failed to connect: {err_msg}"
                    ),
                )
            finally:
                self.after(
                    0,
                    lambda: self.test_btn.config(
                        state="normal", text="📡 Test Connection"
                    ),
                )

        threading.Thread(target=run_test, daemon=True).start()

    def get_data(self):
        return {
            "bot_token": self.token_entry.get().strip(),
            "chat_id": self.chat_id_entry.get().strip(),
        }

    def validate_and_proceed(self):
        data = self.get_data()
        if not data["bot_token"] or not data["chat_id"]:
            messagebox.showerror("Error", "Please fill in all configuration fields.")
            return
        self.controller.show_frame("FaceEnrollPage")
        self.controller.frames["FaceEnrollPage"].on_visible()


class FaceEnrollPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.enrolled_embeddings = []
        self.enabled = False

        ttk.Label(
            self, text="Face Verification Enrollment", style="Header.TLabel"
        ).pack(pady=(10, 2))
        ttk.Label(
            self,
            text="Reduce false alarms by verifying your face when wrong password login attempts occur.",
            style="SubHeader.TLabel",
        ).pack(anchor="w", pady=(0, 10))

        # Status Panel
        self.status_panel = ttk.LabelFrame(self, text=" Status / Console ", padding=10)
        self.status_panel.pack(fill="both", expand=True, pady=5)

        self.status_text = tk.Text(
            self.status_panel,
            height=10,
            width=60,
            font=("Consolas", 9),
            state="disabled",
            bg="#1e1e1e",
            fg=FG,
            relief="flat",
            highlightthickness=0,
        )
        self.status_text.pack(fill="both", expand=True, padx=5, pady=5)

        # Control Row
        self.btn_frame = tk.Frame(self, bg=BG)
        self.btn_frame.pack(fill="x", side="bottom", pady=(10, 4))

        self.back_btn = tk.Button(
            self.btn_frame,
            text="← Back",
            command=self._go_back,
            font=("Segoe UI", 10),
            bg="#3c3c3c",
            fg=FG,
            relief="flat",
            padx=16,
            pady=7,
            cursor="hand2",
        )
        self.back_btn.pack(side="left", padx=(0, 6))

        self.skip_btn = tk.Button(
            self.btn_frame,
            text="Skip / Password Only",
            command=self._skip,
            font=("Segoe UI", 10),
            bg="#3c3c3c",
            fg=FG,
            relief="flat",
            padx=16,
            pady=7,
            cursor="hand2",
        )
        self.skip_btn.pack(side="left", padx=(0, 6))

        self.enroll_btn = tk.Button(
            self.btn_frame,
            text="👤 Enroll Face",
            command=self._enroll,
            font=("Segoe UI", 10, "bold"),
            bg=ACCENT,
            fg=FG,
            relief="flat",
            padx=16,
            pady=7,
            cursor="hand2",
            state="disabled",
        )
        self.enroll_btn.pack(side="right", padx=(0, 6))

    def log(self, msg):
        self.status_text.config(state="normal")
        self.status_text.insert("end", "> " + msg + "\n")
        self.status_text.see("end")
        self.status_text.config(state="disabled")
        self.update_idletasks()

    def get_data(self):
        return {
            "enabled": self.enabled,
            "threshold": 0.363,
            "reference_embeddings": self.enrolled_embeddings,
        }

    def _go_back(self):
        self.controller.show_frame("ConfigPage")

    def _skip(self):
        self.enabled = False
        self.enrolled_embeddings = []
        self.controller.show_frame("InstallPage")
        self.controller.frames["InstallPage"].start_install()

    def on_visible(self):
        self.status_text.config(state="normal")
        self.status_text.delete("1.0", "end")
        self.status_text.config(state="disabled")
        self.log("Initializing Face Verification Enrollment...")
        self.enroll_btn.config(state="disabled")
        self.skip_btn.config(
            text="Skip / Password Only", command=self._skip, bg="#3c3c3c"
        )

        # Start background model check
        threading.Thread(target=self._check_and_prepare_models, daemon=True).start()

    def _check_and_prepare_models(self):
        from modules.face_verification import (
            get_model_paths,
            YUNET_URL,
            YUNET_HASH,
            SFACE_URL,
            SFACE_HASH,
        )
        from utils.network import download_file_with_checksum, check_internet

        yunet_path, sface_path = get_model_paths()

        if os.path.exists(yunet_path) and os.path.exists(sface_path):
            self.log("Model files already cached offline.")
            self.after(0, lambda: self.enroll_btn.config(state="normal"))
            self.log("Click 'Enroll Face' to begin face registration.")
            return

        self.log("Required face models not found locally.")
        self.log("Checking internet connection...")
        if not check_internet():
            self.log("Offline: Cannot download models. Face verification is disabled.")
            self.log(
                "Click 'Skip / Password Only' to proceed without face verification."
            )
            return

        self.log("Downloading models (YuNet detector ~3MB, SFace recognizer ~15MB)...")
        # Download YuNet
        if not os.path.exists(yunet_path):
            self.log("Downloading face detection model...")
            ok = download_file_with_checksum(YUNET_URL, yunet_path, YUNET_HASH)
            if not ok:
                self.log(
                    "Error downloading face detection model. Checksum mismatch or network error."
                )
                return

        # Download SFace
        if not os.path.exists(sface_path):
            self.log("Downloading face recognition model...")
            ok = download_file_with_checksum(SFACE_URL, sface_path, SFACE_HASH)
            if not ok:
                self.log(
                    "Error downloading face recognition model. Checksum mismatch or network error."
                )
                return

        self.log("Model downloads completed and verified successfully!")
        self.after(0, lambda: self.enroll_btn.config(state="normal"))
        self.log("Click 'Enroll Face' to begin face registration.")

    def _enroll(self):
        self.enroll_btn.config(state="disabled")
        self.back_btn.config(state="disabled")
        self.skip_btn.config(state="disabled")
        self.log(
            "Starting enrollment camera capture in 3 seconds. Please look at the camera."
        )

        def run_enroll():
            import time
            from modules.camera import CameraModule
            from modules.face_verification import (
                FaceVerificationModule,
                serialize_embedding,
                get_model_paths,
            )
            from utils.system import get_captures_dir

            time.sleep(3)
            device_idx = 0

            camera = CameraModule(device_index=device_idx)
            captures_dir = get_captures_dir()

            yunet_path, sface_path = get_model_paths()
            fvm = FaceVerificationModule(yunet_path=yunet_path, sface_path=sface_path)

            embeddings = []
            success_count = 0

            for i in range(1, 6):
                self.log(f"Capturing image {i}/5... Please hold still.")
                filepath = camera.execute(captures_dir, prefix=f"enroll_temp_{i}_")
                if not filepath:
                    self.log(f"Capture {i} failed: camera error.")
                    break

                self.log("Extracting face embedding...")
                emb = fvm.extract_embedding(filepath)

                # Delete temporary enroll image to preserve privacy
                try:
                    os.remove(filepath)
                except Exception:
                    pass

                if emb is None:
                    self.log(
                        f"Capture {i} failed: No face detected. Please ensure face is centered and well-lit."
                    )
                    break

                embeddings.append(emb)
                success_count += 1
                time.sleep(0.5)

            if success_count == 5:
                self.log("All 5 captures processed successfully!")
                self.log("Serializing and encrypting reference face profile...")
                serialized_embs = []
                for emb in embeddings:
                    serialized_embs.append(serialize_embedding(emb))

                self.enrolled_embeddings = serialized_embs
                self.enabled = True
                self.log(
                    "Face enrollment complete! Face verification is now configured."
                )

                # Rename the skip button to 'Proceed' and change action
                self.after(0, self._show_proceed)
            else:
                self.log(
                    "Enrollment unsuccessful. Please click 'Enroll Face' to try again or click 'Skip' to skip."
                )
                self.after(0, self._restore_buttons)

        threading.Thread(target=run_enroll, daemon=True).start()

    def _restore_buttons(self):
        self.enroll_btn.config(state="normal")
        self.back_btn.config(state="normal")
        self.skip_btn.config(state="normal")

    def _show_proceed(self):
        self.skip_btn.config(
            text="Proceed →", command=self._proceed, state="normal", bg=GREEN
        )
        self.back_btn.config(state="normal")

    def _proceed(self):
        self.controller.show_frame("InstallPage")
        self.controller.frames["InstallPage"].start_install()


class InstallPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ttk.Label(self, text="Installing VigiLo...", style="Header.TLabel").pack(
            pady=(10, 20)
        )

        self.status_var = tk.StringVar(value="Preparing deployment engine...")
        status_label = ttk.Label(
            self, textvariable=self.status_var, font=("Segoe UI", 11)
        )
        status_label.pack(anchor="w", pady=5)

        self.progress = ttk.Progressbar(
            self, orient="horizontal", length=450, mode="determinate"
        )
        self.progress.pack(pady=(0, 20), ipady=5)

        log_frame = ttk.LabelFrame(self, text=" System Log ", padding=5)
        log_frame.pack(fill="both", expand=True, pady=5)

        self.log_text = tk.Text(
            log_frame,
            height=12,
            width=60,
            font=("Consolas", 9),
            state="disabled",
            bg="#1e1e1e",
            fg=GREEN,
            relief="flat",
            highlightthickness=0,
        )
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

    def log(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert("end", "> " + message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
        self.status_var.set(message)
        self.update_idletasks()

    def set_progress(self, val):
        self.progress["value"] = val
        self.update_idletasks()

    def start_install(self):
        threading.Thread(target=self.run_installation, daemon=True).start()

    def run_installation(self):
        engine = InstallEngine()

        # Paths relative to installer execution
        # PyInstaller bundles files in _MEIPASS, so we fetch using helper
        src_exe = get_resource_path("VigiLo.exe")
        if not os.path.exists(src_exe):
            # Development Mode fallback
            src_exe = os.path.join(os.getcwd(), "dist", "VigiLo.exe")

        src_uninstall = get_resource_path("uninstall.exe")
        if not os.path.exists(src_uninstall):
            # Development Mode fallback
            src_uninstall = os.path.join(os.getcwd(), "dist", "uninstall.exe")

        config_data = self.controller.get_config_data()

        def log_cb(msg):
            self.log(msg)

        def progress_cb(val):
            self.set_progress(val)

        success = engine.deploy(
            src_exe=src_exe,
            src_uninstall=src_uninstall,
            telegram_config=config_data,
            progress_callback=progress_cb,
            log_callback=log_cb,
        )

        if success:
            time.sleep(1)
            self.controller.show_frame("SuccessPage")
        else:
            self.log("ERROR: Installation sequence failed. Please check privileges.")
            messagebox.showerror(
                "Setup Failure",
                "VigiLo installation was unsuccessful.\nEnsure you run the installer as Administrator.",
            )


class SuccessPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        footer = ttk.Frame(self)
        footer.pack(side="bottom", fill="x", pady=5)

        tk.Button(
            footer,
            text="Close",
            command=lambda: sys.exit(),
            font=("Segoe UI", 12, "bold"),
            bg="#333333",
            fg="white",
            activebackground="#555555",
            activeforeground="white",
            relief="flat",
            padx=30,
            pady=10,
            cursor="hand2",
        ).pack(side="top", pady=(0, 15))

        ttk.Label(
            footer,
            text="© Copyright All Rights Reserved.",
            font=("Segoe UI", 9, "bold"),
            foreground="#333333",
        ).pack(side="bottom")

        content = ttk.Frame(self)
        content.pack(fill="both", expand=True, padx=20)

        lbl = ttk.Label(
            content,
            text="Installation Complete!",
            font=("Segoe UI", 24, "bold"),
            foreground="#28a745",
        )
        lbl.pack(pady=(5, 0))

        ttk.Label(
            content,
            text="VigiLo Security is now active.",
            font=("Segoe UI", 13),
            foreground="#555555",
        ).pack(pady=(0, 10))

        status_frame = ttk.LabelFrame(content, text=" System Status ", padding=5)
        status_frame.pack(fill="x", pady=4)

        checklist = [
            ("✅", "System Service Scheduled Task", "Active (SYSTEM)"),
            ("✅", "User Polling Commander Task", "Active (USER Logon)"),
            ("✅", "Telegram Connection Status", "Connected & Ready"),
        ]

        for i, (icon, title, status) in enumerate(checklist):
            ttk.Label(status_frame, text=icon, font=("Segoe UI", 14)).grid(
                row=i, column=0, padx=5, pady=2
            )
            ttk.Label(status_frame, text=title, font=("Segoe UI", 12, "bold")).grid(
                row=i, column=1, sticky="w", padx=2
            )
            ttk.Label(
                status_frame, text=status, font=("Segoe UI", 11), foreground="#666666"
            ).grid(row=i, column=2, sticky="w", padx=5)

        steps_frame = ttk.Frame(content)
        steps_frame.pack(fill="x", pady=16)

        ttk.Label(
            steps_frame, text="👉 Next Steps:", font=("Segoe UI", 13, "bold")
        ).pack(anchor="w", pady=(0, 2))

        steps_text = (
            "1. Lock your workstation screen (Win + L).\n"
            "2. Enter a wrong password/PIN to trigger an alert event.\n"
            "3. Confirm that the camera capture is received on Telegram."
        )
        ttk.Label(
            steps_frame, text=steps_text, font=("Segoe UI", 11), justify="left"
        ).pack(anchor="w", padx=10, pady=(0, 6))


if __name__ == "__main__":
    if not is_admin():
        # Force UAC elevation on script run
        from security.privilege import elevate

        elevate()
    app = InstallerApp()
    app.mainloop()
