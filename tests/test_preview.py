import pytest

pytest.importorskip("PIL")

from haircut_vision.catalog import load_catalog
from haircut_vision.demo_fixture import demo_portrait, synthetic_landmarks
from haircut_vision.preview import render_preview
from haircut_vision.vision import decode_image_bytes


def test_preview_preserves_dimensions_and_changes_pixels():
    image = demo_portrait((320, 320))
    preview = render_preview(image, synthetic_landmarks(), load_catalog()[2])
    assert preview.size == image.size
    assert preview.mode == "RGB"
    assert preview.tobytes() != image.tobytes()


def test_preview_rejects_bad_color():
    with pytest.raises(ValueError, match="six-digit"):
        render_preview(demo_portrait(), synthetic_landmarks(), load_catalog()[0], color="#fff")


def test_opencv_decodes_uploaded_image_bytes():
    import io

    source = demo_portrait((96, 64))
    encoded = io.BytesIO()
    source.save(encoded, format="PNG")
    decoded = decode_image_bytes(encoded.getvalue())
    assert decoded.size == source.size
    assert decoded.mode == "RGB"
