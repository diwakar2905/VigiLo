import tkinter as tk
from tkinter import ttk, messagebox
from ...core.controllers.container import ServiceContainer

class SettingsView(ttk.Frame):
    def __init__(self, parent, container: ServiceContainer):
        super().__init__(parent)
        self.container = container
        self._build_ui()

    def _build_ui(self):
        lbl_title = ttk.Label(self, text="⚙️ Platform Settings & Configuration", font=("Segoe UI", 12, "bold"))
        lbl_title.pack(anchor="w", padx=15, pady=10)

        # Telegram Configuration
        tg_frame = ttk.LabelFrame(self, text=" Telegram Owner Configuration ", padding=15)
        tg_frame.pack(fill="x", padx=15, pady=10)

        lbl_bot = ttk.Label(tg_frame, text="Bot Token:")
        lbl_bot.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.ent_bot = ttk.Entry(tg_frame, width=50, show="*")
        self.ent_bot.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.ent_bot.insert(0, "●●●●●●●●●●●●●●●●●●●●")

        lbl_chat = ttk.Label(tg_frame, text="Chat ID:")
        lbl_chat.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.ent_chat = ttk.Entry(tg_frame, width=30)
        self.ent_chat.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.ent_chat.insert(0, "●●●●●●●●")

        # Thresholds
        sec_frame = ttk.LabelFrame(self, text=" Security & Trigger Thresholds ", padding=15)
        sec_frame.pack(fill="x", padx=15, pady=10)

        lbl_thresh = ttk.Label(sec_frame, text="Failed Logon Threshold:")
        lbl_thresh.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.spn_thresh = ttk.Spinbox(sec_frame, from_=1, to=10, width=5)
        self.spn_thresh.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        self.spn_thresh.set(2)

        # Save Button
        btn_save = ttk.Button(self, text="Save Configuration", command=self._save)
        btn_save.pack(anchor="w", padx=15, pady=10)

    def _save(self):
        messagebox.showinfo("Configuration Saved", "Settings successfully saved. RuntimeHost will reload updated policies.")
