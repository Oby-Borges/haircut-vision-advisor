import pytest

from haircut_vision.demo_fixture import synthetic_landmarks
from haircut_vision.measurements import extract_measurements


def test_extracts_normalized_ratios():
    measurements = extract_measurements(
        synthetic_landmarks(aspect=1.42, forehead_ratio=0.91, jaw_ratio=0.84)
    )
    assert measurements.length_to_width == pytest.approx(1.42)
    assert measurements.forehead_to_cheek == pytest.approx(0.91)
    assert measurements.jaw_to_cheek == pytest.approx(0.84)
    assert measurements.yaw_asymmetry == pytest.approx(0.0)


def test_rejects_incomplete_landmarks():
    with pytest.raises(ValueError, match="Expected at least"):
        extract_measurements([(0.0, 0.0, 0.0)] * 20)


def test_yaw_asymmetry_flags_off_center_nose():
    landmarks = synthetic_landmarks()
    landmarks[1] = (0.62, 0.49, 0.0)
    assert extract_measurements(landmarks).yaw_asymmetry > 0.14
