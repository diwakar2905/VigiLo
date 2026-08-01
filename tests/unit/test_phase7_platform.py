import os
import tempfile
import shutil
import pytest

from src.core.events import EventBus, VigiLoEvent
from src.core.services.webhooks import WebhookEngine
from src.api.v1 import VigiLoPublicAPIv1
from src.core.plugins import PluginManager
from src.core.plugins.marketplace import MarketplaceService, MarketplaceItem
from src.core.scripting import ScriptEngine
from src.ui.themes import ThemeManager
from src.core.i18n import I18nService
from src.core.exceptions import SecurityException
from sdk.vigi_sdk import IVigiLoPlugin, PluginManifest, IVigiLoSDKFacade

class SamplePlugin(IVigiLoPlugin):
    def __init__(self, perms=None):
        self._perms = perms or ["read_timeline", "dispatch_notification"]
        self.loaded = False

    @property
    def manifest(self) -> PluginManifest:
        return PluginManifest(
            plugin_id="sample_plugin",
            name="Sample Plugin",
            version="1.0.0",
            author="Tester",
            description="Test Plugin",
            required_permissions=self._perms
        )

    def on_load(self, sdk: IVigiLoSDKFacade) -> bool:
        self.loaded = True
        return True

    def on_unload(self) -> None:
        self.loaded = False

class TestPhase7Platform:
    def setup_method(self):
        self.test_dir = tempfile.mkdtemp()

    def teardown_method(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_event_bus_pub_sub(self):
        eb = EventBus()
        eb.initialize()

        received = []
        eb.subscribe("TEST_EVENT", lambda evt: received.append(evt.data["msg"]))

        eb.publish(VigiLoEvent("TEST_EVENT", {"msg": "Hello EventBus"}))
        assert len(received) == 1
        assert received[0] == "Hello EventBus"

    def test_webhook_hmac_signature(self):
        eb = EventBus()
        eb.initialize()

        engine = WebhookEngine(eb)
        engine.initialize()

        payload = b'{"key": "value"}'
        sig = engine.compute_hmac_signature(payload, "secret123")
        assert len(sig) == 64  # SHA-256 hex digest length

    def test_public_api_v1(self):
        api = VigiLoPublicAPIv1()
        assert api.version == "1.0.0"
        state = api.get_device_state()
        assert state in ["DISARMED", "WATCH_MODE", "LOST_MODE"]

        ident = api.get_device_identity()
        assert ident.public_id.startswith("VIGI-")

        telemetry = api.get_telemetry_snapshot()
        assert telemetry.ram_used_mb > 0

    def test_plugin_sdk_lifecycle_and_sandboxing(self):
        api = VigiLoPublicAPIv1()
        pm = PluginManager(api)
        pm.initialize()

        plugin = SamplePlugin()
        assert pm.install_plugin(plugin) is True
        assert pm.enable_plugin("sample_plugin") is True
        assert len(pm.get_active_plugins()) == 1

        # Disable plugin
        assert pm.disable_plugin("sample_plugin") is True
        assert len(pm.get_active_plugins()) == 0

    def test_plugin_permission_denied(self):
        api = VigiLoPublicAPIv1()
        pm = PluginManager(api)
        pm.initialize()

        # Plugin without read_timeline permission
        plugin = SamplePlugin(perms=["dispatch_notification"])
        pm.install_plugin(plugin)
        pm.enable_plugin("sample_plugin")

        from src.core.plugins.plugin_manager import VigiLoSDKFacadeImpl
        facade = VigiLoSDKFacadeImpl(plugin.manifest, api)

        with pytest.raises(SecurityException):
            facade.get_timeline_events()

    def test_script_engine_ast_sandboxing(self):
        eb = EventBus()
        eb.initialize()

        se = ScriptEngine(eb)
        se.initialize()

        # Valid script
        rule_id = se.register_rule("TestRule", "TEST_EVT", "print('AST Safe Execution')")
        assert rule_id.startswith("RULE-")

        # Invalid script with prohibited import
        with pytest.raises(SecurityException):
            se.register_rule("BadRule", "TEST_EVT", "import os\nos.system('calc')")

    def test_theme_manager(self):
        tm = ThemeManager()
        t = tm.get_current_theme()
        assert t.theme_name == "dark"
        assert tm.set_theme("light") is True
        assert tm.get_current_theme().bg_primary == "#ffffff"

    def test_i18n_service(self):
        locales_dir = os.path.join(self.test_dir, "locales")
        os.makedirs(locales_dir, exist_ok=True)
        with open(os.path.join(locales_dir, "en.json"), "w", encoding="utf-8") as f:
            f.write('{"hello": "Hello {name}"}')

        i18n = I18nService(locales_dir, "en")
        i18n.initialize()
        assert i18n.translate("hello", name="VigiLo") == "Hello VigiLo"

    def test_marketplace_service(self):
        ms = MarketplaceService()
        ms.initialize()

        manifest = PluginManifest("p1", "Test Plugin", "1.0", "Author", "Desc", [])
        item = MarketplaceItem(manifest, "http://dl", True, 4.8, 100)
        ms.register_item(item)

        results = ms.search_catalog("Test")
        assert len(results) == 1
        assert ms.verify_publisher_signature(item) is False  # Missing signature string
