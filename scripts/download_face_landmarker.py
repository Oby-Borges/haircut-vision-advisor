"""Download the official MediaPipe Face Landmarker task model."""

from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/"
    "face_landmarker/float16/1/face_landmarker.task"
)
DESTINATION = Path(__file__).resolve().parents[1] / "models" / "face_landmarker.task"


def main() -> None:
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading official model to {DESTINATION} ...")
    urllib.request.urlretrieve(MODEL_URL, DESTINATION)
    size = DESTINATION.stat().st_size
    if size < 1_000_000:
        DESTINATION.unlink(missing_ok=True)
        raise RuntimeError("Downloaded model was unexpectedly small and was removed")
    digest = hashlib.sha256(DESTINATION.read_bytes()).hexdigest()
    print(f"Downloaded {size:,} bytes; SHA-256 {digest}")


if __name__ == "__main__":
    main()
