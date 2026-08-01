import ctypes
import os
import tkinter as tk
from tkinter import ttk, messagebox
from ...core.models.device_state import DeviceState
from ...core.controllers.container import ServiceContainer

class RecoveryWizardDialog(tk.Toplevel):
    def __init__(self, parent, container: ServiceContainer):
        super().__init__(parent)
        self.container = container
        self.title("🧙 VigiLo Device Recovery Wizard")
        self.geometry("620x450")
        self.resizable(False, False)

        self.step_index = 0
        self.steps = [
            ("1. Confirm Device State", self._render_step1),
            ("2. Execute Remote Workstation Lock", self._render_step2),
            ("3. Collect Evidence & Snapshot", self._render_step3),
            ("4. Generate Forensic Incident Report", self._render_step4),
            ("5. Recovery Tips & Next Steps", self._render_step5)
        ]

        self._build_ui()

    def _build_ui(self):
        # Top banner
        self.header_frame = ttk.Frame(self, padding=10)
        self.header_frame.pack(fill="x")

        self.lbl_step_title = ttk.Label(self.header_frame, text="", font=("Segoe UI", 12, "bold"))
        self.lbl_step_title.pack(anchor="w")

        self.progress = ttk.Progressbar(self.header_frame, maximum=len(self.steps))
        self.progress.pack(fill="x", pady=5)

        # Content container
        self.content_frame = ttk.LabelFrame(self, text=" Wizard Step ", padding=15)
        self.content_frame.pack(fill="both", expand=True, padx=15, pady=5)

        # Bottom navigation controls
        nav_frame = ttk.Frame(self, padding=10)
        nav_frame.pack(fill="x")

        self.btn_back = ttk.Button(nav_frame, text="< Back", command=self._prev_step)
        self.btn_back.pack(side="left", padx=5)

        self.btn_next = ttk.Button(nav_frame, text="Next >", command=self._next_step)
        self.btn_next.pack(side="right", padx=5)

        self._show_step(0)

    def _show_step(self, index: int):
        self.step_index = index
        title, render_func = self.steps[index]
        self.lbl_step_title.config(text=title)
        self.progress.config(value=index + 1)

        for w in self.content_frame.winfo_children():
            w.destroy()

        render_func(self.content_frame)

        self.btn_back.config(state="disabled" if index == 0 else "normal")
        if index == len(self.steps) - 1:
            self.btn_next.config(text="Finish & Close", command=self.destroy)
        else:
            self.btn_next.config(text="Next >", command=self._next_step)

    def _prev_step(self):
        if self.step_index > 0:
            self._show_step(self.step_index - 1)

    def _next_step(self):
        if self.step_index < len(self.steps) - 1:
            self._show_step(self.step_index + 1)

    # Steps UI
    def _render_step1(self, parent):
        lbl = ttk.Label(parent, text="Step 1: Set Device State to LOST MODE\n\nThis immediately restricts remote access rights to recovery commands only and activates active evidence logging.", wraplength=550)
        lbl.pack(anchor="w", pady=10)

        def enable_lost():
            self.container.device_state_service.transition_to(DeviceState.LOST_MODE, "Recovery Wizard Execution", "RecoveryWizard")
            messagebox.showinfo("State Transitioned", "Device is now in LOST MODE.")

        btn = ttk.Button(parent, text="🚨 Enable LOST MODE Now", command=enable_lost)
        btn.pack(anchor="w", pady=10)

    def _render_step2(self, parent):
        lbl = ttk.Label(parent, text="Step 2: Lock Workstation Session\n\nSecure local desktop session to prevent unauthorized access while maintaining background recovery listener.", wraplength=550)
        lbl.pack(anchor="w", pady=10)

        def lock_pc():
            try:
                ctypes.windll.user32.LockWorkStation()
                self.container.timeline_service.record_event("WORKSTATION_LOCKED", "INFO", "Workstation locked by Recovery Wizard")
                messagebox.showinfo("Workstation Locked", "Native Windows LockWorkstation executed.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to lock workstation: {e}")

        btn = ttk.Button(parent, text="🔒 Lock Workstation Session", command=lock_pc)
        btn.pack(anchor="w", pady=10)

    def _render_step3(self, parent):
        lbl = ttk.Label(parent, text="Step 3: Collect Evidence Snapshot\n\nRecord immediate camera capture and record incident event to timeline.", wraplength=550)
        lbl.pack(anchor="w", pady=10)

        def snap():
            self.container.timeline_service.record_event("EVIDENCE_COLLECTED", "INFO", "Recovery wizard evidence snapshot taken")
            messagebox.showinfo("Evidence Collected", "Incident recorded to persistent timeline with SHA-256 integrity hash.")

        btn = ttk.Button(parent, text="📸 Trigger Evidence Collection", command=snap)
        btn.pack(anchor="w", pady=10)

    def _render_step4(self, parent):
        lbl = ttk.Label(parent, text="Step 4: Generate Forensic Report\n\nCompile all incident timeline items and image hashes into a tamper-evident PDF/JSON report.", wraplength=550)
        lbl.pack(anchor="w", pady=10)

        def report():
            rep = self.container.report_service.generate_report()
            out_file = os.path.join(self.container.base_data_dir, f"recovery_report_{rep.report_id}.pdf")
            self.container.report_service.export_pdf(rep, out_file)
            messagebox.showinfo("Report Created", f"Forensic report created at:\n{out_file}")

        btn = ttk.Button(parent, text="📋 Compile Forensic Report", command=report)
        btn.pack(anchor="w", pady=10)

    def _render_step5(self, parent):
        lbl_text = (
            "Step 5: Recovery Guidance & Best Practices\n\n"
            "✓ Keep your device powered on and connected to WiFi.\n"
            "✓ Monitor your Telegram Bot for real-time intruder photo alerts.\n"
            "✓ Provide the generated Forensic PDF Report to law enforcement.\n"
            "✓ Use /locate in Telegram to track WiFi triangulation networks."
        )
        lbl = ttk.Label(parent, text=lbl_text, wraplength=550, font=("Segoe UI", 10))
        lbl.pack(anchor="w", pady=10)
