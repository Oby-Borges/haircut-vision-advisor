"""License-safe programmatic hairstyle silhouette preview."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from .measurements import landmark_bounds
from .types import Hairstyle


def render_preview(
    image: Any,
    landmarks: Sequence[Any],
    style: Hairstyle,
    *,
    color: str = "#2a1a12",
    opacity: int = 205,
    scale: float = 1.0,
    x_offset: float = 0.0,
    y_offset: float = 0.0,
):
    """Overlay an original stylized silhouette aligned to landmark bounds."""

    from PIL import Image, ImageDraw

    base = image.convert("RGBA")
    width, height = base.size
    min_x, min_y, max_x, max_y = landmark_bounds(landmarks)
    face_w = (max_x - min_x) * width
    face_h = (max_y - min_y) * height
    center_x = ((min_x + max_x) / 2 + x_offset) * width
    forehead_y = (min_y + y_offset) * height
    hair_w = face_w * 1.15 * scale
    hair_h = face_h * _height_factor(style.silhouette) * scale
    left, right = center_x - hair_w / 2, center_x + hair_w / 2
    bottom = forehead_y + face_h * 0.17
    top = bottom - hair_h

    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    rgba = _parse_color(color, opacity)
    accent = (max(rgba[0] - 24, 0), max(rgba[1] - 24, 0), max(rgba[2] - 24, 0), opacity)

    silhouette = style.silhouette
    if silhouette in {"buzz", "crew"}:
        draw.pieslice(
            (left, top + hair_h * 0.25, right, bottom + hair_h * 0.30), 180, 360, fill=rgba
        )
        if silhouette == "crew":
            draw.rectangle(
                (left + hair_w * 0.15, top + hair_h * 0.28, right - hair_w * 0.12, bottom),
                fill=rgba,
            )
    elif silhouette in {"quiff", "pompadour"}:
        lift = hair_h * (0.22 if silhouette == "quiff" else 0.05)
        draw.polygon(
            [
                (left, bottom),
                (left + hair_w * 0.06, top + hair_h * 0.62),
                (left + hair_w * 0.40, top + hair_h * 0.34),
                (right - hair_w * 0.10, top + lift),
                (right, top + hair_h * 0.48),
                (right, bottom),
            ],
            fill=rgba,
        )
    elif silhouette in {"fringe", "crop", "curtain"}:
        draw.rounded_rectangle(
            (left, top + hair_h * 0.18, right, bottom), radius=max(8, int(hair_w * 0.12)), fill=rgba
        )
        teeth = 7 if silhouette != "curtain" else 4
        for index in range(teeth):
            x = left + hair_w * (index + 0.25) / teeth
            drop = hair_h * (0.20 + 0.08 * (index % 2))
            if silhouette == "curtain" and index in {1, 2}:
                continue
            draw.polygon(
                [
                    (x, bottom - 3),
                    (x + hair_w / teeth * 0.8, bottom - 3),
                    (x + hair_w / teeth * 0.4, bottom + drop),
                ],
                fill=rgba,
            )
    elif silhouette in {"afro", "long_layers"}:
        radius = hair_w * (0.17 if silhouette == "afro" else 0.13)
        count = 8 if silhouette == "afro" else 6
        for index in range(count):
            cx = left + hair_w * (index + 0.5) / count
            cy = top + hair_h * (0.45 + 0.12 * (index % 2))
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=rgba)
        draw.rectangle((left, top + hair_h * 0.48, right, bottom + hair_h * 0.35), fill=rgba)
    else:
        draw.rounded_rectangle(
            (left, top + hair_h * 0.20, right, bottom), radius=max(8, int(hair_w * 0.14)), fill=rgba
        )

    # A subtle highlight makes the deliberately simple overlay easier to read.
    draw.arc(
        (left + hair_w * 0.12, top + hair_h * 0.20, right - hair_w * 0.12, bottom),
        190,
        330,
        fill=accent,
        width=max(2, int(hair_w * 0.012)),
    )
    return Image.alpha_composite(base, overlay).convert("RGB")


def _height_factor(silhouette: str) -> float:
    return {
        "buzz": 0.20,
        "crew": 0.27,
        "crop": 0.30,
        "fringe": 0.34,
        "curtain": 0.40,
        "quiff": 0.40,
        "pompadour": 0.48,
        "afro": 0.52,
        "long_layers": 0.48,
    }.get(silhouette, 0.34)


def _parse_color(value: str, alpha: int) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    if len(value) != 6:
        raise ValueError("Color must be a six-digit hex string")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16), max(0, min(255, alpha))
