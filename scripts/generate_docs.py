import os

def generate_api_reference_md(output_path: str):
    content = [
        "# VigiLo Public API Reference (v1)",
        "",
        "> Stable, versioned public API facade (`src/api/v1/public_api.py`) exposing core VigiLo capabilities to UI components, plugins, and automation engines.",
        "",
        "## Endpoints & Methods",
        "",
        "### 1. Device State API",
        "- `get_device_state() -> str`: Returns current DeviceState (`DISARMED`, `WATCH_MODE`, `LOST_MODE`).",
        "- `set_device_state(target_state: str, reason: str, actor: str) -> bool`: Transitions system state.",
        "",
        "### 2. Device Identity API",
        "- `get_device_identity() -> DeviceIdentityModel`: Returns hardware-bound UUID, Public ID, and RSA fingerprint.",
        "",
        "### 3. Timeline & Incident API",
        "- `get_timeline_events(filter_type: str, limit: int) -> List[IncidentEvent]`: Fetches persistent timeline.",
        "- `record_incident(event_type: str, severity: str, description: str, metadata: dict) -> IncidentEvent`: Records event with SHA-256 hash.",
        "- `generate_forensic_report() -> IncidentReportModel`: Compiles tamper-evident forensic report.",
        "",
        "### 4. Health & Diagnostics API",
        "- `get_system_health() -> str`: Returns aggregate system status (`HEALTHY`, `DEGRADED`, `UNHEALTHY`).",
        "- `run_self_diagnostics() -> Dict`: Runs automated probe checks.",
        "",
        "### 5. Observability API",
        "- `get_telemetry_snapshot() -> TelemetrySnapshot`: Exposes real-time CPU, RAM, queue size, thread counts."
    ]
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(content))
    print(f"[DOC-GEN] Created {output_path}")

def generate_plugin_sdk_guide_md(output_path: str):
    content = [
        "# VigiLo Plugin SDK Developer Guide",
        "",
        "> Official Plugin SDK (`sdk/vigi_sdk.py`) enabling third-party developers to build custom commands, notification providers, widgets, and recovery modules without modifying core code.",
        "",
        "## Plugin Lifecycle",
        "1. `on_load(sdk: IVigiLoSDKFacade) -> bool`: Invoked when plugin is enabled.",
        "2. `on_unload() -> None`: Invoked during plugin disable or platform shutdown.",
        "",
        "## Declaring Plugin Permissions",
        "Plugins must declare required permissions in their `PluginManifest`:",
        "```python",
        "manifest = PluginManifest(",
        "    plugin_id='my_custom_plugin',",
        "    name='Custom Recovery Plugin',",
        "    version='1.0.0',",
        "    author='Developer Name',",
        "    description='Extends recovery capabilities',",
        "    required_permissions=['read_timeline', 'dispatch_notification'],",
        "    trust_level='COMMUNITY'",
        ")",
        "```"
    ]
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(content))
    print(f"[DOC-GEN] Created {output_path}")

def main():
    generate_api_reference_md("docs/api_reference.md")
    generate_plugin_sdk_guide_md("docs/plugin_sdk_guide.md")

if __name__ == "__main__":
    main()
