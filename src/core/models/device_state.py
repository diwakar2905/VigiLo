from enum import Enum, auto
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict

class DeviceState(Enum):
    DISARMED = "DISARMED"
    WATCH_MODE = "WATCH_MODE"
    LOST_MODE = "LOST_MODE"

@dataclass
class DeviceStateModel:
    state: DeviceState
    updated_at: str
    updated_by: str
    transition_reason: str

class FeaturePermissionMatrix:
    ALLOWED_FEATURES: Dict[DeviceState, List[str]] = {
        DeviceState.DISARMED: [
            "runtime_health",
            "configuration",
            "view_logs",
            "view_timeline"
        ],
        DeviceState.WATCH_MODE: [
            "runtime_health",
            "configuration",
            "view_logs",
            "view_timeline",
            "win_login_monitor",
            "failed_login_detection",
            "webcam_capture",
            "notification"
        ],
        DeviceState.LOST_MODE: [
            "runtime_health",
            "configuration",
            "view_logs",
            "view_timeline",
            "win_login_monitor",
            "failed_login_detection",
            "webcam_capture",
            "notification",
            "lock_device",
            "locate_device",
            "screenshot",
            "recovery_message",
            "evidence_collection",
            "incident_timeline",
            "generate_report",
            "recovery_wizard"
        ]
    }

    PROHIBITED_FEATURES: Dict[DeviceState, List[str]] = {
        DeviceState.DISARMED: [
            "win_login_monitor",
            "failed_login_detection",
            "webcam_capture",
            "notification",
            "lock_device",
            "locate_device",
            "screenshot",
            "recovery_message",
            "audio_record",
            "file_browse",
            "remote_cmd",
            "device_wipe"
        ],
        DeviceState.WATCH_MODE: [
            "audio_record",
            "file_browse",
            "remote_cmd",
            "device_wipe",
            "lock_device",
            "locate_device"
        ],
        DeviceState.LOST_MODE: [
            "audio_record",
            "file_browse",
            "remote_cmd",
            "device_wipe"
        ]
    }

    @classmethod
    def is_feature_allowed(cls, state: DeviceState, feature_name: str) -> bool:
        allowed = cls.ALLOWED_FEATURES.get(state, [])
        return feature_name.lower() in [f.lower() for f in allowed]
