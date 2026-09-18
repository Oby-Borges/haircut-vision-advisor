"""Landmark-based face proportions for near-frontal images."""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

from .types import FaceMeasurements

LANDMARKS = {
    "forehead_top": 10,
    "chin": 152,
    "forehead_left": 103,
    "forehead_right": 332,
    "cheek_left": 234,
    "cheek_right": 454,
    "jaw_left": 172,
    "jaw_right": 397,
    "nose": 1,
}


def _xy(point: Any) -> tuple[float, float]:
    if hasattr(point, "x"):
        return float(point.x), float(point.y)
    return float(point[0]), float(point[1])


def _distance(a: Any, b: Any) -> float:
    ax, ay = _xy(a)
    bx, by = _xy(b)
    return math.hypot(ax - bx, ay - by)


def extract_measurements(landmarks: Sequence[Any]) -> FaceMeasurements:
    """Return normalized measurements from a MediaPipe-compatible landmark list."""

    required_max = max(LANDMARKS.values())
    if len(landmarks) <= required_max:
        raise ValueError(f"Expected at least {required_max + 1} landmarks, got {len(landmarks)}")

    p = {name: landmarks[index] for name, index in LANDMARKS.items()}
    face_length_raw = _distance(p["forehead_top"], p["chin"])
    forehead_raw = _distance(p["forehead_left"], p["forehead_right"])
    cheek_raw = _distance(p["cheek_left"], p["cheek_right"])
    jaw_raw = _distance(p["jaw_left"], p["jaw_right"])
    if cheek_raw <= 1e-8:
        raise ValueError("Cheekbone width is zero; landmarks are not usable")

    nose_left = _distance(p["nose"], p["cheek_left"])
    nose_right = _distance(p["nose"], p["cheek_right"])
    yaw = abs(nose_left - nose_right) / max(nose_left + nose_right, 1e-8)

    return FaceMeasurements(
        face_length=face_length_raw / cheek_raw,
        forehead_width=forehead_raw / cheek_raw,
        cheekbone_width=1.0,
        jaw_width=jaw_raw / cheek_raw,
        length_to_width=face_length_raw / cheek_raw,
        forehead_to_cheek=forehead_raw / cheek_raw,
        jaw_to_cheek=jaw_raw / cheek_raw,
        yaw_asymmetry=yaw,
    )


def landmark_bounds(landmarks: Sequence[Any]) -> tuple[float, float, float, float]:
    """Return normalized min-x, min-y, max-x, max-y bounds."""

    points = [_xy(point) for point in landmarks]
    xs, ys = zip(*points, strict=True)
    return min(xs), min(ys), max(xs), max(ys)
