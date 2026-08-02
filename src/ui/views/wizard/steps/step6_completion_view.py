import tkinter as tk
from tkinter import ttk
from src.ui.viewmodels.recovery_wizard_viewmodel import RecoveryWizardViewModel

class Step6CompletionView(ttk.Frame):
    """Step 6: Completion & Reassuring Next Steps Guide View."""

    def __init__(self, parent, vm: RecoveryWizardViewModel):
        super().__init__(parent, padding=15)
        self.vm = vm

        self._build_ui()

    def _build_ui(self):
        lbl_h = ttk.Label(self, text="🎉 Step 6: Recovery Completed Successfully!", font=("Segoe UI", 12, "bold"))
        lbl_h.pack(anchor="w", pady=(0, 10))

        lbl_desc = ttk.Label(self, text="Your recovery objectives have been executed and your evidence package is securely stored.", font=("Segoe UI", 10), wraplength=550)
        lbl_desc.pack(anchor="w", pady=(0, 15))

        box = ttk.LabelFrame(self, text=" 💡 Recommended Next Actions ", padding=15)
        box.pack(fill="both", expand=True)

        steps = [
            "1. 🔑 Reset your Microsoft Account & local Windows passwords.",
            "2. 🛡️ Keep VigiLo in WATCH MODE for active intruder monitoring.",
            "3. 📂 Save your generated Forensic PDF Report in a safe backup location.",
            "4. 📞 Provide the Forensic PDF Report to law enforcement if your device was stolen."
        ]

        for s in steps:
            l = ttk.Label(box, text=s, font=("Segoe UI", 9, "bold"))
            l.pack(anchor="w", pady=4)
