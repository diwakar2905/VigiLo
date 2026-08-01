import os
from typing import Dict, List, Optional, Any
from src.core.interfaces.i_service import IService
from src.api.v1.public_api import VigiLoPublicAPIv1
from src.core.exceptions.vigi_exceptions import SecurityException
from src.core.services.notifications.notification_message import NotificationMessage
from sdk.vigi_sdk import IVigiLoPlugin, IVigiLoSDKFacade, PluginManifest

class VigiLoSDKFacadeImpl(IVigiLoSDKFacade):
    """SDK Facade implementation enforcing plugin permission sandboxing."""

    def __init__(self, manifest: PluginManifest, api: VigiLoPublicAPIv1):
        self.manifest = manifest
        self.api = api

    def _check_perm(self, perm_name: str) -> None:
        if perm_name not in self.manifest.required_permissions:
            raise SecurityException(f"Plugin '{self.manifest.plugin_id}' lacks required permission '{perm_name}'.")

    def get_platform_version(self) -> str:
        return self.api.version

    def get_device_state(self) -> str:
        return self.api.get_device_state()

    def get_timeline_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        self._check_perm("read_timeline")
        events = self.api.get_timeline_events(limit=limit)
        return [e.to_dict() for e in events]

    def record_incident(self, event_type: str, severity: str, description: str) -> bool:
        self._check_perm("write_incident")
        evt = self.api.record_incident(event_type, severity, description)
        return bool(evt)

    def send_notification(self, title: str, body: str, severity: str = "INFO") -> bool:
        self._check_perm("dispatch_notification")
        msg = NotificationMessage(title=title, body=body, severity=severity)
        return self.api._container.notification_service.dispatch(msg)

class PluginManager(IService):
    def __init__(self, api: VigiLoPublicAPIv1):
        self.api = api
        self._installed_plugins: Dict[str, IVigiLoPlugin] = {}
        self._active_plugins: Dict[str, IVigiLoPlugin] = {}
        self._initialized = False

    def initialize(self) -> bool:
        self._initialized = True
        return True

    def shutdown(self) -> None:
        for p_id in list(self._active_plugins.keys()):
            self.disable_plugin(p_id)
        self._installed_plugins.clear()
        self._initialized = False

    def install_plugin(self, plugin: IVigiLoPlugin) -> bool:
        manifest = plugin.manifest
        if manifest.plugin_id in self._installed_plugins:
            print(f"[WARN] Plugin '{manifest.plugin_id}' already installed.")
            return False
        self._installed_plugins[manifest.plugin_id] = plugin
        return True

    def enable_plugin(self, plugin_id: str) -> bool:
        if plugin_id not in self._installed_plugins:
            return False
        if plugin_id in self._active_plugins:
            return True
        
        plugin = self._installed_plugins[plugin_id]
        facade = VigiLoSDKFacadeImpl(plugin.manifest, self.api)
        
        try:
            success = plugin.on_load(facade)
            if success:
                self._active_plugins[plugin_id] = plugin
                return True
        except Exception as e:
            print(f"[ERROR] Failed to enable plugin '{plugin_id}': {e}")
        return False

    def disable_plugin(self, plugin_id: str) -> bool:
        if plugin_id in self._active_plugins:
            plugin = self._active_plugins[plugin_id]
            try:
                plugin.on_unload()
            except Exception as e:
                print(f"[ERROR] Error during plugin '{plugin_id}' unload: {e}")
            del self._active_plugins[plugin_id]
            return True
        return False

    def remove_plugin(self, plugin_id: str) -> bool:
        self.disable_plugin(plugin_id)
        if plugin_id in self._installed_plugins:
            del self._installed_plugins[plugin_id]
            return True
        return False

    def get_installed_plugins(self) -> List[PluginManifest]:
        return [p.manifest for p in self._installed_plugins.values()]

    def get_active_plugins(self) -> List[PluginManifest]:
        return [p.manifest for p in self._active_plugins.values()]
