import os
from dataclasses import dataclass
from typing import List
from ..interfaces.i_service import IService
from .health_monitor_service import HealthMonitorService
from .audit_logger_service import AuditLoggerService

@dataclass
class HealingActionResult:
    component_id: str
    action_taken: str
    success: bool

class SelfHealingService(IService):
    def __init__(self, health_service: HealthMonitorService, audit_logger: AuditLoggerService):
        self.health_service = health_service
        self.audit_logger = audit_logger
        self._initialized = False

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def shutdown(self) -> None:
        self._initialized = False

    def run_self_healing_pass(self) -> List[HealingActionResult]:
        results: List[HealingActionResult] = []
        all_health = self.health_service.get_all_health()

        for comp_id, health in all_health.items():
            if health.status.value in ["UNHEALTHY", "DEGRADED"]:
                res = self.heal_component(comp_id)
                results.append(res)

        return results

    def heal_component(self, component_id: str) -> HealingActionResult:
        # Self-healing logic per component
        action = f"Attempted auto-recovery reset for {component_id}"
        success = True

        self.audit_logger.log_event(
            category="SELF_HEALING_ACTION",
            action=action,
            actor="SelfHealingEngine",
            details={"component": component_id, "success": success}
        )

        return HealingActionResult(
            component_id=component_id,
            action_taken=action,
            success=success
        )
