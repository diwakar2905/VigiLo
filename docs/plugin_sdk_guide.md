# VigiLo Plugin SDK Developer Guide

> Official Plugin SDK (`sdk/vigi_sdk.py`) enabling third-party developers to build custom commands, notification providers, widgets, and recovery modules without modifying core code.

## Plugin Lifecycle
1. `on_load(sdk: IVigiLoSDKFacade) -> bool`: Invoked when plugin is enabled.
2. `on_unload() -> None`: Invoked during plugin disable or platform shutdown.

## Declaring Plugin Permissions
Plugins must declare required permissions in their `PluginManifest`:
```python
manifest = PluginManifest(
    plugin_id='my_custom_plugin',
    name='Custom Recovery Plugin',
    version='1.0.0',
    author='Developer Name',
    description='Extends recovery capabilities',
    required_permissions=['read_timeline', 'dispatch_notification'],
    trust_level='COMMUNITY'
)
```