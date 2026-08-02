import tkinter as tk
from tkinter import ttk
from src.core.services.timeline.forensic_timeline_service import ForensicDetailDTO

class ForensicEvidenceDetailModal(tk.Toplevel):
    """Multi-Tab Forensic Evidence Inspector Modal."""

    def __init__(self, parent, dto: ForensicDetailDTO):
        super().__init__(parent)
        self.dto = dto

        self.title(f"🔍 Forensic Investigation Inspector — Incident {dto.incident_id}")
        self.geometry("640x480")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        # Header Bar
        header = ttk.Frame(self, padding=15)
        header.pack(fill="x")

        sev_icon = "🚨" if self.dto.severity in ["CRITICAL", "HIGH"] else "ℹ️"
        lbl_title = ttk.Label(header, text=f"{sev_icon} [{self.dto.severity}] {self.dto.event_type}", font=("Segoe UI", 12, "bold"))
        lbl_title.pack(side="left")

        lbl_id = ttk.Label(header, text=f"ID: {self.dto.incident_id}", font=("Segoe UI", 9))
        lbl_id.pack(side="right")

        # Notebook Tabs
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Tab 1: Overview
        tab_overview = ttk.Frame(notebook, padding=15)
        notebook.add(tab_overview, text=" 📋 Overview ")

        fields = [
            ("Timestamp", self.dto.timestamp),
            ("Device State", self.dto.device_state),
            ("User Session", self.dto.user_session),
            ("Trigger Source", self.dto.trigger_source),
            ("Correlation ID", self.dto.correlation_id),
            ("Description", self.dto.description)
        ]

        for label, val in fields:
            f_frame = ttk.Frame(tab_overview)
            f_frame.pack(fill="x", pady=4)
            l = ttk.Label(f_frame, text=f"{label}:", font=("Segoe UI", 9, "bold"), width=15)
            l.pack(side="left")
            v = ttk.Label(f_frame, text=str(val), font=("Segoe UI", 9), wraplength=420)
            v.pack(side="left")

        # Tab 2: Evidence & Media
        tab_media = ttk.Frame(notebook, padding=15)
        notebook.add(tab_media, text=" 📷 Media Evidence ")

        l_media = ttk.Label(tab_media, text=f"Media File Path: {self.dto.media_path or 'No photo asset linked'}", font=("Segoe UI", 9))
        l_media.pack(anchor="w", pady=5)

        l_preview = ttk.Label(tab_media, text="[ Media Preview Placeholder / Forensic Capture Available ]", font=("Segoe UI", 10, "italic"))
        l_preview.pack(pady=30)

        # Tab 3: Cryptographic Hashes
        tab_hashes = ttk.Frame(notebook, padding=15)
        notebook.add(tab_hashes, text=" 🔒 Cryptographic Hashes ")

        l_h_status = ttk.Label(tab_hashes, text=f"Integrity Status: {self.dto.evidence_status} ✅", font=("Segoe UI", 10, "bold"))
        l_h_status.pack(anchor="w", pady=(0, 10))

        l_sha = ttk.Label(tab_hashes, text=f"SHA-256 Digest:\n{self.dto.sha256_hash}", font=("Segoe UI", 9, "bold"), wraplength=550)
        l_sha.pack(anchor="w", pady=5)

        # Tab 4: Raw Audit Logs
        tab_logs = ttk.Frame(notebook, padding=15)
        notebook.add(tab_logs, text=" 📜 Raw Audit Logs ")

        txt_logs = tk.Text(tab_logs, font=("Consolas", 8), height=12)
        txt_logs.pack(fill="both", expand=True)
        for log_line in self.dto.raw_logs:
            txt_logs.insert("end", log_line + "\n")
        txt_logs.config(state="disabled")

        # Footer Close Button
        btn_close = ttk.Button(self, text="Close Inspector", command=self.destroy)
        btn_close.pack(side="right", padx=15, pady=(0, 15))
