from typing import Dict
from ..models.health_object import HealthObject, HealthStatus
from ..services.health_monitor_service import HealthMonitorService

class HealthController:
    def __init__(self, service: HealthMonitorService):
        self.service = service

    def update_node_health(self, health_obj: HealthObject) -> None:
        self.service.update_health(health_obj)

    def get_all_nodes(self) -> Dict[str, HealthObject]:
        return self.service.get_all_health()

    def get_system_health(self) -> HealthStatus:
        return self.service.get_aggregate_health()
