import tkinter as tk
from tkinter import ttk

class FluentIncidentDetailDialog(tk.Toplevel):
    """Forensic incident detail modal."""

    def __init__(self, parent, incident_data: dict):
        super().__init__(parent)
        self.title("🚨 Incident Forensic Details")
        self.geometry("520x400")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_ui(incident_data)

    def _build_ui(self, data: dict):
        pad = ttk.Frame(self, padding=20)
        pad.pack(fill="both", expand=True)

        lbl_title = ttk.Label(pad, text=f"Incident: {data.get('event_type', 'INCIDENT')}", font=("Segoe UI", 12, "bold"))
        lbl_title.pack(anchor="w", pady=(0, 10))

        fields = [
            ("Severity", data.get("severity", "CRITICAL")),
            ("Timestamp", data.get("timestamp", "N/A")),
            ("Event ID", data.get("event_id", "N/A")),
            ("SHA-256 Hash", data.get("sha256_hash", "N/A")),
            ("Correlation ID", data.get("correlation_id", "N/A")),
            ("Description", data.get("description", "No details available."))
        ]

        for label, val in fields:
            f_frame = ttk.Frame(pad)
            f_frame.pack(fill="x", pady=3)
            l = ttk.Label(f_frame, text=f"{label}:", font=("Segoe UI", 9, "bold"), width=15)
            l.pack(side="left")
            v = ttk.Label(f_frame, text=str(val), font=("Segoe UI", 9), wraplength=340)
            v.pack(side="left")

        btn_close = ttk.Button(pad, text="Close Details", command=self.destroy)
        btn_close.pack(side="right", pady=(15, 0))
