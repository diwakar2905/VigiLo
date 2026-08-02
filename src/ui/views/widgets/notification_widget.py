import tkinter as tk
from tkinter import ttk

class NotificationCenterWidget(ttk.LabelFrame):
    """Notification Center & Egress Health Widget."""

    def __init__(self, parent):
        super().__init__(parent, text=" 📬 Notification Center & Delivery Health ", padding=15)
        self._build_ui()

    def _build_ui(self):
        self.lbl_provider = ttk.Label(self, text="• Current Primary Provider: Telegram (Priority 1)", font=("Segoe UI", 9))
        self.lbl_provider.pack(anchor="w", pady=2)

        self.lbl_status = ttk.Label(self, text="• Provider Health: HEALTHY ✅", font=("Segoe UI", 9))
        self.lbl_status.pack(anchor="w", pady=2)

        self.lbl_queue = ttk.Label(self, text="• Offline Queue Size: 0 pending messages", font=("Segoe UI", 9))
        self.lbl_queue.pack(anchor="w", pady=2)

        self.lbl_last = ttk.Label(self, text="• Last Notification: Delivered (0 retries)", font=("Segoe UI", 9))
        self.lbl_last.pack(anchor="w", pady=2)
