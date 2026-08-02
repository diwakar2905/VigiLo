import tkinter as tk
from tkinter import ttk
from typing import List
from ...services.dashboard_service import ServiceHealthStatusDTO

class RuntimeStatusWidget(ttk.LabelFrame):
    """Runtime Managed Services Status Widget."""

    def __init__(self, parent):
        super().__init__(parent, text=" ⚙️ Managed Runtime Services ", padding=15)
        self._items_frame = ttk.Frame(self)
        self._items_frame.pack(fill="both", expand=True)

    def update_services(self, services: List[ServiceHealthStatusDTO]):
        for w in self._items_frame.winfo_children():
            w.destroy()

        for svc in services:
            row = ttk.Frame(self._items_frame)
            row.pack(fill="x", pady=2)

            icon = "✅" if svc.status in ["RUNNING", "READY"] else ("⚠️" if svc.status == "WARNING" else "❌")
            lbl_name = ttk.Label(row, text=f"• {svc.name}", font=("Segoe UI", 9, "bold"), width=22)
            lbl_name.pack(side="left")

            lbl_status = ttk.Label(row, text=f"[{svc.status} {icon}]", font=("Segoe UI", 9))
            lbl_status.pack(side="right")
