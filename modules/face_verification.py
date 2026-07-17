# modules/face_verification.py
"""Face Verification Module for VigiLo.

Uses YuNet (face detection) and SFace (face recognition) ONNX models
to perform local, private face verification.
"""

from __future__ import annotations

import json
import os
import numpy as np

from modules.base import BaseModule
from utils.system import get_base_dir, get_captures_dir
from logs.logger import logger

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
YUNET_URL: str = (
    "https://github.com/SaifullahSayyed/VigiLo/releases/download/v2.0.0/face_detection_yunet.onnx"
)
YUNET_HASH: str = "a7d8d21adcb5c64c7e6c0c21323f4963574c88597f8c950228e9323f40f0f0c0"

SFACE_URL: str = (
    "https://github.com/SaifullahSayyed/VigiLo/releases/download/v2.0.0/face_recognition_sface.onnx"
)
SFACE_HASH: str = "6e6f6630f9a2b85e0031940989f5bc3e264ef8b4a034ee51016834b9d0f0f0c0"


def get_model_paths() -> tuple[str, str]:
    """Returns absolute paths to local model cache files (YuNet, SFace)."""
    base_dir = get_base_dir()
    models_dir = os.path.join(base_dir, "models")
    yunet_path = os.path.join(models_dir, "face_detection_yunet.onnx")
    sface_path = os.path.join(models_dir, "face_recognition_sface.onnx")
    return yunet_path, sface_path


def serialize_embedding(embedding: np.ndarray) -> str:
    """Serializes a numpy float32 embedding array to a JSON list string."""
    return json.dumps(embedding.tolist())


def deserialize_embedding(serialized_str: str) -> np.ndarray:
    """Deserializes a JSON list string back to a numpy float32 array."""
    data = json.loads(serialized_str)
    return np.array(data, dtype=np.float32)


class FaceVerificationModule(BaseModule):
    """Integrates OpenCV YuNet and SFace models for face authentication.

    Parameters
    ----------
    yunet_path:
        Path to local YuNet model ONNX file.
    sface_path:
        Path to local SFace model ONNX file.
    threshold:
        Cosine similarity threshold for a match (default 0.363).
    """

    def __init__(
        self,
        yunet_path: str | None = None,
        sface_path: str | None = None,
        threshold: float = 0.363,
    ) -> None:
        p1, p2 = get_model_paths()
        self.yunet_path = yunet_path if yunet_path else p1
        self.sface_path = sface_path if sface_path else p2
        self.threshold = threshold

        self._detector = None
        self._recognizer = None
        self._initialized = False

    def execute(self, image_path: str, reference_embeddings: list[np.ndarray]) -> bool:
        """Executes face verification check on the target image."""
        return self.verify(image_path, reference_embeddings)

    def initialize(self) -> bool:
        """Loads and initializes YuNet detector and SFace recognizer engines."""
        if self._initialized:
            return True

        if not os.path.exists(self.yunet_path) or not os.path.exists(self.sface_path):
            logger.warning(
                "FaceVerificationModule: Missing model ONNX files. Cannot initialize."
            )
            return False

        try:
            import cv2

            # Instantiate YuNet detector
            self._detector = cv2.FaceDetectorYN.create(
                model=self.yunet_path,
                config="",
                input_size=(320, 320),
                score_threshold=0.9,
                nms_threshold=0.3,
            )

            # Instantiate SFace recognizer
            self._recognizer = cv2.FaceRecognizerSF.create(
                model=self.sface_path, config=""
            )

            self._initialized = True
            logger.info(
                "FaceVerificationModule: Successfully initialized face recognition engines."
            )
            return True
        except Exception as exc:
            logger.error(f"FaceVerificationModule: Initialization exception: {exc}")
            return False

    def extract_embedding(self, image_path: str) -> np.ndarray | None:
        """Loads the image, detects the face, aligns it, and returns its feature vector."""
        if not self.initialize():
            return None

        try:
            import cv2

            img = cv2.imread(image_path)
            if img is None:
                logger.error(
                    f"FaceVerificationModule: Image file could not be read: {image_path}"
                )
                return None

            height, width = img.shape[:2]
            self._detector.setInputSize((width, height))

            retval, faces = self._detector.detect(img)
            if retval == 0 or faces is None or len(faces) == 0:
                logger.info("FaceVerificationModule: No face detected in the image.")
                return None

            # Align and crop the dominant face (first face detected)
            aligned_face = self._recognizer.alignCrop(img, faces[0])
            embedding = self._recognizer.feature(aligned_face)
            return embedding
        except Exception as exc:
            logger.error(
                f"FaceVerificationModule: Embedding extraction exception: {exc}"
            )
            return None

    def verify(self, image_path: str, reference_embeddings: list[np.ndarray]) -> bool:
        """Compares target image face embedding against multiple enrolled reference embeddings.

        Returns True if a match exceeds the similarity threshold.
        """
        if not reference_embeddings:
            logger.warning(
                "FaceVerificationModule: No reference embeddings configured for comparison."
            )
            return False

        target_emb = self.extract_embedding(image_path)
        if target_emb is None:
            return False

        try:
            import cv2

            for ref in reference_embeddings:
                score = self._recognizer.match(
                    target_emb, ref, cv2.FaceRecognizerSF_FR_COSINE
                )
                if score >= self.threshold:
                    logger.info(
                        f"FaceVerificationModule: Verification match succeeded "
                        f"(Similarity score: {score:.4f} >= threshold: {self.threshold:.4f})."
                    )
                    return True

            logger.info(
                "FaceVerificationModule: Verification failed (no match matched the threshold)."
            )
            return False
        except Exception as exc:
            logger.error(f"FaceVerificationModule: Cosine comparison exception: {exc}")
            return False


class FaceStats:
    """Records face-matching false-alarm vs intrusion stats locally."""

    @staticmethod
    def get_stats_path() -> str:
        return os.path.join(get_captures_dir(), "face_stats.json")

    @classmethod
    def record_attempt(cls, is_owner: bool) -> None:
        path = cls.get_stats_path()
        stats = {"suppressed_owner_matches": 0, "escalated_intrusions": 0}

        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    stats = json.load(f)
            except Exception:
                pass

        if is_owner:
            stats["suppressed_owner_matches"] = (
                stats.get("suppressed_owner_matches", 0) + 1
            )
        else:
            stats["escalated_intrusions"] = stats.get("escalated_intrusions", 0) + 1

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(stats, f, indent=4)
        except Exception as exc:
            logger.error(f"FaceStats: Failed to write statistics: {exc}")
