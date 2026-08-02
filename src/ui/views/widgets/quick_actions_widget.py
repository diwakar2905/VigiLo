import tkinter as tk
from tkinter import ttk, messagebox
from ..modals.confirmation_dialog import FluentConfirmationDialog

class QuickActionsRecoveryWidget(ttk.LabelFrame):
    """Quick Recovery Actions Panel Widget."""

    def __init__(self, parent, on_action_callback):
        super().__init__(parent, text=" ⚡ Quick Recovery Actions ", padding=15)
        self.on_action = on_action_callback
        self._build_ui()

    def _build_ui(self):
        grid = ttk.Frame(self)
        grid.pack(fill="both", expand=True)

        btn_lock = ttk.Button(grid, text="🔒 Lock Workstation", command=self._confirm_lock)
        btn_lock.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        btn_photo = ttk.Button(grid, text="📷 Capture Photo", command=lambda: self._execute("capture"))
        btn_photo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        btn_screen = ttk.Button(grid, text="📸 Desktop Screenshot", command=lambda: self._execute("screenshot"))
        btn_screen.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        btn_report = ttk.Button(grid, text="📊 Generate PDF Report", command=lambda: self._execute("report"))
        btn_report.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

    def _confirm_lock(self):
        FluentConfirmationDialog(
            self.winfo_toplevel(),
            title="Lock Workstation Confirmation",
            message="Are you sure you want to trigger an immediate Windows Workstation Lock? Active user session will be locked.",
            on_confirm_callback=lambda: self._execute("lock")
        )

    def _execute(self, action_id: str):
        if self.on_action:
            self.on_action(action_id)
