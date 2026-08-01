import sys
import os
import tkinter as tk
from tkinter import ttk

# Ensure path
if not getattr(sys, 'frozen', False):
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if root_dir not in sys.path:
        sys.path.append(root_dir)

from src.core.controllers.container import ServiceContainer
from src.ui.views.home_view import HomeView
from src.ui.views.protection_view import ProtectionView
from src.ui.views.timeline_view import TimelineView
from src.ui.views.health_view import HealthView
from src.ui.views.logs_view import LogsView
from src.ui.views.settings_view import SettingsView
from src.ui.views.about_view import AboutView
from src.ui.wizard.recovery_wizard import RecoveryWizardDialog

class VigiLoDashboardApp(tk.Tk):
    def __init__(self, container: ServiceContainer = None):
        super().__init__()
        if container is None:
            container = ServiceContainer.get_instance()
        self.container = container

        self.title("🛡️ VigiLo Privacy-First Windows Device Recovery Platform")
        self.geometry("960x640")
        self.minsize(800, 500)

        self._configure_styles()
        self._build_ui()

    def _configure_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", tabposition="n")
        style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[12, 6])

    def _build_ui(self):
        # Notebook with all 7 requested tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.home_view = HomeView(self.notebook, self.container, on_wizard_launch=self.launch_recovery_wizard)
        self.protection_view = ProtectionView(self.notebook, self.container)
        self.timeline_view = TimelineView(self.notebook, self.container)
        self.health_view = HealthView(self.notebook, self.container)
        self.logs_view = LogsView(self.notebook, self.container)
        self.settings_view = SettingsView(self.notebook, self.container)
        self.about_view = AboutView(self.notebook, self.container)

        self.notebook.add(self.home_view, text=" Home ")
        self.notebook.add(self.protection_view, text=" Protection ")
        self.notebook.add(self.timeline_view, text=" Timeline ")
        self.notebook.add(self.health_view, text=" Health ")
        self.notebook.add(self.logs_view, text=" Logs ")
        self.notebook.add(self.settings_view, text=" Settings ")
        self.notebook.add(self.about_view, text=" About ")

    def launch_recovery_wizard(self):
        dlg = RecoveryWizardDialog(self, self.container)
        dlg.grab_set()

def main():
    app = VigiLoDashboardApp()
    app.mainloop()

if __name__ == "__main__":
    main()
