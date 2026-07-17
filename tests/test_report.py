# tests/test_report.py
import os
import json
import tempfile
from unittest.mock import MagicMock, patch

from config.schema import AppConfig, TelegramConfig
from modules.report import (
    get_local_ip,
    get_mac_address,
    get_boot_time,
    get_logged_in_user,
    ReportModule,
)


def test_metadata_collection_utilities():
    """Verify that metadata collection utilities return sensible non-empty strings."""
    ip = get_local_ip()
    assert isinstance(ip, str)
    assert len(ip) > 0

    mac = get_mac_address()
    assert isinstance(mac, str)
    assert len(mac) > 0

    bt = get_boot_time()
    assert isinstance(bt, str)
    assert len(bt) > 0

    user = get_logged_in_user()
    assert isinstance(user, str)
    assert len(user) > 0


def test_pdf_report_compilation_and_generation():
    """Verify that ReportModule builds a valid PDF file with system details, stats, timeline, and image."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # 1. Create a mock face_stats.json
        stats_data = {"suppressed_owner_matches": 12, "escalated_intrusions": 3}
        stats_path = os.path.join(tmp_dir, "face_stats.json")
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats_data, f)

        # 2. Create a dummy alert JPEG file using PIL
        from PIL import Image as PILImage

        dummy_img_path = os.path.join(tmp_dir, "alert_1720888800.jpg")
        img = PILImage.new("RGB", (100, 100), color="red")
        img.save(dummy_img_path)

        # Mock get_captures_dir to point to our temp folder so it loads face_stats and scans files
        with patch("modules.report.get_captures_dir", return_value=tmp_dir):
            rm = ReportModule()
            pdf_path = rm.execute(save_dir=tmp_dir)

            assert pdf_path is not None
            assert os.path.exists(pdf_path)
            assert pdf_path.endswith(".pdf")
            assert os.path.getsize(pdf_path) > 0


@patch("modules.report.ReportModule.execute")
def test_telegram_polling_report_command_dispatch(mock_report_execute):
    """Verify that /report command triggers report generation, document upload, and cleanup."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        fake_pdf = os.path.join(tmp_dir, "VigiLo_Incident_Report_test.pdf")
        with open(fake_pdf, "wb") as f:
            f.write(b"%PDF-1.4 mock pdf data")

        mock_report_execute.return_value = fake_pdf

        mock_tg_client = MagicMock()
        mock_tg_client.send_document.return_value = True

        app_config = AppConfig(telegram=TelegramConfig("token", "12345"))

        from services.telegram_polling import TelegramPollingService

        service = TelegramPollingService(
            telegram_client=mock_tg_client,
            app_config=app_config,
            captures_dir=tmp_dir,
        )

        # Run command execution in synchronous wrapper to avoid background thread racing in test
        with patch(
            "security.core.security_core.authorization_manager.authorize_request",
            return_value=True,
        ), patch("security.core.security_core.authorization_manager.authorize_action"):
            # Directly call _run_report synchronously
            service._run_report()

        # Check report was executed, document sent, and temp file cleaned up
        mock_report_execute.assert_called_once_with(tmp_dir)
        mock_tg_client.send_document.assert_called_once_with(
            fake_pdf, caption="📊 VigiLo Security Report"
        )
        assert not os.path.exists(fake_pdf)  # Cleanup verified
