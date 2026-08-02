import os
import json
import hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from src.api.v1.public_api import VigiLoPublicAPIv1
from src.core.models.incident_event import IncidentEvent

SUPPORTED_EVENT_TYPES = [
    "FAILED_LOGIN", "SUCCESSFUL_LOGIN", "CAMERA_CAPTURE", "SCREENSHOT",
    "AUDIO_RECORDING", "NOTIFICATION_SENT", "QUEUE_RETRY", "OFFLINE_BUFFER",
    "CONFIGURATION_CHANGE", "RUNTIME_RESTART", "POLICY_VIOLATION",
    "TAMPER_DETECTION", "VAULT_LOCKED", "FACE_VERIFICATION",
    "RECOVERY_STARTED", "RECOVERY_COMPLETED"
]

@dataclass
class ForensicDetailDTO:
    incident_id: str
    severity: str
    event_type: str
    timestamp: str
    device_state: str
    user_session: str
    trigger_source: str
    description: str
    evidence_status: str
    sha256_hash: str
    correlation_id: str
    media_path: Optional[str] = None
    raw_logs: List[str] = field(default_factory=list)
    bookmarked: bool = False

class ForensicTimelineService:
    """Service providing search, filtering, and forensic detail extraction."""

    def __init__(self, api: Optional[VigiLoPublicAPIv1] = None):
        self.api = api or VigiLoPublicAPIv1()
        self._bookmarked_ids: set = set()

    def get_all_events(self, limit: int = 200) -> List[ForensicDetailDTO]:
        events = self.api.get_timeline_events(limit=limit)
        return [self._convert_to_dto(e) for e in events]

    def _convert_to_dto(self, e: IncidentEvent) -> ForensicDetailDTO:
        meta = e.metadata or {}
        return ForensicDetailDTO(
            incident_id=e.incident_id,
            severity=e.severity,
            event_type=e.event_type,
            timestamp=e.timestamp,
            device_state=meta.get("device_state", "WATCH_MODE"),
            user_session=meta.get("user_session", "SYSTEM\\Owner"),
            trigger_source=meta.get("trigger_source", "Windows EventID 4625"),
            description=e.description,
            evidence_status="VERIFIED_HASH" if e.sha256_hash else "UNVERIFIED",
            sha256_hash=e.sha256_hash or hashlib.sha256(e.description.encode('utf-8')).hexdigest().upper(),
            correlation_id=meta.get("correlation_id", f"COR-{e.incident_id[:8]}"),
            media_path=meta.get("media_path"),
            raw_logs=[f"[{e.timestamp[:19]}] Log entry for incident {e.incident_id}: {e.description}"],
            bookmarked=e.incident_id in self._bookmarked_ids
        )

    def search_and_filter(
        self,
        query: str = "",
        severity: str = "ALL",
        event_type: str = "ALL",
        bookmarked_only: bool = False
    ) -> List[ForensicDetailDTO]:
        all_dtos = self.get_all_events()
        results = []

        q = query.lower().strip()
        for d in all_dtos:
            if severity != "ALL" and d.severity.upper() != severity.upper():
                continue
            if event_type != "ALL" and d.event_type.upper() != event_type.upper():
                continue
            if bookmarked_only and not d.bookmarked:
                continue

            if q:
                match_text = f"{d.incident_id} {d.event_type} {d.description} {d.user_session} {d.trigger_source}".lower()
                if q not in match_text:
                    continue

            results.append(d)

        return results

    def toggle_bookmark(self, incident_id: str) -> bool:
        if incident_id in self._bookmarked_ids:
            self._bookmarked_ids.remove(incident_id)
            return False
        else:
            self._bookmarked_ids.add(incident_id)
            return True

    def export_investigation(self, dtos: List[ForensicDetailDTO], output_path: str) -> bool:
        try:
            records = [
                {
                    "incident_id": d.incident_id,
                    "severity": d.severity,
                    "event_type": d.event_type,
                    "timestamp": d.timestamp,
                    "device_state": d.device_state,
                    "description": d.description,
                    "sha256_hash": d.sha256_hash,
                    "correlation_id": d.correlation_id
                }
                for d in dtos
            ]
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump({"investigation_export": records}, f, indent=2)
            return True
        except Exception as e:
            print(f"[ERROR] Failed to export investigation: {e}")
            return False
