import tkinter as tk
from tkinter import ttk
from ...core.controllers.container import ServiceContainer

class ProtectionView(ttk.Frame):
    def __init__(self, parent, container: ServiceContainer):
        super().__init__(parent)
        self.container = container
        self._build_ui()

    def _build_ui(self):
        lbl_title = ttk.Label(self, text="🛡️ VigiLo Protection & Feature Matrix", font=("Segoe UI", 12, "bold"))
        lbl_title.pack(anchor="w", padx=15, pady=10)

        matrix_frame = ttk.LabelFrame(self, text=" Allowed Features by Device Mode ", padding=15)
        matrix_frame.pack(fill="both", expand=True, padx=15, pady=10)

        headers = ["Feature Name", "Disarmed", "Watch Mode", "Lost Mode", "Privacy Guard Status"]
        for c, h in enumerate(headers):
            lbl = ttk.Label(matrix_frame, text=h, font=("Segoe UI", 10, "bold"))
            lbl.grid(row=0, column=c, sticky="w", padx=10, pady=5)

        features = [
            ("Windows Failed Logon Monitor (Event 4625)", "❌ Disabled", "✅ Active", "✅ Active", "No background storage"),
            ("Webcam Intruder Capture", "❌ Disabled", "✅ Active", "✅ Active", "Captures ONLY on wrong PIN"),
            ("Telegram Alert Notification", "❌ Disabled", "✅ Active", "✅ Active", "Encrypted to owner chat"),
            ("Remote Workstation Lock", "❌ Disabled", "❌ Disabled", "✅ Active", "Requires owner authorization"),
            ("Geo & WiFi Triangulation", "❌ Disabled", "❌ Disabled", "✅ Active", "Used for device location"),
            ("Silent Screenshot Evidence", "❌ Disabled", "❌ Disabled", "✅ Active", "Lost Mode recovery only"),
            ("Forensic Report Generation", "✅ Active", "✅ Active", "✅ Active", "SHA-256 tamper evident"),
            ("Microphone / Audio Capture", "❌ Blocked", "❌ Blocked", "❌ Blocked", "PROHIBITED (Privacy Guarantee)")
        ]

        for r, feat in enumerate(features, start=1):
            for c, val in enumerate(feat):
                lbl = ttk.Label(matrix_frame, text=val, font=("Segoe UI", 9))
                lbl.grid(row=r, column=c, sticky="w", padx=10, pady=3)
