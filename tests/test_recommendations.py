from haircut_vision.catalog import load_catalog
from haircut_vision.demo_fixture import synthetic_landmarks
from haircut_vision.face_shape import classify_face_shape
from haircut_vision.measurements import extract_measurements
from haircut_vision.recommend import rank_hairstyles
from haircut_vision.types import Preferences


def _oval_result():
    return classify_face_shape(extract_measurements(synthetic_landmarks()))


def test_exact_preferences_raise_matching_style():
    preferences = Preferences(
        desired_length="very_short",
        maintenance="low",
        fade="no",
        texture="straight",
        category="classic",
    )
    ranked = rank_hairstyles(load_catalog(), _oval_result(), preferences)
    assert ranked[0].style.id == "classic_buzz"
    assert ranked[0].score <= 100
    assert "length" in ranked[0].breakdown
    assert any("Matches" in reason for reason in ranked[0].reasons)


def test_ranking_is_deterministic_and_descending():
    preferences = Preferences(texture="coily", category="natural")
    first = rank_hairstyles(load_catalog(), _oval_result(), preferences)
    second = rank_hairstyles(load_catalog(), _oval_result(), preferences)
    assert [item.style.id for item in first] == [item.style.id for item in second]
    assert [item.score for item in first] == sorted([item.score for item in first], reverse=True)
