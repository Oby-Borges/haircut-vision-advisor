import json
from pathlib import Path

import pytest
from PIL import Image

from haircut_vision.catalog import load_catalog
from haircut_vision.style_images import style_image_path

ROOT = Path(__file__).resolve().parents[1]


def test_every_catalog_style_has_valid_generated_image_and_prompt():
    prompts = json.loads(
        (ROOT / "assets" / "hairstyle_image_prompts.json").read_text(encoding="utf-8")
    )
    catalog = load_catalog()
    assert set(prompts["styles"]) == {style.id for style in catalog}
    assert prompts["model_label"] == "Nano Banana 2"
    for style in catalog:
        path = style_image_path(style.id)
        assert path is not None, f"Missing image for {style.id}"
        with Image.open(path) as image:
            assert image.format == "JPEG"
            assert min(image.size) >= 512
            assert image.width == image.height
            image.verify()


def test_missing_image_is_a_safe_fallback(tmp_path):
    assert style_image_path("new_style", tmp_path) is None


@pytest.mark.parametrize("value", ["../secrets", "C:/file", "", "style.png"])
def test_image_id_rejects_non_catalog_paths(value):
    with pytest.raises(ValueError):
        style_image_path(value)
