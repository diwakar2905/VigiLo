from typing import Callable, List, Dict, Any, Optional
from ..services.dashboard_service import DashboardService, ControlCenterSummaryDTO

class ObservableProperty:
    def __init__(self, initial_value: Any = None):
        self._value = initial_value
        self._listeners: List[Callable[[Any], None]] = []

    def get(self) -> Any:
        return self._value

    def set(self, new_value: Any) -> None:
        if self._value != new_value:
            self._value = new_value
            for listener in self._listeners:
                try:
                    listener(new_value)
                except Exception as e:
                    print(f"[ERROR] ObservableProperty listener failed: {e}")

    def subscribe(self, callback: Callable[[Any], None]) -> None:
        self._listeners.append(callback)

class DashboardViewModel:
    """Master ViewModel powering the Fluent Device Security Control Center UI."""

    def __init__(self, service: Optional[DashboardService] = None):
        self.service = service or DashboardService()
        self.summary = ObservableProperty(self.service.get_summary())
        self.diagnostic_report = ObservableProperty(None)
        self.is_diagnosing = ObservableProperty(False)

    def refresh(self) -> None:
        self.summary.set(self.service.get_summary())

    def run_self_test(self) -> None:
        self.is_diagnosing.set(True)
        report = self.service.run_diagnostics()
        self.diagnostic_report.set(report)
        self.is_diagnosing.set(False)

    def execute_action(self, action_id: str) -> bool:
        res = self.service.execute_quick_action(action_id)
        self.refresh()
        return res
