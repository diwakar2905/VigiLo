import os
import json
import hashlib
import uuid
import platform
from datetime import datetime
from typing import List, Dict

from ..interfaces.i_service import IService
from ..models.incident_event import IncidentEvent
from ..models.incident_report import IncidentReportModel
from .timeline_service import IncidentTimelineService

class IncidentReportService(IService):
    def __init__(self, timeline_service: IncidentTimelineService, captures_dir: str):
        self.timeline_service = timeline_service
        self.captures_dir = captures_dir
        self._initialized = False

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def shutdown(self) -> None:
        self._initialized = False

    def generate_report(self) -> IncidentReportModel:
        events = self.timeline_service.get_timeline(limit=100)
        image_hashes = self._collect_image_hashes()

        report = IncidentReportModel(
            report_id=f"REP-{uuid.uuid4().hex[:8].upper()}",
            device_name=platform.node(),
            device_id=hashlib.sha256(platform.node().encode('utf-8')).hexdigest()[:16].upper(),
            os_version=f"{platform.system()} {platform.release()} ({platform.version()})",
            generated_at=datetime.utcnow().isoformat(),
            timeline_events=events,
            image_hashes=image_hashes
        )
        return report

    def export_json(self, report: IncidentReportModel, output_path: str) -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report.to_dict(), f, indent=2)
        return output_path

    def export_pdf(self, report: IncidentReportModel, output_path: str) -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # Native lightweight text-formatted forensic report generator (PDF/Text export)
        # Ensures robust generation without heavy binary external dependencies
        content = []
        content.append("================================================================================")
        content.append(f"                    VIGILO INCIDENT FORENSIC RECOVERY REPORT")
        content.append("================================================================================")
        content.append(f"Report ID:         {report.report_id}")
        content.append(f"Generated At:      {report.generated_at} UTC")
        content.append(f"Device Name:       {report.device_name}")
        content.append(f"Device ID:         {report.device_id}")
        content.append(f"OS Version:        {report.os_version}")
        content.append(f"Audit Summary Hash:{report.audit_summary_hash}")
        content.append("================================================================================")
        content.append("\n[INCIDENT TIMELINE EVENTS]")
        content.append("--------------------------------------------------------------------------------")
        for ev in report.timeline_events:
            content.append(f"[{ev.timestamp}] [{ev.severity}] {ev.event_type} - {ev.description}")
            content.append(f"  ID: {ev.incident_id} | Hash: {ev.sha256_hash}")
            if ev.metadata:
                content.append(f"  Metadata: {json.dumps(ev.metadata)}")
            content.append("")
        
        content.append("--------------------------------------------------------------------------------")
        content.append("[CRYPTOGRAPHIC EVIDENCE INTEGRITY HASHES (SHA-256)]")
        content.append("--------------------------------------------------------------------------------")
        for img_name, img_hash in report.image_hashes.items():
            content.append(f"{img_name}: {img_hash}")
        content.append("================================================================================")
        
        pdf_path = output_path if output_path.endswith('.pdf') or output_path.endswith('.txt') else output_path + '.pdf'
        with open(pdf_path, "w", encoding="utf-8") as f:
            f.write("\n".join(content))
        return pdf_path

    def _collect_image_hashes(self) -> Dict[str, str]:
        hashes = {}
        if os.path.exists(self.captures_dir):
            for fname in os.listdir(self.captures_dir):
                if fname.endswith((".jpg", ".png", ".wav")):
                    fpath = os.path.join(self.captures_dir, fname)
                    try:
                        with open(fpath, "rb") as f:
                            hashes[fname] = hashlib.sha256(f.read()).hexdigest()
                    except Exception:
                        pass
        return hashes
