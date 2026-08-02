import os
import tempfile
import shutil
import pytest
from src.core.services.recovery.guided_recovery_service import GuidedRecoveryService
from src.ui.viewmodels.recovery_wizard_viewmodel import RecoveryWizardViewModel

class TestRecoveryWizard:
    def setup_method(self):
        self.test_dir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_guided_recovery_service_summary(self):
        svc = GuidedRecoveryService()
        summary = svc.get_summary()

        assert summary.device_name != ""
        assert summary.device_id.startswith("VIGI-")
        assert summary.battery_level > 0
        assert summary.network_state != ""

    def test_guided_recovery_goal_execution(self):
        svc = GuidedRecoveryService()
        executed_goals = ["locate", "photo", "lock", "report"]

        res = svc.execute_goals(executed_goals)
        assert res.success_count == 4
        assert res.failed_count == 0
        assert len(res.goals_executed) == 4

    def test_wizard_viewmodel_step_navigation(self):
        vm = RecoveryWizardViewModel()
        assert vm.current_step.get() == 1

        # Advance to Step 2
        vm.next_step()
        assert vm.current_step.get() == 2

        # Step back to Step 1
        vm.prev_step()
        assert vm.current_step.get() == 1

        # Execute selected goals in VM
        vm.execute_selected_goals()
        assert vm.current_step.get() == 2  # Advances step after goal execution
        assert vm.execution_result.get() is not None

    def test_pdf_report_generation(self):
        svc = GuidedRecoveryService()
        pdf_path = os.path.join(self.test_dir, "test_recovery_report.pdf")

        success = svc.generate_pdf_report(pdf_path)
        assert success is True
        assert os.path.exists(pdf_path)
