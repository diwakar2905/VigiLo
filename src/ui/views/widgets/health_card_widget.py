import tkinter as tk
from tkinter import ttk
from ...themes.fluent_theme import FluentThemeManager
from ...services.dashboard_service import ControlCenterSummaryDTO

class HealthCardWidget(ttk.LabelFrame):
    """Device Health Banner Card Widget."""

    def __init__(self, parent):
        super().__init__(parent, text=" 🛡️ Device Protection & Identity ", padding=15)
        self.theme = FluentThemeManager("dark").get_palette()
        self._build_ui()

    def _build_ui(self):
        top_row = ttk.Frame(self)
        top_row.pack(fill="x", expand=True)

        self.lbl_status = ttk.Label(top_row, text="🛡️ PROTECTION STATUS: PROTECTED", font=("Segoe UI", 12, "bold"))
        self.lbl_status.pack(side="left")

        self.lbl_state_badge = ttk.Label(top_row, text="[ WATCH MODE ]", font=("Segoe UI", 10, "bold"))
        self.lbl_state_badge.pack(side="right")

        detail_row = ttk.Frame(self)
        detail_row.pack(fill="x", pady=(10, 0))

        self.lbl_details = ttk.Label(
            detail_row,
            text="Device: N/A  |  ID: VIGI-XXXX  |  Last Heartbeat: 2s ago  |  Runtime: v1.0  |  Config: v3.5.0",
            font=("Segoe UI", 9)
        )
        self.lbl_details.pack(anchor="w")

    def update_summary(self, summary: ControlCenterSummaryDTO):
        status_text = f"🛡️ PROTECTION STATUS: {summary.protection_status}"
        self.lbl_status.config(text=status_text)
        self.lbl_state_badge.config(text=f"[ {summary.device_state} ]")

        details = (
            f"Device: {summary.device_name}  |  ID: {summary.device_id}  |  "
            f"Heartbeat: {summary.last_heartbeat}  |  Runtime: {summary.runtime_version}  |  Config: {summary.config_version}"
        )
        self.lbl_details.config(text=details)
