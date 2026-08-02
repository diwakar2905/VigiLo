import tkinter as tk
from tkinter import ttk
from src.ui.viewmodels.recovery_wizard_viewmodel import RecoveryWizardViewModel

class Step3ExecutionView(ttk.Frame):
    """Step 3: Action Execution Progress View."""

    def __init__(self, parent, vm: RecoveryWizardViewModel):
        super().__init__(parent, padding=15)
        self.vm = vm

        self._build_ui()
        self._bind_vm()

    def _build_ui(self):
        lbl_h = ttk.Label(self, text="Step 3: Executing Recovery Actions", font=("Segoe UI", 12, "bold"))
        lbl_h.pack(anchor="w", pady=(0, 10))

        lbl_desc = ttk.Label(self, text="Please wait while VigiLo executes your selected recovery objectives...", font=("Segoe UI", 10))
        lbl_desc.pack(anchor="w", pady=(0, 15))

        self.progress_bar = ttk.Progressbar(self, maximum=100)
        self.progress_bar.pack(fill="x", pady=10)

        self.lbl_status = ttk.Label(self, text="Initializing...", font=("Segoe UI", 10, "bold"))
        self.lbl_status.pack(anchor="w", pady=5)

        self.txt_log = tk.Text(self, font=("Consolas", 9), height=8)
        self.txt_log.pack(fill="both", expand=True, pady=10)

    def _bind_vm(self):
        self.vm.progress_percent.subscribe(lambda pct: self.progress_bar.config(value=pct))
        self.vm.progress_status.subscribe(self._on_status_change)

    def _on_status_change(self, msg: str):
        self.lbl_status.config(text=msg)
        self.txt_log.insert("end", f"• {msg}\n")
        self.txt_log.see("end")
