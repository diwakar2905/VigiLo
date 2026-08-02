import os
import json
import tempfile
import shutil
import pytest
from src.core.services.timeline.forensic_timeline_service import ForensicTimelineService, SUPPORTED_EVENT_TYPES
from src.ui.viewmodels.timeline_viewmodel import TimelineViewModel

class TestForensicTimeline:
    def setup_method(self):
        self.test_dir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_supported_event_types_count(self):
        assert len(SUPPORTED_EVENT_TYPES) == 16
        assert "FAILED_LOGIN" in SUPPORTED_EVENT_TYPES
        assert "POLICY_VIOLATION" in SUPPORTED_EVENT_TYPES
        assert "RECOVERY_COMPLETED" in SUPPORTED_EVENT_TYPES

    def test_forensic_timeline_service_search_and_filter(self):
        svc = ForensicTimelineService()
        events = svc.get_all_events()

        # Perform search and filter
        results = svc.search_and_filter(query="", severity="ALL", event_type="ALL")
        assert isinstance(results, list)

        if len(events) > 0:
            e0 = events[0]
            assert e0.sha256_hash != ""
            assert len(e0.sha256_hash) == 64

    def test_bookmark_toggling(self):
        svc = ForensicTimelineService()
        events = svc.get_all_events()
        if len(events) > 0:
            incident_id = events[0].incident_id

            # Toggle bookmark ON
            is_bm = svc.toggle_bookmark(incident_id)
            assert is_bm is True

            # Toggle bookmark OFF
            is_bm = svc.toggle_bookmark(incident_id)
            assert is_bm is False

    def test_timeline_viewmodel_filtering(self):
        vm = TimelineViewModel()
        vm.set_severity_filter("CRITICAL")
        vm.set_search_query("FAILED_LOGIN")

        filtered = vm.filtered_events.get()
        assert isinstance(filtered, list)

    def test_forensic_investigation_export(self):
        svc = ForensicTimelineService()
        events = svc.get_all_events()

        export_path = os.path.join(self.test_dir, "investigation_export.json")
        success = svc.export_investigation(events, export_path)

        assert success is True
        assert os.path.exists(export_path)

        with open(export_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert "investigation_export" in data
