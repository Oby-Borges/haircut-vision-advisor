"""Thin adapter around the supported MediaPipe Tasks Face Landmarker API."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[2] / "models" / "face_landmarker.task"


class VisionUnavailableError(RuntimeError):
    """Raised when MediaPipe or its model is unavailable."""


def configured_model_path() -> Path:
    return Path(os.environ.get("FACE_LANDMARKER_MODEL", DEFAULT_MODEL_PATH)).expanduser()


def detect_landmarks(
    pil_image: Any, model_path: str | Path | None = None
) -> list[tuple[float, float, float]]:
    """Detect the most prominent face and return normalized xyz tuples."""

    path = Path(model_path) if model_path else configured_model_path()
    if not path.is_file():
        raise VisionUnavailableError(
            f"Face Landmarker model not found at {path}. Run "
            "`python scripts/download_face_landmarker.py`."
        )
    try:
        import mediapipe as mp
        import numpy as np
    except ImportError as exc:
        raise VisionUnavailableError(
            "MediaPipe and NumPy are required for real image analysis. Install the project "
            "with a supported Python 3.11/3.12 environment."
        ) from exc

    rgb = pil_image.convert("RGB")
    image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.asarray(rgb))
    base_options = mp.tasks.BaseOptions(model_asset_path=str(path))
    options = mp.tasks.vision.FaceLandmarkerOptions(
        base_options=base_options,
        running_mode=mp.tasks.vision.RunningMode.IMAGE,
        num_faces=1,
        min_face_detection_confidence=0.55,
        min_face_presence_confidence=0.55,
    )
    with mp.tasks.vision.FaceLandmarker.create_from_options(options) as landmarker:
        result = landmarker.detect(image)
    if not result.face_landmarks:
        raise ValueError("No face detected. Try a centered, well-lit, near-frontal image.")
    return [(float(point.x), float(point.y), float(point.z)) for point in result.face_landmarks[0]]
