from ..services.diagnostics_engine_service import DiagnosticsEngineService, DiagnosticReport

class DiagnosticsController:
    def __init__(self, service: DiagnosticsEngineService):
        self.service = service

    def run_diagnostics(self) -> DiagnosticReport:
        return self.service.run_full_diagnostics()
