from haircut_vision.catalog import load_catalog
from haircut_vision.types import FACE_SHAPES


def test_catalog_has_at_least_fifteen_unique_styles():
    styles = load_catalog()
    assert len(styles) >= 15
    assert len({style.id for style in styles}) == len(styles)


def test_catalog_represents_all_face_shapes_and_textures():
    styles = load_catalog()
    represented_shapes = {shape for style in styles for shape in style.face_shapes}
    represented_textures = {texture for style in styles for texture in style.textures}
    assert set(FACE_SHAPES) <= represented_shapes
    assert {"straight", "wavy", "curly", "coily"} <= represented_textures
