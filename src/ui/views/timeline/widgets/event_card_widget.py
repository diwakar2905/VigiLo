import tkinter as tk
from tkinter import ttk
from src.core.services.timeline.forensic_timeline_service import ForensicDetailDTO

class ForensicEventCardWidget(ttk.Frame):
    """Forensic Event Card Item Widget."""

    def __init__(self, parent, dto: ForensicDetailDTO, on_select_cb, on_bookmark_cb):
        super().__init__(parent, padding=8, cursor="hand2")
        self.dto = dto
        self.on_select = on_select_cb
        self.on_bookmark = on_bookmark_cb

        self._build_ui()

    def _build_ui(self):
        # Top Row
        top = ttk.Frame(self)
        top.pack(fill="x")

        sev_icon = "🚨" if self.dto.severity in ["CRITICAL", "HIGH"] else "ℹ️"
        lbl_sev = ttk.Label(top, text=f"{sev_icon} [{self.dto.severity}]", font=("Segoe UI", 9, "bold"))
        lbl_sev.pack(side="left")

        lbl_type = ttk.Label(top, text=f" {self.dto.event_type}", font=("Segoe UI", 9, "bold"))
        lbl_type.pack(side="left")

        star_icon = "⭐" if self.dto.bookmarked else "☆"
        btn_bm = ttk.Button(top, text=star_icon, width=3, command=lambda: self.on_bookmark(self.dto.incident_id))
        btn_bm.pack(side="right")

        lbl_time = ttk.Label(top, text=f"{self.dto.timestamp[:19]}  ", font=("Segoe UI", 9))
        lbl_time.pack(side="right")

        # Bottom Row
        bot = ttk.Frame(self)
        bot.pack(fill="x", pady=(4, 0))

        lbl_desc = ttk.Label(bot, text=self.dto.description, font=("Segoe UI", 9), wraplength=500)
        lbl_desc.pack(side="left")

        btn_inspect = ttk.Button(bot, text="Inspect Forensic Evidence", command=lambda: self.on_select(self.dto))
        btn_inspect.pack(side="right")
