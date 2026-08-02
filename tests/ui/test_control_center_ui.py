import pytest
from src.ui.themes.fluent_theme import FluentThemeManager
from src.ui.services.dashboard_service import DashboardService
from src.ui.viewmodels.dashboard_viewmodel import DashboardViewModel, ObservableProperty

class TestControlCenterUI:
    def test_fluent_theme_palettes(self):
        dark_pal = FluentThemeManager("dark").get_palette()
        assert dark_pal.bg_canvas == "#0f172a"
        assert dark_pal.accent_blue == "#0284c7"

        light_pal = FluentThemeManager("light").get_palette()
        assert light_pal.bg_canvas == "#f8fafc"

        hc_pal = FluentThemeManager("high_contrast").get_palette()
        assert hc_pal.bg_canvas == "#000000"

    def test_observable_property_binding(self):
        prop = ObservableProperty("Initial")
        events = []
        prop.subscribe(lambda val: events.append(val))

        prop.set("Updated")
        assert len(events) == 1
        assert events[0] == "Updated"

    def test_dashboard_service_summary(self):
        svc = DashboardService()
        summary = svc.get_summary()

        assert summary.device_name != ""
        assert summary.device_id.startswith("VIGI-")
        assert summary.cpu_percent >= 0.0
        assert summary.ram_used_mb > 0
        assert len(summary.services) == 8

    def test_dashboard_viewmodel_data_binding(self):
        svc = DashboardService()
        vm = DashboardViewModel(svc)

        summary = vm.summary.get()
        assert summary is not None
        assert summary.protection_status in ["PROTECTED", "WARNING", "CRITICAL"]

        # Run Self-Test via ViewModel
        vm.run_self_test()
        diag_rep = vm.diagnostic_report.get()
        assert diag_rep is not None
        assert "overall_status" in diag_rep
