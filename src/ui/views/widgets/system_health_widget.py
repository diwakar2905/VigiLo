import tkinter as tk
from tkinter import ttk
from ...services.dashboard_service import ControlCenterSummaryDTO

class SystemHealthWidget(ttk.LabelFrame):
    """System Telemetry & Hardware Health Widget."""

    def __init__(self, parent):
        super().__init__(parent, text=" 💻 Hardware & OS Telemetry ", padding=15)
        self._build_ui()

    def _build_ui(self):
        self.lbl_cpu = ttk.Label(self, text="• CPU Usage: -- %", font=("Segoe UI", 9))
        self.lbl_cpu.pack(anchor="w", pady=2)

        self.lbl_ram = ttk.Label(self, text="• Memory (RAM): -- MB", font=("Segoe UI", 9))
        self.lbl_ram.pack(anchor="w", pady=2)

        self.lbl_disk = ttk.Label(self, text="• Disk Space (C:): -- GB Free", font=("Segoe UI", 9))
        self.lbl_disk.pack(anchor="w", pady=2)

        self.lbl_os = ttk.Label(self, text="• Operating System: Windows", font=("Segoe UI", 9))
        self.lbl_os.pack(anchor="w", pady=2)

        self.lbl_def = ttk.Label(self, text="• Windows Defender: ACTIVE ✅", font=("Segoe UI", 9))
        self.lbl_def.pack(anchor="w", pady=2)

    def update_telemetry(self, summary: ControlCenterSummaryDTO):
        self.lbl_cpu.config(text=f"• CPU Usage: {summary.cpu_percent:.1f}%")
        self.lbl_ram.config(text=f"• Memory (RAM): {summary.ram_used_mb:.1f} MB")
        self.lbl_disk.config(text=f"• Disk Space (C:): {summary.disk_free_gb:.1f} GB Free")
        self.lbl_os.config(text=f"• Operating System: {summary.os_version}")
        self.lbl_def.config(text=f"• Windows Defender: {summary.defender_status} ✅")
