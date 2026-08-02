import tkinter as tk
from tkinter import ttk
from src.core.services.timeline.forensic_timeline_service import SUPPORTED_EVENT_TYPES

class TimelineFilterSearchWidget(ttk.Frame):
    """Full-Text Search & Multi-Filter Control Bar for Forensic Workbench."""

    def __init__(self, parent, on_search_cb, on_severity_cb, on_event_type_cb, on_bookmark_toggle_cb, on_export_cb):
        super().__init__(parent, padding=10)
        self.on_search = on_search_cb
        self.on_severity = on_severity_cb
        self.on_event_type = on_event_type_cb
        self.on_bookmark_toggle = on_bookmark_toggle_cb
        self.on_export = on_export_cb

        self._build_ui()

    def _build_ui(self):
        # Top Search Row
        row1 = ttk.Frame(self)
        row1.pack(fill="x", pady=(0, 5))

        lbl_s = ttk.Label(row1, text="🔍 Search Investigation Log:", font=("Segoe UI", 9, "bold"))
        lbl_s.pack(side="left", padx=(0, 5))

        self.ent_search = ttk.Entry(row1, font=("Segoe UI", 9))
        self.ent_search.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.ent_search.bind("<KeyRelease>", lambda e: self.on_search(self.ent_search.get()))

        btn_export = ttk.Button(row1, text="💾 Export Signed PDF/JSON", command=self.on_export)
        btn_export.pack(side="right")

        # Bottom Filter Row
        row2 = ttk.Frame(self)
        row2.pack(fill="x")

        # Severity Combobox
        lbl_sev = ttk.Label(row2, text="Severity:", font=("Segoe UI", 9))
        lbl_sev.pack(side="left", padx=(0, 2))

        self.cbo_sev = ttk.Combobox(row2, values=["ALL", "CRITICAL", "HIGH", "WARNING", "INFO"], state="readonly", width=12)
        self.cbo_sev.set("ALL")
        self.cbo_sev.pack(side="left", padx=(0, 10))
        self.cbo_sev.bind("<<ComboboxSelected>>", lambda e: self.on_severity(self.cbo_sev.get()))

        # Event Type Combobox
        lbl_type = ttk.Label(row2, text="Event Category:", font=("Segoe UI", 9))
        lbl_type.pack(side="left", padx=(0, 2))

        type_vals = ["ALL"] + SUPPORTED_EVENT_TYPES
        self.cbo_type = ttk.Combobox(row2, values=type_vals, state="readonly", width=22)
        self.cbo_type.set("ALL")
        self.cbo_type.pack(side="left", padx=(0, 10))
        self.cbo_type.bind("<<ComboboxSelected>>", lambda e: self.on_event_type(self.cbo_type.get()))

        # Bookmark Toggle Button
        self.btn_bm = ttk.Checkbutton(row2, text="⭐ Bookmarked Only", command=self.on_bookmark_toggle_cb)
        self.btn_bm.pack(side="left")
