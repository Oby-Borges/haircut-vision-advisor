"""Local AI-generated catalog references, separate from personal previews."""

from pathlib import Path

IMAGE_DIRECTORY = Path(__file__).resolve().parents[2] / "assets" / "hairstyle_images"


def style_image_path(style_id: str, directory: Path = IMAGE_DIRECTORY) -> Path | None:
    if not style_id or any(c not in "abcdefghijklmnopqrstuvwxyz0123456789_" for c in style_id):
        raise ValueError("Invalid style image ID")
    path = directory / f"{style_id}.jpg"
    return path if path.is_file() else None
