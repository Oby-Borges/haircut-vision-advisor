from copy import deepcopy

import pytest

from haircut_vision.catalog import load_catalog
from haircut_vision.handoff import validate_handoff
from haircut_vision.scan import assess_capture, demo_view, load_capture
from haircut_vision.session import (
    VIEWS,
    approve_plan,
    create_plan,
    export_handoff,
    new_session,
    save_capture,
    scan_status,
    update_preferences,
)


def complete_session():
    session = new_session()
    for view in VIEWS:
        capture = assess_capture(demo_view(view), view, synthetic=True)
        capture["reviewed"] = True
        save_capture(session, view, capture)
    update_preferences(
        session,
        {
            "no_cut_regions": ["ears"],
            "cut_top": False,
            "top_length_mm": 50,
            "base_length_mm": 9,
            "fade_height": "none",
        },
    )
    return session


def test_four_distinct_reviewed_views_required():
    session = complete_session()
    assert scan_status(session)["scan_complete"]
    assert not scan_status(session)["head_frame_ready"]
    assert scan_status(session)["confidence"] is None
    del session["captures"]["rear"]
    assert not scan_status(session)["scan_complete"]
    with pytest.raises(ValueError, match="Complete"):
        create_plan(session, load_catalog()[0], {})


def test_duplicate_view_rejected():
    session = complete_session()
    with pytest.raises(ValueError, match="already assigned"):
        save_capture(session, "rear", deepcopy(session["captures"]["front"]))


def test_synthetic_and_real_photos_cannot_mix():
    session = complete_session()
    capture = deepcopy(session["captures"]["rear"])
    capture["synthetic"] = False
    with pytest.raises(ValueError, match="fresh session"):
        save_capture(session, "rear", capture)


def test_handoff_schema_and_cross_record_invariants():
    from jsonschema import ValidationError

    session = complete_session()
    plan = create_plan(session, load_catalog()[0], {})
    approve_plan(session, plan["plan_id"])
    output = export_handoff(session)
    validate_handoff(output)
    wrong_id = deepcopy(output)
    wrong_id["preview"]["plan_id"] = "stale-plan"
    with pytest.raises(ValueError, match="same plan ID"):
        validate_handoff(wrong_id)
    unsafe = deepcopy(output)
    unsafe["planning"]["executable"] = True
    with pytest.raises(ValidationError):
        validate_handoff(unsafe)
    wrong_top = deepcopy(output)
    wrong_top["proposal"]["top_length_mm"] = 0
    with pytest.raises(ValueError, match="Keep-top"):
        validate_handoff(wrong_top)
    wrong_length = deepcopy(output)
    wrong_length["proposal"]["side_length_mm"] = -10
    with pytest.raises(ValidationError):
        validate_handoff(wrong_length)


def test_approval_bound_to_scan_preferences_style_and_preview():
    session = complete_session()
    style = load_catalog()[0]
    plan = create_plan(session, style, {"scale": 1.0})
    with pytest.raises(ValueError, match="Approve"):
        export_handoff(session)
    approve_plan(session, plan["plan_id"])
    output = export_handoff(session)
    assert output["plan_id"] == output["preview"]["plan_id"] == output["planning"]["plan_id"]
    assert output["proposal"]["top_length_mm"] is None
    assert not output["planning"]["executable"]
    assert create_plan(session, style, {"scale": 1.0})["approved"]
    new_plan = create_plan(session, style, {"scale": 1.1})
    assert new_plan["plan_id"] != plan["plan_id"]
    assert session["approval"] is None
    with pytest.raises(ValueError, match="changed"):
        approve_plan(session, plan["plan_id"])
    approve_plan(session, new_plan["plan_id"])
    update_preferences(session, {**session["preferences"], "base_length_mm": 12})
    assert session["plan"] is None and session["approval"] is None


def test_retake_invalidates_plan():
    session = complete_session()
    plan = create_plan(session, load_catalog()[0], {})
    approve_plan(session, plan["plan_id"])
    capture = deepcopy(session["captures"]["rear"])
    capture["digest"] = "new-photo"
    save_capture(session, "rear", capture)
    assert session["plan"] is None and session["approval"] is None


def test_bad_image_and_poor_quality_rejected():
    from PIL import Image

    with pytest.raises(ValueError, match="photo"):
        load_capture(b"invalid image")
    assert assess_capture(Image.new("RGB", (600, 600)), "rear")["issues"]


def test_rectangular_image_measurements_use_pixel_geometry(monkeypatch):
    from PIL import Image

    from haircut_vision.demo_fixture import synthetic_landmarks

    # Same physical face rendered in a 2:1 image; x is normalized by double width.
    points = [(x / 2, y, z) for x, y, z in synthetic_landmarks()]
    monkeypatch.setattr("haircut_vision.scan.detect_landmarks", lambda image: points)
    import numpy as np

    image = Image.fromarray(
        np.random.default_rng(42).integers(40, 210, (600, 1200, 3), dtype=np.uint8)
    )
    result = assess_capture(image, "front")
    assert result["measurements"].length_to_width == pytest.approx(1.36)
