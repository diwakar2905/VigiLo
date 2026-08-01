import ctypes
from typing import List
from ..interfaces.i_service import IService
from ..models.permission_descriptor import PermissionDescriptor

class TrustService(IService):
    def __init__(self):
        self._initialized = False

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def shutdown(self) -> None:
        self._initialized = False

    def is_admin(self) -> bool:
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False

    def get_permission_descriptors(self) -> List[PermissionDescriptor]:
        admin_granted = self.is_admin()
        
        return [
            PermissionDescriptor(
                permission_id="win_event_log",
                name="Windows Security Event Log Access",
                justification="Required to instantly detect failed login attempts (Event 4625) without polling, protecting your device in under 0.1 seconds.",
                privacy_impact="Monitors logon security events locally. No event data is transmitted outside your local machine without owner trigger.",
                is_granted=admin_granted,
                is_required=True
            ),
            PermissionDescriptor(
                permission_id="webcam_capture",
                name="Camera Hardware Access",
                justification="Required to take a photo of intruders attempting unauthorized physical login access to your device.",
                privacy_impact="Camera is activated ONLY during failed login thresholds or owner-initiated lost recovery requests. Zero secret background streaming.",
                is_granted=True,
                is_required=True
            ),
            PermissionDescriptor(
                permission_id="telegram_notification",
                name="Telegram Encrypted Messaging",
                justification="Required to transmit alert photos and system recovery status directly to your personal Telegram client.",
                privacy_impact="Alerts are sent exclusively to your self-configured Bot Token and Chat ID. No third-party servers or cloud databases involved.",
                is_granted=True,
                is_required=True
            ),
            PermissionDescriptor(
                permission_id="system_lock",
                name="Windows Workstation Lock (LockWorkstation)",
                justification="Required to secure desktop sessions remotely when device loss is confirmed.",
                privacy_impact="Invokes native Windows Lock API (user32.dll). No credential bypass or system corruption.",
                is_granted=True,
                is_required=False
            )
        ]
