import os
import json
from typing import Dict, Any, List
from ..interfaces.i_service import IService
from ..exceptions.vigi_exceptions import SecurityException, ConfigurationException

class SecurityPolicyService(IService):
    def __init__(self, policy_filepath: str):
        self.policy_filepath = policy_filepath
        self._policies: Dict[str, Dict[str, Any]] = {}
        self._initialized = False

    def initialize(self) -> bool:
        os.makedirs(os.path.dirname(self.policy_filepath), exist_ok=True)
        if os.path.exists(self.policy_filepath):
            try:
                with open(self.policy_filepath, "r", encoding="utf-8") as f:
                    self._policies = json.load(f)
            except Exception:
                self._policies = self._default_policies()
        else:
            self._policies = self._default_policies()
            self._save_policies()

        self._initialized = True
        return True

    def shutdown(self) -> None:
        self._initialized = False

    def evaluate_filesystem_policy(self, target_path: str, action: str) -> bool:
        policy = self._policies.get("filesystem", {})
        allowed_dirs: List[str] = policy.get("allowed_directories", [])
        
        abs_target = os.path.abspath(target_path).lower()
        is_safe = any(abs_target.startswith(os.path.abspath(d).lower()) for d in allowed_dirs)

        if not is_safe:
            raise SecurityException(f"Filesystem policy violation: Access to '{target_path}' prohibited under action '{action}'.")
        return True

    def evaluate_command_policy(self, command_name: str) -> bool:
        policy = self._policies.get("commands", {})
        allowed_cmds: List[str] = policy.get("allowed_commands", [])
        prohibited_cmds: List[str] = policy.get("prohibited_commands", [])

        clean_cmd = command_name.lower().strip()
        if clean_cmd in [c.lower() for c in prohibited_cmds]:
            raise SecurityException(f"Security Policy Violation: Command '{command_name}' is explicitly prohibited.")
        return True

    def evaluate_notification_policy(self, provider_type: str) -> bool:
        policy = self._policies.get("notification", {})
        enabled_providers: List[str] = policy.get("enabled_providers", [])
        return provider_type.lower() in [p.lower() for p in enabled_providers]

    def _default_policies(self) -> Dict[str, Dict[str, Any]]:
        program_data = os.getenv("PROGRAMDATA") or "C:\\ProgramData"
        captures_dir = os.path.join(program_data, "AntiTheftCaptures")
        vigilo_dir = os.path.join(program_data, "VigiLo")

        return {
            "filesystem": {
                "allowed_directories": [captures_dir, vigilo_dir],
                "max_file_size_mb": 50
            },
            "commands": {
                "allowed_commands": ["/ping", "/mode", "/status", "/disarm", "/watch", "/lost", "/report", "/timeline", "/trust", "/capture", "/screen", "/locate", "/lock", "/msg"],
                "prohibited_commands": ["rmdir /s", "format", "powershell -encodedcommand", "del /f"]
            },
            "notification": {
                "enabled_providers": ["telegram", "webhook"],
                "max_retries": 3
            },
            "recovery": {
                "require_owner_confirmation": True,
                "auto_lock_on_lost_mode": True
            }
        }

    def _save_policies(self) -> None:
        try:
            with open(self.policy_filepath, "w", encoding="utf-8") as f:
                json.dump(self._policies, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Failed to save security policies: {e}")
