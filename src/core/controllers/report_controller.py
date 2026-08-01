from ..models.incident_report import IncidentReportModel
from ..services.report_generator_service import IncidentReportService

class ReportController:
    def __init__(self, service: IncidentReportService):
        self.service = service

    def create_report(self) -> IncidentReportModel:
        return self.service.generate_report()

    def export_pdf(self, report: IncidentReportModel, filepath: str) -> str:
        return self.service.export_pdf(report, filepath)

    def export_json(self, report: IncidentReportModel, filepath: str) -> str:
        return self.service.export_json(report, filepath)
