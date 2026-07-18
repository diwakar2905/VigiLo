# tests/test_face_verification.py
import json
import os
import tempfile
import numpy as np
from unittest.mock import MagicMock, patch

from config.schema import AppConfig, FaceVerificationConfig, TelegramConfig
from config.manager import ConfigManager
from modules.face_verification import (
    FaceVerificationModule,
    FaceStats,
    serialize_embedding,
    deserialize_embedding,
)


def test_embedding_serialization():
    """Verify that embeddings can be serialized and deserialized accurately."""
    original = np.array([0.1, -0.2, 0.5, 0.9], dtype=np.float32)
    serialized = serialize_embedding(original)
    assert isinstance(serialized, str)

    deserialized = deserialize_embedding(serialized)
    assert np.allclose(original, deserialized)


def test_face_verification_module_not_initialized():
    """Verify module returns False on initialize when model paths are missing."""
    fvm = FaceVerificationModule(
        yunet_path="nonexistent_yunet.onnx", sface_path="nonexistent_sface.onnx"
    )
    assert not fvm.initialize()
    assert fvm.extract_embedding("any_image.jpg") is None


@patch("modules.face_verification.logger")
def test_face_verification_verify_logic(mock_logger):
    """Verify match logic under matching and non-matching thresholds using mocked CV2 components."""
    fvm = FaceVerificationModule(
        yunet_path="mock_yunet.onnx", sface_path="mock_sface.onnx"
    )
    fvm._initialized = True

    # Create mock recognizer
    mock_recognizer = MagicMock()
    fvm._recognizer = mock_recognizer

    # Mock extract_embedding to return a dummy embedding
    dummy_emb = np.array([0.1, 0.2], dtype=np.float32)
    fvm.extract_embedding = MagicMock(return_value=dummy_emb)

    ref_embs = [np.array([0.3, 0.4], dtype=np.float32)]

    # Scenario 1: Match score >= threshold (0.363)
    mock_recognizer.match.return_value = 0.5
    assert fvm.verify("dummy.jpg", ref_embs) is True

    # Scenario 2: Match score < threshold
    mock_recognizer.match.return_value = 0.2
    assert fvm.verify("dummy.jpg", ref_embs) is False

    # Scenario 3: Empty references
    assert fvm.verify("dummy.jpg", []) is False


def test_face_stats_recording():
    """Verify that FaceStats records attempts accurately to face_stats.json."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Patch get_captures_dir to point to temporary directory
        with patch("modules.face_verification.get_captures_dir", return_value=tmp_dir):
            stats_path = os.path.join(tmp_dir, "face_stats.json")

            # 1. Record owner attempt (suppressed match)
            FaceStats.record_attempt(is_owner=True)
            assert os.path.exists(stats_path)
            with open(stats_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert data["suppressed_owner_matches"] == 1
            assert data["escalated_intrusions"] == 0

            # 2. Record intruder attempt (escalated intrusion)
            FaceStats.record_attempt(is_owner=False)
            with open(stats_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert data["suppressed_owner_matches"] == 1
            assert data["escalated_intrusions"] == 1


def test_config_save_load_roundtrip_encryption():
    """Verify config save/load roundtrip encrypts and decrypts face embeddings using DPAPI."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        config_path = os.path.join(tmp_dir, "config.json")

        # Create dummy app config
        dummy_emb = np.array([0.1, -0.2, 0.3], dtype=np.float32)
        serialized_emb = serialize_embedding(dummy_emb)

        app_config = AppConfig(
            telegram=TelegramConfig("token", "chatid"),
            face_verification=FaceVerificationConfig(
                enabled=True,
                threshold=0.363,
                reference_embeddings=[serialized_emb],
            ),
        )

        # Save config
        manager = ConfigManager(config_path=config_path)
        save_success = manager.save(app_config)
        assert save_success is True

        # Assert saved config file contains encrypted string (so it shouldn't look like original serialized json)
        with open(config_path, "r", encoding="utf-8") as f:
            saved_raw_dict = json.load(f)

        saved_ref_embs = saved_raw_dict["face_verification"]["reference_embeddings"]
        assert len(saved_ref_embs) == 1
        assert saved_ref_embs[0] != serialized_emb  # DPAPI encrypted

        # Load config and verify decrypted result matches original
        loaded_manager = ConfigManager(config_path=config_path)
        loaded_config = loaded_manager.config
        assert loaded_config.face_verification.enabled is True
        assert loaded_config.face_verification.threshold == 0.363
        assert len(loaded_config.face_verification.reference_embeddings) == 1
        assert loaded_config.face_verification.reference_embeddings[0] == serialized_emb


@patch("core.engine.CameraModule")
@patch("modules.face_verification.FaceVerificationModule")
def test_capture_alert_flow_integration(mock_fvm_class, mock_camera_class):
    """Verify capture_alert suppression/escalation flow based on face match results."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        config_path = os.path.join(tmp_dir, "config.json")

        dummy_emb = np.array([0.1, -0.2], dtype=np.float32)
        serialized_emb = serialize_embedding(dummy_emb)

        # Setup configuration with face verification enabled
        app_config = AppConfig(
            telegram=TelegramConfig("token123", "chatid456"),
            face_verification=FaceVerificationConfig(
                enabled=True,
                threshold=0.363,
                reference_embeddings=[serialized_emb],
            ),
        )

        manager = ConfigManager(config_path=config_path)
        manager.save(app_config)

        # Instantiate engine using the mock configuration
        from core.engine import VigiLoEngine

        engine = VigiLoEngine(config_path=config_path)
        engine.captures_dir = tmp_dir

        # Setup mock camera execute to write a dummy image file
        mock_camera = MagicMock()
        mock_camera_class.return_value = mock_camera

        def fake_camera_execute(save_dir, prefix):
            # Create a mock physical image file
            path = os.path.join(save_dir, f"{prefix}mock_image.jpg")
            with open(path, "w") as f:
                f.write("mock image data")
            return path

        mock_camera.execute.side_effect = fake_camera_execute

        # Setup mock face verification module
        mock_fvm = MagicMock()
        mock_fvm_class.return_value = mock_fvm

        # Test Case 1: Match Owner -> Alert is Suppressed (image is deleted)
        mock_fvm.verify.return_value = True

        with patch("modules.face_verification.get_captures_dir", return_value=tmp_dir):
            engine.capture_alert()

            # The file should be deleted on match
            files_left = os.listdir(tmp_dir)
            # Filter config files
            alert_files = [f for f in files_left if "alert" in f]
            assert len(alert_files) == 0

            # Test Case 2: Mismatch (Intruder) -> Alert is Escalated (image kept and renamed to alert_ prefix)
            mock_fvm.verify.return_value = False
            engine.last_capture_time = 0  # reset cooldown
            engine.capture_alert()

            files_left = os.listdir(tmp_dir)
            alert_files = [f for f in files_left if f.startswith("alert_")]
            assert len(alert_files) == 1
            assert alert_files[0].endswith(".jpg")
