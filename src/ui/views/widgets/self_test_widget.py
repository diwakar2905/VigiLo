import tkinter as tk
from tkinter import ttk

class SelfTestDiagnosticWidget(ttk.LabelFrame):
    """One-Click System Diagnostics Launcher Widget."""

    def __init__(self, parent, on_run_diagnostics_callback):
        super().__init__(parent, text=" 🩺 Automated Self-Test Diagnostics ", padding=15)
        self.on_run_diagnostics = on_run_diagnostics_callback
        self._build_ui()

    def _build_ui(self):
        top_row = ttk.Frame(self)
        top_row.pack(fill="x")

        self.btn_run = ttk.Button(top_row, text="🔍 Run Full System Diagnostics", command=self._handle_run)
        self.btn_run.pack(side="left")

        self.lbl_overall = ttk.Label(top_row, text="Status: Not Run Yet", font=("Segoe UI", 10, "bold"))
        self.lbl_overall.pack(side="right")

        self.results_frame = ttk.Frame(self)
        self.results_frame.pack(fill="both", expand=True, pady=(10, 0))

    def _handle_run(self):
        self.btn_run.config(state="disabled", text="Running Diagnostics Probes...")
        if self.on_run_diagnostics:
            self.on_run_diagnostics()

    def display_report(self, report: dict):
        self.btn_run.config(state="normal", text="🔍 Run Full System Diagnostics")
        overall = report.get("overall_status", "HEALTHY")
        icon = "✅ PASS" if overall == "HEALTHY" else ("⚠️ WARNING" if overall == "WARNING" else "❌ FAILED")
        self.lbl_overall.config(text=f"Status: {icon}")

        for w in self.results_frame.winfo_children():
            w.destroy()

        for c in report.get("checks", []):
            row = ttk.Frame(self.results_frame)
            row.pack(fill="x", pady=2)

            c_icon = "✅" if c.get("status") == "HEALTHY" else ("⚠️" if c.get("status") == "WARNING" else "❌")
            l_comp = ttk.Label(row, text=f"• {c.get('component')}:", font=("Segoe UI", 9, "bold"), width=25)
            l_comp.pack(side="left")

            l_msg = ttk.Label(row, text=f"{c_icon} {c.get('message')}", font=("Segoe UI", 9))
            l_msg.pack(side="left")
