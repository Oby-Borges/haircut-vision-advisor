"""Load and validate the configurable hairstyle catalog."""

from __future__ import annotations

import json
from pathlib import Path

from .types import FACE_SHAPES, Hairstyle

DEFAULT_CATALOG_PATH = Path(__file__).resolve().parents[2] / "assets" / "hairstyles.json"


def load_catalog(path: str | Path = DEFAULT_CATALOG_PATH) -> list[Hairstyle]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    styles = [Hairstyle.from_dict(item) for item in raw]
    validate_catalog(styles)
    return styles


def validate_catalog(styles: list[Hairstyle]) -> None:
    if len(styles) < 10:
        raise ValueError("Catalog must contain at least 10 styles")
    ids = [style.id for style in styles]
    if len(ids) != len(set(ids)):
        raise ValueError("Catalog style IDs must be unique")
    for style in styles:
        if not style.face_shapes or not set(style.face_shapes).issubset(FACE_SHAPES):
            raise ValueError(f"Invalid face shape compatibility for {style.id}")
        params = style.robot_parameters
        for required in ("top_length_mm", "side_length_mm", "back_length_mm", "fade_type"):
            if required not in params:
                raise ValueError(f"{style.id} is missing robot parameter {required}")
