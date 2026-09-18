"""Synthetic, non-biometric fixture for UI demos and deterministic tests."""

from __future__ import annotations

import math


def synthetic_landmarks(
    *,
    aspect: float = 1.36,
    forehead_ratio: float = 0.88,
    jaw_ratio: float = 0.82,
) -> list[tuple[float, float, float]]:
    points = [(0.5, 0.5, 0.0) for _ in range(478)]
    cheek_width = 0.42
    half_cheek = cheek_width / 2
    half_forehead = cheek_width * forehead_ratio / 2
    half_jaw = cheek_width * jaw_ratio / 2
    face_height = cheek_width * aspect

    # Fill an ellipse so preview bounds behave like real landmark output.
    for index in range(478):
        angle = 2 * math.pi * index / 478
        points[index] = (
            0.5 + half_cheek * math.cos(angle),
            0.48 + face_height / 2 * math.sin(angle),
            0.0,
        )
    anchors = {
        10: (0.5, 0.48 - face_height / 2, 0.0),
        152: (0.5, 0.48 + face_height / 2, 0.0),
        103: (0.5 - half_forehead, 0.32, 0.0),
        332: (0.5 + half_forehead, 0.32, 0.0),
        234: (0.5 - half_cheek, 0.49, 0.0),
        454: (0.5 + half_cheek, 0.49, 0.0),
        172: (0.5 - half_jaw, 0.65, 0.0),
        397: (0.5 + half_jaw, 0.65, 0.0),
        1: (0.5, 0.49, -0.02),
    }
    for index, point in anchors.items():
        points[index] = point
    return points


def demo_portrait(size: tuple[int, int] = (720, 720)):
    """Create an original abstract portrait; imports Pillow only when needed."""

    from PIL import Image, ImageDraw

    image = Image.new("RGB", size, "#e8ecf2")
    draw = ImageDraw.Draw(image)
    width, height = size
    draw.rounded_rectangle((0, 0, width, height), radius=54, fill="#e8ecf2")
    draw.ellipse((width * 0.28, height * 0.15, width * 0.72, height * 0.82), fill="#d8a27f")
    draw.ellipse((width * 0.37, height * 0.40, width * 0.41, height * 0.44), fill="#293241")
    draw.ellipse((width * 0.59, height * 0.40, width * 0.63, height * 0.44), fill="#293241")
    draw.arc(
        (width * 0.43, height * 0.56, width * 0.57, height * 0.67), 10, 170, fill="#7a3e2f", width=5
    )
    return image
