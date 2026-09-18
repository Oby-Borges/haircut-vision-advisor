import pytest

from haircut_vision.demo_fixture import synthetic_landmarks
from haircut_vision.face_shape import classify_face_shape
from haircut_vision.measurements import extract_measurements


@pytest.mark.parametrize(
    ("expected", "aspect", "forehead", "jaw"),
    [
        ("round", 1.08, 0.90, 0.90),
        ("square", 1.18, 0.91, 0.96),
        ("oblong", 1.68, 0.90, 0.86),
        ("heart", 1.30, 1.00, 0.70),
        ("diamond", 1.35, 0.72, 0.72),
        ("oval", 1.36, 0.88, 0.82),
    ],
)
def test_classifies_canonical_geometry(expected, aspect, forehead, jaw):
    measurements = extract_measurements(
        synthetic_landmarks(aspect=aspect, forehead_ratio=forehead, jaw_ratio=jaw)
    )
    result = classify_face_shape(measurements)
    assert result.label == expected
    assert 0 <= result.confidence <= 1
    assert len(result.scores) == 6
    assert result.reasons
