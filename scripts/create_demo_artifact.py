"""Generate the original, license-safe README demo graphic."""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from haircut_vision.catalog import load_catalog  # noqa: E402
from haircut_vision.demo_fixture import demo_portrait, synthetic_landmarks  # noqa: E402
from haircut_vision.face_shape import classify_face_shape  # noqa: E402
from haircut_vision.measurements import extract_measurements  # noqa: E402
from haircut_vision.preview import render_preview  # noqa: E402
from haircut_vision.recommend import rank_hairstyles  # noqa: E402
from haircut_vision.types import Preferences  # noqa: E402


def font(size: int, bold: bool = False):
    names = [
        "arialbd.ttf" if bold else "arial.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
    ]
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main() -> None:
    canvas = Image.new("RGB", (1400, 820), "#f6f2ea")
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((40, 36, 1360, 154), radius=28, fill="#203442")
    draw.text((76, 60), "HAIRCUT VISION ADVISOR", fill="#eebd70", font=font(22, True))
    draw.text(
        (76, 92),
        "Explainable style guidance · no cutting controls",
        fill="white",
        font=font(34, True),
    )

    portrait = demo_portrait((520, 520))
    landmarks = synthetic_landmarks()
    measurements = extract_measurements(landmarks)
    shape = classify_face_shape(measurements)
    recommendations = rank_hairstyles(load_catalog(), shape, Preferences())
    selected = recommendations[0]
    preview = render_preview(portrait, landmarks, selected.style)

    canvas.paste(portrait.resize((430, 430)), (60, 220))
    canvas.paste(preview.resize((430, 430)), (510, 220))
    draw.text((60, 668), "Original synthetic fixture", fill="#52626c", font=font(20))
    draw.text((510, 668), f"Preview: {selected.style.name}", fill="#52626c", font=font(20))

    draw.rounded_rectangle((980, 220, 1340, 720), radius=24, fill="#ffffff")
    draw.text((1014, 250), "EXPLAINABLE RESULT", fill="#b06d1e", font=font(17, True))
    draw.text((1014, 290), shape.label.title(), fill="#203442", font=font(46, True))
    draw.text(
        (1014, 355),
        f"Length / width   {measurements.length_to_width:.2f}",
        fill="#344955",
        font=font(20),
    )
    draw.text(
        (1014, 392),
        f"Forehead / cheek {measurements.forehead_to_cheek:.2f}",
        fill="#344955",
        font=font(20),
    )
    draw.text(
        (1014, 429),
        f"Jaw / cheek      {measurements.jaw_to_cheek:.2f}",
        fill="#344955",
        font=font(20),
    )
    draw.line((1014, 478, 1306, 478), fill="#d9e0e3", width=2)
    draw.text((1014, 506), "Top suggestions", fill="#203442", font=font(22, True))
    for index, recommendation in enumerate(recommendations[:3], 1):
        draw.text(
            (1014, 548 + 42 * (index - 1)),
            f"{index}. {recommendation.style.name}  {recommendation.score:.0f}",
            fill="#344955",
            font=font(19),
        )
    draw.text((1014, 675), "Stylistic suggestions only", fill="#a15b19", font=font(17, True))

    destination = ROOT / "docs" / "demo-preview.png"
    canvas.save(destination, optimize=True)
    print(f"Wrote {destination}")


if __name__ == "__main__":
    main()
