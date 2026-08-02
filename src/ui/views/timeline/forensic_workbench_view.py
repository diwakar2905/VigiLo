import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from src.ui.viewmodels.timeline_viewmodel import TimelineViewModel
from .widgets.filter_search_widget import TimelineFilterSearchWidget
from .widgets.event_tree_group_widget import TimelineEventTreeGroupWidget
from .modals.evidence_detail_dialog import ForensicEvidenceDetailModal

class ForensicTimelineWorkbenchView(ttk.Frame):
    """Forensic Incident Timeline & Investigation Workbench View."""

    def __init__(self, parent, vm: TimelineViewModel = None):
        super().__init__(parent)
        self.vm = vm or TimelineViewModel()

        self._build_ui()
        self._bind_viewmodel()

    def _build_ui(self):
        # 1. Top Filter & Search Controls Bar
        self.filter_bar = TimelineFilterSearchWidget(
            self,
            on_search_cb=self.vm.set_search_query,
            on_severity_cb=self.vm.set_severity_filter,
            on_event_type_cb=self.vm.set_event_type_filter,
            on_bookmark_toggle_cb=self.vm.toggle_bookmarked_only,
            on_export_cb=self._handle_export
        )
        self.filter_bar.pack(fill="x")

        # 2. Event Tree Group View
        self.tree_widget = TimelineEventTreeGroupWidget(
            self,
            on_select_cb=self._on_event_selected,
            on_bookmark_cb=self.vm.toggle_event_bookmark
        )
        self.tree_widget.pack(fill="both", expand=True, padx=10, pady=5)

    def _bind_viewmodel(self):
        self.vm.filtered_events.subscribe(self._on_events_updated)
        self.vm.selected_event_detail.subscribe(self._on_detail_selected)
        self._on_events_updated(self.vm.filtered_events.get())

    def _on_events_updated(self, events):
        self.tree_widget.update_events(events)

    def _on_event_selected(self, dto):
        self.vm.select_event_for_detail(dto)

    def _on_detail_selected(self, dto):
        if dto:
            ForensicEvidenceDetailModal(self.winfo_toplevel(), dto)

    def _handle_export(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            title="Export Signed Forensic Investigation Log"
        )
        if file_path:
            success = self.vm.export_current_investigation(file_path)
            if success:
                messagebox.showinfo("Forensic Export", f"Investigation log exported successfully to:\n{file_path}")
            else:
                messagebox.showerror("Forensic Export", "Failed to export investigation log.")
