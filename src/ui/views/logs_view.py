import os
import tkinter as tk
from tkinter import ttk
from ...core.controllers.container import ServiceContainer

class LogsView(ttk.Frame):
    def __init__(self, parent, container: ServiceContainer):
        super().__init__(parent)
        self.container = container
        self._build_ui()

    def _build_ui(self):
        top_bar = ttk.Frame(self)
        top_bar.pack(fill="x", padx=15, pady=10)

        lbl_title = ttk.Label(top_bar, text="📜 Audit Log Viewer", font=("Segoe UI", 12, "bold"))
        lbl_title.pack(side="left")

        btn_refresh = ttk.Button(top_bar, text="Refresh Logs", command=self.refresh)
        btn_refresh.pack(side="right")

        self.txt_logs = tk.Text(self, wrap="none", font=("Consolas", 9))
        scrollbar_y = ttk.Scrollbar(self, orient="vertical", command=self.txt_logs.yview)
        scrollbar_x = ttk.Scrollbar(self, orient="horizontal", command=self.txt_logs.xview)
        self.txt_logs.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        self.txt_logs.pack(side="left", fill="both", expand=True, padx=(15, 0), pady=10)
        scrollbar_y.pack(side="right", fill="y", padx=(0, 15), pady=10)
        scrollbar_x.pack(side="bottom", fill="x", padx=15)

        self.refresh()

    def refresh(self):
        self.txt_logs.delete("1.0", tk.END)
        log_path = os.path.join(self.container.base_data_dir, "audit.log")
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for line in lines[-200:]:  # Last 200 log entries
                        self.txt_logs.insert(tk.END, line)
            except Exception as e:
                self.txt_logs.insert(tk.END, f"[ERROR] Failed to read audit log: {e}")
        else:
            self.txt_logs.insert(tk.END, "[INFO] Audit log file initialized.")
