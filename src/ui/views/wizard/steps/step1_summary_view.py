import tkinter as tk
from tkinter import ttk
from src.ui.viewmodels.recovery_wizard_viewmodel import RecoveryWizardViewModel

class Step1SummaryView(ttk.Frame):
    """Step 1: Reassuring Incident Summary View."""

    def __init__(self, parent, vm: RecoveryWizardViewModel):
        super().__init__(parent, padding=15)
        self.vm = vm

        self._build_ui()

    def _build_ui(self):
        lbl_h = ttk.Label(self, text="Step 1: Device Status & Incident Summary", font=("Segoe UI", 12, "bold"))
        lbl_h.pack(anchor="w", pady=(0, 10))

        lbl_desc = ttk.Label(self, text="Don't panic. VigiLo is connected to your Windows computer and will guide you step-by-step through securing your device and gathering evidence.", font=("Segoe UI", 10), wraplength=550)
        lbl_desc.pack(anchor="w", pady=(0, 15))

        s = self.vm.summary.get()

        box = ttk.LabelFrame(self, text=" 💻 Device Status Information ", padding=15)
        box.pack(fill="both", expand=True)

        items = [
            ("Device Name", s.device_name),
            ("Device ID", s.device_id),
            ("Last Seen", s.last_seen),
            ("Current State", s.current_state),
            ("Battery Level", f"{s.battery_level}%"),
            ("Network Connection", s.network_state),
            ("Estimated Location", s.location_summary)
        ]

        for label, val in items:
            f = ttk.Frame(box)
            f.pack(fill="x", pady=3)
            l1 = ttk.Label(f, text=f"{label}:", font=("Segoe UI", 9, "bold"), width=20)
            l1.pack(side="left")
            l2 = ttk.Label(f, text=str(val), font=("Segoe UI", 9))
            l2.pack(side="left")
