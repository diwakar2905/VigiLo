import os
import shutil
import tempfile
import pytest
from src.core.repositories.timeline_repository import TimelineRepository
from src.core.repositories.audit_log_repository import AuditLogRepository
from src.core.services.audit_logger_service import AuditLoggerService
from src.core.services.timeline_service import IncidentTimelineService
from src.core.services.report_generator_service import IncidentReportService

class TestTimelineAndReport:
    def setup_method(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_file = os.path.join(self.test_dir, "timeline.db")
        self.audit_file = os.path.join(self.test_dir, "audit.log")
        self.captures_dir = os.path.join(self.test_dir, "captures")
        os.makedirs(self.captures_dir, exist_ok=True)

        self.timeline_repo = TimelineRepository(self.db_file)
        self.audit_repo = AuditLogRepository(self.audit_file)
        self.audit_service = AuditLoggerService(self.audit_repo)
        self.audit_service.initialize()

        self.timeline_service = IncidentTimelineService(self.timeline_repo, self.audit_service)
        self.timeline_service.initialize()

        self.report_service = IncidentReportService(self.timeline_service, self.captures_dir)
        self.report_service.initialize()

    def teardown_method(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_record_and_retrieve_incident(self):
        event = self.timeline_service.record_event("FAILED_LOGIN", "WARNING", "Failed login attempt detected")
        assert event.incident_id.startswith("INC-")
        assert event.sha256_hash is not None

        events = self.timeline_service.get_timeline()
        assert len(events) >= 1
        assert events[0].event_type == "FAILED_LOGIN"

    def test_generate_and_export_report(self):
        self.timeline_service.record_event("STATE_TRANSITION", "INFO", "Switched to WATCH_MODE")
        report = self.report_service.generate_report()
        assert report.report_id.startswith("REP-")
        assert len(report.timeline_events) >= 1

        json_out = os.path.join(self.test_dir, "report.json")
        pdf_out = os.path.join(self.test_dir, "report.pdf")

        exported_json = self.report_service.export_json(report, json_out)
        exported_pdf = self.report_service.export_pdf(report, pdf_out)

        assert os.path.exists(exported_json)
        assert os.path.exists(exported_pdf)
        assert os.path.getsize(exported_pdf) > 0
