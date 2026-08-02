import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any
from ..modals.incident_detail_dialog import FluentIncidentDetailDialog

class RecentIncidentsWidget(ttk.LabelFrame):
    """Recent Incidents List & Forensic Viewer Widget."""

    def __init__(self, parent):
        super().__init__(parent, text=" 🚨 Recent Incident Evidence Log ", padding=15)
        self._list_frame = ttk.Frame(self)
        self._list_frame.pack(fill="both", expand=True)
        self._incidents: List[Dict[str, Any]] = []

    def update_incidents(self, incidents: List[Dict[str, Any]]):
        self._incidents = incidents
        for w in self._list_frame.winfo_children():
            w.destroy()

        if not incidents:
            lbl_empty = ttk.Label(self._list_frame, text="✅ No recent incident evidence detected.", font=("Segoe UI", 9, "italic"))
            lbl_empty.pack(anchor="w", pady=5)
            return

        for idx, inc in enumerate(incidents[:5]):
            row = ttk.Frame(self._list_frame, cursor="hand2")
            row.pack(fill="x", pady=4)

            sev = inc.get("severity", "INFO")
            icon = "🚨" if sev in ["CRITICAL", "HIGH"] else "ℹ️"
            txt = f"{icon} [{inc.get('timestamp', '')[:19]}] {inc.get('event_type', '')}: {inc.get('description', '')}"

            lbl = ttk.Label(row, text=txt, font=("Segoe UI", 9))
            lbl.pack(side="left")

            btn = ttk.Button(row, text="View Forensic Details", command=lambda data=inc: self._open_detail(data))
            btn.pack(side="right")

    def _open_detail(self, data: dict):
        FluentIncidentDetailDialog(self.winfo_toplevel(), data)
