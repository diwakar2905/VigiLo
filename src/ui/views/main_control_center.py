import tkinter as tk
from tkinter import ttk, messagebox
from ..themes.fluent_theme import FluentThemeManager
from ..viewmodels.dashboard_viewmodel import DashboardViewModel
from .widgets.health_card_widget import HealthCardWidget
from .widgets.runtime_status_widget import RuntimeStatusWidget
from .widgets.system_health_widget import SystemHealthWidget
from .widgets.quick_actions_widget import QuickActionsRecoveryWidget
from .widgets.self_test_widget import SelfTestDiagnosticWidget
from .widgets.incident_list_widget import RecentIncidentsWidget
from .widgets.notification_widget import NotificationCenterWidget

class DeviceControlCenterApp(tk.Tk):
    """Commercial-Grade VigiLo Device Security Control Center (Fluent MVVM Architecture)."""

    def __init__(self, vm: DashboardViewModel = None):
        super().__init__()
        self.vm = vm or DashboardViewModel()
        self.theme = FluentThemeManager("dark").get_palette()

        self.title("🛡️ VigiLo Device Security Control Center")
        self.geometry("980x680")
        self.minsize(850, 600)
        self.configure(bg=self.theme.bg_canvas)

        self._build_ui()
        self._bind_viewmodel()

    def _build_ui(self):
        # 1. Header Bar
        header = ttk.Frame(self, padding=(20, 15))
        header.pack(fill="x")

        lbl_logo = ttk.Label(header, text="🛡️ VigiLo Control Center", font=("Segoe UI", 16, "bold"))
        lbl_logo.pack(side="left")

        state_btn_frame = ttk.Frame(header)
        state_btn_frame.pack(side="right")

        btn_disarm = ttk.Button(state_btn_frame, text="Disarm", command=lambda: self._set_state("DISARMED"))
        btn_disarm.pack(side="left", padx=2)

        btn_watch = ttk.Button(state_btn_frame, text="Watch Mode", command=lambda: self._set_state("WATCH_MODE"))
        btn_watch.pack(side="left", padx=2)

        btn_lost = ttk.Button(state_btn_frame, text="Lost Mode", command=lambda: self._set_state("LOST_MODE"))
        btn_lost.pack(side="left", padx=2)

        # 2. Device Health Banner Card
        self.health_card = HealthCardWidget(self)
        self.health_card.pack(fill="x", padx=20, pady=(0, 10))

        # 3. Tabbed Container Shell
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # Tab 1: Control Center Grid
        tab_home = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab_home, text="  🏠 Control Center  ")

        grid = ttk.Frame(tab_home)
        grid.pack(fill="both", expand=True)
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        self.runtime_widget = RuntimeStatusWidget(grid)
        self.runtime_widget.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.system_widget = SystemHealthWidget(grid)
        self.system_widget.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.incidents_widget = RecentIncidentsWidget(grid)
        self.incidents_widget.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.actions_widget = QuickActionsRecoveryWidget(grid, on_action_callback=self._handle_quick_action)
        self.actions_widget.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        # Tab 2: Forensic Timeline Workbench
        tab_timeline = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(tab_timeline, text="  📜 Forensic Timeline Workbench  ")

        from src.ui.views.timeline.forensic_workbench_view import ForensicTimelineWorkbenchView
        self.timeline_workbench = ForensicTimelineWorkbenchView(tab_timeline)
        self.timeline_workbench.pack(fill="both", expand=True)

        # Tab 3: Diagnostics & Self-Test
        tab_diag = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab_diag, text="  🩺 Self-Test Diagnostics  ")

        self.self_test_widget = SelfTestDiagnosticWidget(tab_diag, on_run_diagnostics_callback=self._handle_run_diagnostics)
        self.self_test_widget.pack(fill="both", expand=True)

        # Tab 4: Notification Center
        tab_notif = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab_notif, text="  📬 Notification Center  ")

        self.notif_widget = NotificationCenterWidget(tab_notif)
        self.notif_widget.pack(fill="both", expand=True)

    def _bind_viewmodel(self):
        self.vm.summary.subscribe(self._on_summary_updated)
        self.vm.diagnostic_report.subscribe(self._on_diagnostics_updated)
        self._on_summary_updated(self.vm.summary.get())

    def _on_summary_updated(self, summary):
        if not summary:
            return
        self.health_card.update_summary(summary)
        self.runtime_widget.update_services(summary.services)
        self.system_widget.update_telemetry(summary)
        
        # Load timeline events
        events = [e.to_dict() for e in self.vm.service.api.get_timeline_events(limit=5)]
        self.incidents_widget.update_incidents(events)

    def _on_diagnostics_updated(self, report):
        if report:
            self.self_test_widget.display_report(report)

    def _set_state(self, target_state: str):
        self.vm.service.api.set_device_state(target_state, "User Control Center Button", "User")
        self.vm.refresh()

    def _handle_quick_action(self, action_id: str):
        res = self.vm.execute_action(action_id)
        if res:
            messagebox.showinfo("Quick Action Execution", f"Action '{action_id}' executed successfully.")

    def _handle_run_diagnostics(self):
        self.vm.run_self_test()
