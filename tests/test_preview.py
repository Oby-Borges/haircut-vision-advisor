import pytest

pytest.importorskip("PIL")

from haircut_vision.catalog import load_catalog
from haircut_vision.demo_fixture import demo_portrait, synthetic_landmarks
from haircut_vision.preview import render_preview


def test_preview_preserves_dimensions_and_changes_pixels():
    image = demo_portrait((320, 320))
    preview = render_preview(image, synthetic_landmarks(), load_catalog()[2])
    assert preview.size == image.size
    assert preview.mode == "RGB"
    assert preview.tobytes() != image.tobytes()


def test_preview_rejects_bad_color():
    with pytest.raises(ValueError, match="six-digit"):
        render_preview(demo_portrait(), synthetic_landmarks(), load_catalog()[0], color="#fff")
