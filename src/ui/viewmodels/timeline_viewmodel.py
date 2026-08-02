from typing import List, Optional
from src.ui.viewmodels.dashboard_viewmodel import ObservableProperty
from src.core.services.timeline.forensic_timeline_service import ForensicTimelineService, ForensicDetailDTO

class TimelineViewModel:
    """ViewModel for the Forensic Incident Timeline Workbench."""

    def __init__(self, service: Optional[ForensicTimelineService] = None):
        self.service = service or ForensicTimelineService()

        # Filter & Search States
        self.search_query = ObservableProperty("")
        self.selected_severity = ObservableProperty("ALL")
        self.selected_event_type = ObservableProperty("ALL")
        self.bookmarked_only = ObservableProperty(False)

        # Output Event List State
        self.filtered_events = ObservableProperty([])
        self.selected_event_detail = ObservableProperty(None)

        self.refresh()

    def refresh(self) -> None:
        events = self.service.search_and_filter(
            query=self.search_query.get(),
            severity=self.selected_severity.get(),
            event_type=self.selected_event_type.get(),
            bookmarked_only=self.bookmarked_only.get()
        )
        self.filtered_events.set(events)

    def set_search_query(self, query: str) -> None:
        self.search_query.set(query)
        self.refresh()

    def set_severity_filter(self, severity: str) -> None:
        self.selected_severity.set(severity)
        self.refresh()

    def set_event_type_filter(self, event_type: str) -> None:
        self.selected_event_type.set(event_type)
        self.refresh()

    def toggle_bookmarked_only(self) -> None:
        self.bookmarked_only.set(not self.bookmarked_only.get())
        self.refresh()

    def toggle_event_bookmark(self, incident_id: str) -> None:
        self.service.toggle_bookmark(incident_id)
        self.refresh()

    def select_event_for_detail(self, dto: ForensicDetailDTO) -> None:
        self.selected_event_detail.set(dto)

    def export_current_investigation(self, output_path: str) -> bool:
        return self.service.export_investigation(self.filtered_events.get(), output_path)
