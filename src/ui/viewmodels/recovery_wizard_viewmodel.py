from typing import List, Optional
from src.ui.viewmodels.dashboard_viewmodel import ObservableProperty
from src.core.services.recovery.guided_recovery_service import GuidedRecoveryService, RecoverySummaryDTO, RecoveryResultDTO

class RecoveryWizardViewModel:
    """ViewModel managing the 6-step Guided Recovery Wizard workflow."""

    def __init__(self, service: Optional[GuidedRecoveryService] = None):
        self.service = service or GuidedRecoveryService()

        self.current_step = ObservableProperty(1)  # Steps 1 to 6
        self.summary = ObservableProperty(self.service.get_summary())
        
        # Goals selection state (Step 2)
        self.goal_locate = ObservableProperty(True)
        self.goal_photo = ObservableProperty(True)
        self.goal_lock = ObservableProperty(True)
        self.goal_report = ObservableProperty(True)

        # Progress state (Step 3)
        self.progress_percent = ObservableProperty(0)
        self.progress_status = ObservableProperty("Initializing...")
        self.execution_result = ObservableProperty(None)

        # PDF Report State (Step 5)
        self.pdf_generated_path = ObservableProperty(None)

    def next_step(self) -> None:
        c = self.current_step.get()
        if c < 6:
            self.current_step.set(c + 1)

    def prev_step(self) -> None:
        c = self.current_step.get()
        if c > 1:
            self.current_step.set(c - 1)

    def execute_selected_goals(self) -> None:
        goals = []
        if self.goal_locate.get(): goals.append("locate")
        if self.goal_photo.get(): goals.append("photo")
        if self.goal_lock.get(): goals.append("lock")
        if self.goal_report.get(): goals.append("report")

        def _on_progress(pct, msg):
            self.progress_percent.set(pct)
            self.progress_status.set(msg)

        res = self.service.execute_goals(goals, progress_cb=_on_progress)
        self.execution_result.set(res)
        self.next_step()

    def generate_pdf_report(self, output_path: str) -> bool:
        success = self.service.generate_pdf_report(output_path)
        if success:
            self.pdf_generated_path.set(output_path)
        return success
