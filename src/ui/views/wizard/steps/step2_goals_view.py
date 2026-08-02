import tkinter as tk
from tkinter import ttk
from src.ui.viewmodels.recovery_wizard_viewmodel import RecoveryWizardViewModel

class Step2GoalsView(ttk.Frame):
    """Step 2: Plain-Language Recovery Goal Selection View."""

    def __init__(self, parent, vm: RecoveryWizardViewModel):
        super().__init__(parent, padding=15)
        self.vm = vm

        self._build_ui()

    def _build_ui(self):
        lbl_h = ttk.Label(self, text="Step 2: Select Your Recovery Goals", font=("Segoe UI", 12, "bold"))
        lbl_h.pack(anchor="w", pady=(0, 10))

        lbl_desc = ttk.Label(self, text="Choose what actions VigiLo should take to secure your laptop and gather evidence. All actions execute safely in sequence.", font=("Segoe UI", 10), wraplength=550)
        lbl_desc.pack(anchor="w", pady=(0, 15))

        box = ttk.LabelFrame(self, text=" 🎯 Recovery Objectives ", padding=15)
        box.pack(fill="both", expand=True)

        cb1 = ttk.Checkbutton(box, text="🔍 Locate Device (WiFi & IP Triangulation)", command=lambda: self.vm.goal_locate.set(not self.vm.goal_locate.get()))
        cb1.pack(anchor="w", pady=5)
        cb1.state(['selected'])

        cb2 = ttk.Checkbutton(box, text="📷 Collect Intruder Photo & Desktop Screenshot", command=lambda: self.vm.goal_photo.set(not self.vm.goal_photo.get()))
        cb2.pack(anchor="w", pady=5)
        cb2.state(['selected'])

        cb3 = ttk.Checkbutton(box, text="🔒 Lock Workstation Immediately (Prevent Local Access)", command=lambda: self.vm.goal_lock.set(not self.vm.goal_lock.get()))
        cb3.pack(anchor="w", pady=5)
        cb3.state(['selected'])

        cb4 = ttk.Checkbutton(box, text="📄 Generate Digital Forensic Report with SHA-256 Seals", command=lambda: self.vm.goal_report.set(not self.vm.goal_report.get()))
        cb4.pack(anchor="w", pady=5)
        cb4.state(['selected'])
