import tkinter as tk
from tkinter import ttk
from typing import List, Dict
from src.core.services.timeline.forensic_timeline_service import ForensicDetailDTO
from .event_card_widget import ForensicEventCardWidget

class TimelineEventTreeGroupWidget(ttk.Frame):
    """Collapsible Date/Hour Event Tree Group Widget."""

    def __init__(self, parent, on_select_cb, on_bookmark_cb):
        super().__init__(parent)
        self.on_select = on_select_cb
        self.on_bookmark = on_bookmark_cb
        self._container_frame = ttk.Frame(self)
        self._container_frame.pack(fill="both", expand=True)

    def update_events(self, events: List[ForensicDetailDTO]):
        for w in self._container_frame.winfo_children():
            w.destroy()

        if not events:
            lbl_empty = ttk.Label(self._container_frame, text="✅ No events match the active search and filter criteria.", font=("Segoe UI", 10, "italic"))
            lbl_empty.pack(anchor="w", pady=15)
            return

        # Group events by Date string YYYY-MM-DD
        groups: Dict[str, List[ForensicDetailDTO]] = {}
        for e in events:
            date_key = e.timestamp[:10] if len(e.timestamp) >= 10 else "Unknown Date"
            if date_key not in groups:
                groups[date_key] = []
            groups[date_key].append(e)

        for date_key, group_events in groups.items():
            lf = ttk.LabelFrame(self._container_frame, text=f" 📅 Intrusion Sequence Group: {date_key} ({len(group_events)} events) ", padding=5)
            lf.pack(fill="x", pady=5)

            for evt_dto in group_events:
                card = ForensicEventCardWidget(lf, evt_dto, self.on_select, self.on_bookmark)
                card.pack(fill="x", pady=2)
