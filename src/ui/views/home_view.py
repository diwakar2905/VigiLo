import tkinter as tk
from tkinter import ttk
import platform
from datetime import datetime
from ...core.models.device_state import DeviceState
from ...core.controllers.container import ServiceContainer

class HomeView(ttk.Frame):
    def __init__(self, parent, container: ServiceContainer, on_wizard_launch=None):
        super().__init__(parent)
        self.container = container
        self.on_wizard_launch = on_wizard_launch
        self._build_ui()

    def _build_ui(self):
        # Header banner
        header = ttk.LabelFrame(self, text=" System Status ", padding=15)
        header.pack(fill="x", padx=15, pady=10)

        self.lbl_device_name = ttk.Label(header, text=f"Device Name: {platform.node()}", font=("Segoe UI", 11, "bold"))
        self.lbl_device_name.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.lbl_device_id = ttk.Label(header, text=f"Device ID: {self.container.report_service.generate_report().device_id}", font=("Segoe UI", 10))
        self.lbl_device_id.grid(row=0, column=1, sticky="w", padx=10, pady=5)

        # State Card
        state_frame = ttk.LabelFrame(self, text=" Device Recovery State ", padding=15)
        state_frame.pack(fill="x", padx=15, pady=10)

        self.lbl_current_state = ttk.Label(state_frame, text="Current Mode: WATCH_MODE", font=("Segoe UI", 12, "bold"))
        self.lbl_current_state.pack(anchor="w", padx=10, pady=5)

        btn_box = ttk.Frame(state_frame)
        btn_box.pack(fill="x", padx=10, pady=5)

        btn_disarm = ttk.Button(btn_box, text="Disarm System", command=lambda: self._set_mode(DeviceState.DISARMED))
        btn_disarm.pack(side="left", padx=5)

        btn_watch = ttk.Button(btn_box, text="Enable Watch Mode", command=lambda: self._set_mode(DeviceState.WATCH_MODE))
        btn_watch.pack(side="left", padx=5)

        btn_lost = ttk.Button(btn_box, text="🚨 Report Device Lost", command=lambda: self._set_mode(DeviceState.LOST_MODE))
        btn_lost.pack(side="left", padx=5)

        if self.on_wizard_launch:
            btn_wiz = ttk.Button(btn_box, text="🧙 Launch Recovery Wizard", command=self.on_wizard_launch)
            btn_wiz.pack(side="right", padx=5)

        # Health & Protection Cards
        grid_frame = ttk.Frame(self)
        grid_frame.pack(fill="both", expand=True, padx=15, pady=10)

        card1 = ttk.LabelFrame(grid_frame, text=" Runtime & Protection ", padding=15)
        card1.pack(side="left", fill="both", expand=True, padx=5)
        
        self.lbl_runtime_status = ttk.Label(card1, text="Runtime Status: ACTIVE (SYSTEM Privileges)", font=("Segoe UI", 10))
        self.lbl_runtime_status.pack(anchor="w", pady=5)

        self.lbl_protection_status = ttk.Label(card1, text="Protection Status: Intruders Watched & Logged", font=("Segoe UI", 10))
        self.lbl_protection_status.pack(anchor="w", pady=5)

        card2 = ttk.LabelFrame(grid_frame, text=" Telemetry & Last Activity ", padding=15)
        card2.pack(side="right", fill="both", expand=True, padx=5)

        self.lbl_last_seen = ttk.Label(card2, text=f"Last Heartbeat: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", font=("Segoe UI", 10))
        self.lbl_last_seen.pack(anchor="w", pady=5)

        self.lbl_aggregate_health = ttk.Label(card2, text="System Health: HEALTHY", font=("Segoe UI", 10, "bold"), foreground="green")
        self.lbl_aggregate_health.pack(anchor="w", pady=5)

        self.refresh()

    def _set_mode(self, mode: DeviceState):
        self.container.device_state_service.transition_to(mode, "Set via Dashboard UI", "DesktopUser")
        self.refresh()

    def refresh(self):
        curr_state = self.container.device_state_service.get_current_state()
        self.lbl_current_state.config(text=f"Current Mode: {curr_state.value}")
        
        agg = self.container.health_service.get_aggregate_health()
        fg_color = "green" if agg.value == "HEALTHY" else ("orange" if agg.value == "DEGRADED" else "red")
        self.lbl_aggregate_health.config(text=f"System Health: {agg.value}", foreground=fg_color)
