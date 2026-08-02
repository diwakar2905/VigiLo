import tkinter as tk
from tkinter import ttk
from ...themes.fluent_theme import FluentThemeManager

class FluentConfirmationDialog(tk.Toplevel):
    """Fluent confirmation modal for dangerous recovery actions."""

    def __init__(self, parent, title: str, message: str, on_confirm_callback):
        super().__init__(parent)
        self.title(title)
        self.geometry("450x220")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.theme = FluentThemeManager("dark").get_palette()
        self.configure(bg=self.theme.bg_canvas)
        self.on_confirm = on_confirm_callback

        self._build_ui(title, message)

    def _build_ui(self, title: str, message: str):
        pad = ttk.Frame(self, padding=20)
        pad.pack(fill="both", expand=True)

        lbl_icon = ttk.Label(pad, text="⚠️", font=("Segoe UI", 24))
        lbl_icon.pack(anchor="w")

        lbl_title = ttk.Label(pad, text=title, font=("Segoe UI", 12, "bold"))
        lbl_title.pack(anchor="w", pady=(5, 5))

        lbl_msg = ttk.Label(pad, text=message, font=("Segoe UI", 10), wraplength=400)
        lbl_msg.pack(anchor="w", pady=(0, 15))

        btn_frame = ttk.Frame(pad)
        btn_frame.pack(fill="x", side="bottom")

        btn_confirm = ttk.Button(btn_frame, text="Confirm Action", command=self._handle_confirm)
        btn_confirm.pack(side="right", padx=5)

        btn_cancel = ttk.Button(btn_frame, text="Cancel", command=self.destroy)
        btn_cancel.pack(side="right")

    def _handle_confirm(self):
        self.destroy()
        if self.on_confirm:
            self.on_confirm()
