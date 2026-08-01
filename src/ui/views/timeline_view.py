import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ...core.controllers.container import ServiceContainer

class TimelineView(ttk.Frame):
    def __init__(self, parent, container: ServiceContainer):
        super().__init__(parent)
        self.container = container
        self._build_ui()

    def _build_ui(self):
        top_bar = ttk.Frame(self)
        top_bar.pack(fill="x", padx=15, pady=10)

        lbl_title = ttk.Label(top_bar, text="⏱️ Persistent Incident Timeline", font=("Segoe UI", 12, "bold"))
        lbl_title.pack(side="left")

        btn_export = ttk.Button(top_bar, text="Export JSON", command=self._export_json)
        btn_export.pack(side="right", padx=5)

        btn_report = ttk.Button(top_bar, text="Generate Incident Report", command=self._generate_report)
        btn_report.pack(side="right", padx=5)

        btn_refresh = ttk.Button(top_bar, text="Refresh", command=self.refresh)
        btn_refresh.pack(side="right", padx=5)

        # Treeview table
        columns = ("timestamp", "severity", "type", "description", "hash")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=15)
        
        self.tree.heading("timestamp", text="Timestamp")
        self.tree.heading("severity", text="Severity")
        self.tree.heading("type", text="Event Type")
        self.tree.heading("description", text="Description")
        self.tree.heading("hash", text="SHA256 Integrity Hash")

        self.tree.column("timestamp", width=160)
        self.tree.column("severity", width=80)
        self.tree.column("type", width=140)
        self.tree.column("description", width=260)
        self.tree.column("hash", width=180)

        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 15), pady=10)

        self.refresh()

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        events = self.container.timeline_service.get_timeline(limit=200)
        for ev in events:
            self.tree.insert("", "end", values=(
                ev.timestamp[:19],
                ev.severity,
                ev.event_type,
                ev.description,
                ev.sha256_hash[:16] + "..."
            ))

    def _export_json(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            initialfile="vigilo_timeline_export.json"
        )
        if filepath:
            if self.container.timeline_service.export_json(filepath):
                messagebox.showinfo("Export Successful", f"Timeline exported successfully to:\n{filepath}")
            else:
                messagebox.showerror("Export Failed", "Failed to export timeline JSON.")

    def _generate_report(self):
        report = self.container.report_service.generate_report()
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Reports", "*.pdf"), ("Text Reports", "*.txt")],
            initialfile=f"vigilo_forensic_report_{report.report_id}.pdf"
        )
        if filepath:
            out = self.container.report_service.export_pdf(report, filepath)
            messagebox.showinfo("Report Created", f"Forensic Incident Report generated:\n{out}")
