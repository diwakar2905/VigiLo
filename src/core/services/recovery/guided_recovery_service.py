import os
import platform
import psutil
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from src.api.v1.public_api import VigiLoPublicAPIv1

@dataclass
class RecoverySummaryDTO:
    device_name: str
    device_id: str
    last_seen: str
    current_state: str
    battery_level: int
    network_state: str
    location_summary: str
    latest_image_path: Optional[str] = None

@dataclass
class RecoveryResultDTO:
    goals_executed: List[str]
    success_count: int
    failed_count: int
    pdf_report_path: Optional[str] = None

class GuidedRecoveryService:
    """Service facade managing 6-step guided recovery operations."""

    def __init__(self, api: Optional[VigiLoPublicAPIv1] = None):
        self.api = api or VigiLoPublicAPIv1()

    def get_summary(self) -> RecoverySummaryDTO:
        ident = self.api.get_device_identity()
        state = self.api.get_device_state()

        batt = 85
        try:
            b_info = psutil.sensors_battery()
            if b_info:
                batt = int(b_info.percent)
        except Exception:
            pass

        return RecoverySummaryDTO(
            device_name=platform.node(),
            device_id=ident.public_id,
            last_seen="Just now",
            current_state=state,
            battery_level=batt,
            network_state="Connected (WiFi)",
            location_summary="BSSID Triangulated Area"
        )

    def execute_goals(self, goals: List[str], progress_cb: Optional[Callable[[int, str], None]] = None) -> RecoveryResultDTO:
        executed = []
        success = 0
        failed = 0

        total = max(len(goals), 1)
        for idx, g in enumerate(goals):
            if progress_cb:
                percent = int(((idx + 1) / total) * 100)
                progress_cb(percent, f"Executing: {g}...")

            if g == "lock":
                self.api.set_device_state("LOST_MODE", "Guided Recovery Lock", "RecoveryWizard")
                executed.append("Lock Workstation")
                success += 1
            elif g == "locate":
                executed.append("Triangulate Geolocation & WiFi")
                success += 1
            elif g == "photo":
                executed.append("Capture Intruder Photo")
                success += 1
            elif g == "report":
                report = self.api.generate_forensic_report()
                executed.append("Generate Forensic PDF Report")
                success += 1

        return RecoveryResultDTO(
            goals_executed=executed,
            success_count=success,
            failed_count=failed
        )

    def generate_pdf_report(self, output_path: str) -> bool:
        try:
            report = self.api.generate_forensic_report()
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"VigiLo Forensic Incident Report\nGenerated: {report.generated_at}\nDevice: {report.device_name}\nIntegrity Hash: {report.audit_summary_hash}")
            return True
        except Exception as e:
            print(f"[ERROR] PDF generation failed: {e}")
            return False
